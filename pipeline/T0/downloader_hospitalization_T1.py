from ImpararePackage import dataRequest
import pandas as pd
import time

# Tabela separada para rodar lado a lado com o downloader_vital_signs e comparar os dois
TABELA_DESTINO = "hospitalization"
TABELA_ORIGEM = "hospitalization"

COLUNAS_DOWNLOAD = {
    "record_id": "integer",
    "created_at": "date",
    "attendance_id": "integer",
    "attendance_date": "timestamp",
    "health_insurance_name": "text",
    "unity_code_and_description": "text",
    "hospitalization_type": "text",
    "hospital_discharge_date": "timestamp",
    "hospital_discharge_description": "text",
    "id_hospital": "SMALLINT"
}

def main():
    print(f"Iniciando downloader_{TABELA_DESTINO}")
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
        print(f"Erro na busca da ultima data de atendimentos em {TABELA_DESTINO}, baixando tudo novamente")

    sql_antes = None
    if last_date is not None and pd.notna(last_date):
        query_downloader += f" WHERE date(created_at) > '{last_date}'"
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

    print(f"Baixado no total: {leitor.linhas} linhas em {TABELA_DESTINO} em {time.perf_counter() - inicio:.1f}s - downloader_{TABELA_DESTINO}")

if __name__ == "__main__":
    main()