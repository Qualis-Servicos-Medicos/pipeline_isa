from ImpararePackage import dataRequest
import pandas as pd
import time

TABELA_DESTINO = "prescriptions_V2"
TABELA_ORIGEM = "prescriptions"

COLUNAS_DOWNLOAD = {
    "record_id": "integer",
    "created_at": "date",
    "prescription_date": "timestamp",
    "antibiotic": "text",
    "dosage": "float",
    "antibiotic_unity": "text",
    "frequency": "text",
    "via": "text",
    "id_hospital": "SMALLINT"
}

def main():
    print(f"Iniciando downloader_{TABELA_ORIGEM}")
    inicio = time.perf_counter()
    query_downloader = f"""
        SELECT
            {', '.join([f'{k}::{v}' for k, v in COLUNAS_DOWNLOAD.items()])}
        FROM {TABELA_ORIGEM}
    """

    last_date = None
    try:
        df = dataRequest.get_data(queryText= f"SELECT max(created_at) AS created_at FROM {TABELA_DESTINO}", chunck= None)
        last_date = df.iloc[0]["created_at"]
    except Exception:
        print(f"Erro na busca da ultima data de sinais vitais em {TABELA_DESTINO}, baixando tudo novamente")

    sql_antes = None
    if last_date is not None and pd.notna(last_date):
        query_downloader += f" AND date(created_at) > '{last_date}'"
        print(f"Buscando todos os dados novos desde: {last_date} (exclusive)")
        create_index_wellhead = f"""CREATE INDEX IF NOT EXISTS idx_{TABELA_ORIGEM}_created_at_record_id ON {TABELA_ORIGEM} ((created_at::date), record_id);"""
        dataRequest.execute(create_index_wellhead, isWellheadEngine= True)
    else:
        sql_antes = f"""
            DROP TABLE IF EXISTS {TABELA_DESTINO};
            CREATE UNLOGGED TABLE {TABELA_DESTINO} (
                {', '.join([f'{k} {v}' for k, v in COLUNAS_DOWNLOAD.items()])}
            );
        """

    sql_depois = f"""CREATE INDEX IF NOT EXISTS idx_{TABELA_DESTINO}_created_at_record_id ON {TABELA_DESTINO} (created_at, record_id);"""

    leitor = dataRequest.copy_from_wellhead_to_local_with_stream(query_downloader, TABELA_DESTINO, sql_antes, sql_depois)

    print(f"Baixado no total: {leitor.linhas} linhas em {TABELA_DESTINO} em {time.perf_counter() - inicio:.1f}s - downloader_vital_signs")

if __name__ == "__main__":
    main()
