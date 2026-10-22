from ImpararePackage import dataRequest
import pandas as pd
import os
import threading
import time

# Tabela separada para rodar lado a lado com o downloader_vital_signs e comparar os dois
TABELA_DESTINO = "vital_signs_v2"
BLOCO = 1 << 20  # 1 MB por leitura/escrita no pipe entre os dois COPY

COLUNAS_DOWNLOAD = {
    "record_id": "integer",
    "created_at": "date",
    "acronym": "text",
    "collection_date": "timestamp",
    "value": "float8",
    "measurement_unity": "text",
    "provider_profile": "text",
    "attendance_type": "text",
    "id_hospital": "integer"
}


class LeitorComProgresso:
    """Repassa o stream do COPY TO (wellhead) para o COPY FROM (local) contando linhas e bytes."""

    def __init__(self, arquivo, intervalo_log: float = 5.0):
        self.arquivo = arquivo
        self.intervalo_log = intervalo_log
        self.linhas = 0
        self.bytes = 0
        self.inicio = time.perf_counter()
        self.ultimo_log = self.inicio
        self.primeiro_byte = None

    def read(self, size: int = -1) -> bytes:
        dados = self.arquivo.read(size)
        agora = time.perf_counter()
        if dados and self.primeiro_byte is None:
            self.primeiro_byte = agora - self.inicio
            print(f"Primeiro byte recebido após {self.primeiro_byte:.1f}s")
        # no formato texto do COPY as quebras de linha dentro dos valores vêm escapadas, então cada \n é uma linha
        self.linhas += dados.count(b"\n")
        self.bytes += len(dados)
        if agora - self.ultimo_log >= self.intervalo_log:
            self.ultimo_log = agora
            print(self.resumo())
        return dados

    def resumo(self) -> str:
        decorrido = time.perf_counter() - self.inicio
        mb = self.bytes / 1e6
        return f"{self.linhas:,} linhas | {mb:,.1f} MB | {decorrido:.1f}s | {mb / decorrido:.1f} MB/s | {self.linhas / decorrido:,.0f} linhas/s"

    def close(self):
        self.arquivo.close()


def copy_stream(query_origem: str, tabela_destino: str, sql_antes: str, sql_depois: str) -> LeitorComProgresso:
    """
    Liga COPY (query_origem) TO STDOUT no wellhead direto em COPY tabela_destino FROM STDIN no banco local
    através de um pipe, sem passar por pandas. sql_antes, o COPY e sql_depois rodam numa única transação
    no destino: se qualquer parte falhar, a tabela local fica exatamente como estava.
    """
    conn = dataRequest.LOCALDATABSE.raw_connection()
    r_fd, w_fd = os.pipe()
    erros = []

    def produtor():
        try:
            with os.fdopen(w_fd, "wb", buffering= BLOCO) as escrita:
                conn_origem = dataRequest.ENGINEWELLHEAD.raw_connection()
                try:
                    with conn_origem.cursor() as cur:
                        # garante datas em ISO no texto do COPY, independente da configuração do servidor de origem
                        cur.execute("SET LOCAL datestyle TO ISO")
                        cur.copy_expert(f"COPY ({query_origem}) TO STDOUT", escrita)
                finally:
                    conn_origem.close()
        except BaseException as e:
            erros.append(e)

    thread = threading.Thread(target= produtor, daemon= True)
    thread.start()
    leitor = LeitorComProgresso(os.fdopen(r_fd, "rb", buffering= BLOCO))
    try:
        with conn.cursor() as cur:
            cur.execute(sql_antes)
            cur.copy_expert(f"COPY {tabela_destino} FROM STDIN", leitor, size= BLOCO)
            # o EOF também chega quando o produtor falha no meio, então só confirma depois de checar o erro dele
            thread.join()
            if erros:
                raise erros[0]
            print(f"Transferência concluída: {leitor.resumo()}")
            cur.execute(sql_depois)
        conn.commit()
    finally:
        # sem commit o close faz rollback
        leitor.close()
        conn.close()
    return leitor


def main():
    print("Iniciando downloader_vital_signs_v2")
    inicio = time.perf_counter()
    query_downloader = f"""
        SELECT DISTINCT
            {', '.join([f'{k}::{v}' for k, v in COLUNAS_DOWNLOAD.items()])}
        FROM vital_signs
        WHERE value IS NOT NULL
            AND collection_date IS NOT NULL
    """

    last_date = None
    try:
        df = dataRequest.get_data(queryText= f"SELECT max(created_at) AS created_at FROM {TABELA_DESTINO}", chunck= None)
        last_date = df.iloc[0]["created_at"]
    except Exception:
        print(f"Erro na busca da ultima data de sinais vitais em {TABELA_DESTINO}, baixando tudo novamente")

    if last_date is not None and pd.notna(last_date):
        # o dia de last_date pode ter sido baixado só em parte na execução anterior,
        # então ele é apagado e baixado de novo junto com os dias seguintes
        query_downloader += f" AND date(created_at) >= '{last_date}'"
        sql_antes = f"DELETE FROM {TABELA_DESTINO} WHERE created_at >= '{last_date}'"
        print(f"Buscando todos os dados novos desde: {last_date} (inclusive)")
    else:
        sql_antes = f"""
            DROP TABLE IF EXISTS {TABELA_DESTINO};
            CREATE UNLOGGED TABLE {TABELA_DESTINO} (
                {', '.join([f'{k} {v}' for k, v in COLUNAS_DOWNLOAD.items()])}
            );
        """

    create_index_wellhead = """CREATE INDEX IF NOT EXISTS idx_vital_signs_created_at_record_id ON vital_signs (id_hospital, (created_at::date), record_id);"""
    dataRequest.execute(create_index_wellhead, isWellheadEngine= True)
    # índice criado depois da carga: numa carga completa é bem mais rápido que manter o índice durante o COPY
    sql_depois = f"""CREATE INDEX IF NOT EXISTS idx_{TABELA_DESTINO}_created_at_record_id ON {TABELA_DESTINO} (created_at, record_id);"""

    leitor = copy_stream(query_downloader, TABELA_DESTINO, sql_antes, sql_depois)

    print(f"Baixado no total: {leitor.linhas} linhas em {TABELA_DESTINO} em {time.perf_counter() - inicio:.1f}s - downloader_vital_signs_v2")


if __name__ == "__main__":
    main()
