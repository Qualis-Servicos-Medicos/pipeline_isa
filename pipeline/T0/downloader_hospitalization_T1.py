from ImpararePackage import dataRequest
from ImpararePackage import maestro
import pandas as pd
from multiprocessing import Pool, cpu_count

def worker_uploader(c: pd.DataFrame) -> int:
    dataRequest.set_data_on_sql(df= c, nomeTabelaDestino= "hospitalization", if_exists= "append")
    return len(c)

def main():
    print("Inicinado downloader_hospitalization")
    colunas_download = {
        "record_id": "integer",
        "created_at": "date",
        "attendance_id": "integer",
        "attendance_date": "timestamp",
        "health_insurance_name": "text",
        "unity_code_and_description": "text",
        "hospitalization_type": "text",
        "hospital_discharge_date": "timestamp",
        "hospital_discharge_description": "text",
        "id_hospital": "integer"
    }
    query_dowloader = f"""
        select 
            {', '.join([f'{k}::{v}' for k, v in colunas_download.items()])} 
        FROM hospitalization
    """

    replace = True
    try:
        query_last_dowloaded_date = """
            SELECT 
                created_at 
            FROM hospitalization
            ORDER BY created_at DESC
            LIMIT 1
        """
        df = dataRequest.get_data(queryText= query_last_dowloaded_date, chunck= None)

        last_date = df.iloc[0]["created_at"]
        if last_date is not None and not pd.isna(last_date):
            query_dowloader += f" WHERE date(created_at) > '{last_date}'"
            print(f"Buscando todos os dados novos desde: {last_date}")
            replace = False
    except:
        print(f"Erro na busca da ultima data, baixando tudo novamente")

    if replace:
        replace_query = f"""
            DROP TABLE IF EXISTS hospitalization;
            CREATE UNLOGGED TABLE hospitalization (
                {', '.join([f'{k} {v}' for k, v in colunas_download.items()])}
            );
        """
        dataRequest.execute(replace_query)

    create_index_wellhead = """CREATE INDEX IF NOT EXISTS idx_hospitalization_created_at_record_id ON hospitalization (id_hospital, (created_at::date), record_id);"""
    dataRequest.execute(create_index_wellhead, isWellheadEngine= True)
    create_index_local = """CREATE INDEX IF NOT EXISTS idx_hospitalization_created_at_record_id ON hospitalization (created_at, record_id);"""
    dataRequest.execute(create_index_local)

    df = dataRequest.get_data(queryText= query_dowloader, chunck= 100000, isWellheadEngine=True)
    count = 0
    with Pool(4) as pool:
        for result in pool.imap_unordered(worker_uploader, df):
            count += result

    print(f"Baixado no total: {count} linhas em hospitalization - downloader_hospitalization")
    
if __name__ == "__main__":
    main()