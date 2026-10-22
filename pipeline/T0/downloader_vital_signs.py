from ImpararePackage import dataRequest
import pandas as pd
import time

# Tabela separada para rodar lado a lado com o downloader_vital_signs e comparar os dois
TABELA_DESTINO = "vital_signs"

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

def main():
    print("Iniciando downloader_vital_signs_v2")
    inicio = time.perf_counter()
    query_downloader = f"""
        SELECT
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

    leitor = dataRequest.copy_from_wellhead_to_local_with_stream(query_downloader, TABELA_DESTINO, sql_antes, sql_depois)

    print(f"Baixado no total: {leitor.linhas} linhas em {TABELA_DESTINO} em {time.perf_counter() - inicio:.1f}s - downloader_vital_signs_v2")

if __name__ == "__main__":
    main()
