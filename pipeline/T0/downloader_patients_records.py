from ImpararePackage import dataRequest
from ImpararePackage import maestro
import pandas as pd
from multiprocessing import Pool, cpu_count

def worker_uploader(c: pd.DataFrame) -> int:
    dataRequest.set_data_on_sql(df= c, nomeTabelaDestino= "patients_records", if_exists= "append")
    return len(c)

def main():
    print("Inicinado downloader_patients_records")
    colunas_download = {
        "record_id": "integer",
        "patient_name": "text",
        "birthdate": "date",
        "sex": "text",
        "created_at": "date",
        "id_hospital": "integer"
    }
    query_downloader = f"""
        SELECT 
             {', '.join([f'{k}::{v}' for k, v in colunas_download.items()])}
        FROM patients_records
    """

    replace = True
    try:
        query_last_dowloaded_date = """
            SELECT 
                created_at 
            FROM patients_records
            ORDER BY created_at DESC
            LIMIT 1
        """
        df = dataRequest.get_data(queryText= query_last_dowloaded_date, chunck= None)

        last_date = df.iloc[0]["created_at"]
        if last_date is not None and not pd.isna(last_date):
            query_downloader += f" WHERE date(created_at) > '{last_date}'"
            print(f"Buscando todos os dados novos desde: {last_date}")
            replace = False
    except:
        print(f"Erro na busca da ultima data, baixando tudo novamente")

    if replace:
        replace_query = f"""
            DROP TABLE IF EXISTS patients_records;
            CREATE UNLOGGED TABLE patients_records (
                {', '.join([f'{k} {v}' for k, v in colunas_download.items()])}
            );
        """
        dataRequest.execute(replace_query)

    create_index_wellhead = """CREATE INDEX IF NOT EXISTS idx_patients_records_created_at_record_id ON patients_records (id_hospital, (created_at::date), record_id);"""
    dataRequest.execute(create_index_wellhead, isWellheadEngine= True)
    create_index_local = """CREATE INDEX IF NOT EXISTS idx_patients_records_created_at_record_id ON patients_records (created_at, record_id);"""
    dataRequest.execute(create_index_local)

    df = dataRequest.get_data(queryText= query_downloader, chunck= 100000, isWellheadEngine=True)
    count = 0
    with Pool(4) as pool:
        for result in pool.imap_unordered(worker_uploader, df):
            count += result

    print(f"Baixado no total: {count} linhas em patients_records - downloader_patients_records")
    
if __name__ == "__main__":
    main()

from ImpararePackage import dataRequest
import pandas as pd
import time

# Tabela separada para rodar lado a lado com o downloader_vital_signs e comparar os dois
TABELA_DESTINO = "vital_signs"
TABELA_ORIGEM = "vital_signs"

COLUNAS_DOWNLOAD = {
    "record_id": "integer",
    "created_at": "date",
    "acronym": "text",
    "collection_date": "timestamp",
    "value": "float8",
    "measurement_unity": "text",
    "provider_profile": "text",
    "attendance_type": "text",
    "id_hospital": "SMALLINT"
}

def main():
    print(f"Iniciando downloader_{TABELA_ORIGEM}")
    inicio = time.perf_counter()
    query_downloader = f"""
        SELECT
            {', '.join([f'{k}::{v}' for k, v in COLUNAS_DOWNLOAD.items()])}
        FROM {TABELA_ORIGEM}
        WHERE value IS NOT NULL
            AND collection_date IS NOT NULL
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
