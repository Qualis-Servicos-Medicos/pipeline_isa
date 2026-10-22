from ImpararePackage import dataRequest
from ImpararePackage import maestro
import pandas as pd
from multiprocessing import Pool, cpu_count

def worker_uploader(c: pd.DataFrame) -> int:
    dataRequest.set_data_on_sql(df= c, nomeTabelaDestino= "vital_signs", if_exists= "append")
    return len(c)

def main():  
    print("Inicinado downloader_vital_signs")
    colunas_download = {
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
    query_downloader = f"""
        SELECT DISTINCT
            {', '.join([f'{k}::{v}' for k, v in colunas_download.items()])}
        FROM vital_signs
        WHERE value IS NOT NULL
            AND collection_date IS NOT NULL
    """
    
    replace = True
    try:
        query_last_dowloaded_date = """
            SELECT 
                created_at 
            FROM vital_signs
            ORDER BY created_at DESC
            LIMIT 1
        """
        df = dataRequest.get_data(queryText= query_last_dowloaded_date, chunck= None)

        last_date = df.iloc[0]["created_at"]
        if last_date is not None and not pd.isna(last_date):
            query_downloader += f" AND date(created_at) > '{last_date}'"
            print(f"Buscando todos os dados novos desde: {last_date}")
            replace = False
    except:
        print(f"Erro na busca da ultima data de sinais vitais, baixando tudo novamente")

    if replace:
        replace_query = f"""
            DROP TABLE IF EXISTS vital_signs;
            CREATE UNLOGGED TABLE vital_signs (
                {', '.join([f'{k} {v}' for k, v in colunas_download.items()])}
            );
        """
        dataRequest.execute(replace_query)

    create_index_wellhead = """CREATE INDEX IF NOT EXISTS idx_vital_signs_created_at_record_id ON vital_signs (id_hospital, (created_at::date), record_id);"""
    dataRequest.execute(create_index_wellhead, isWellheadEngine= True)
    create_index_local = """CREATE INDEX IF NOT EXISTS idx_vital_signs_created_at_record_id ON vital_signs (created_at, record_id);"""
    dataRequest.execute(create_index_local)
    
    df = dataRequest.get_data(queryText= query_downloader, chunck= 100000, isWellheadEngine=True)
    count = 0
    with Pool(4) as pool:
        for result in pool.imap_unordered(worker_uploader, df):
            count += result
    
    print(f"Baixado no total: {count} linhas em vital_signs - downloader_vital_signs")

    
if __name__ == "__main__":
    main()


