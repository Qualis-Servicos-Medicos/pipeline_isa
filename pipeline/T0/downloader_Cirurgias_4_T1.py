from ImpararePackage import dataRequest
from ImpararePackage  import maestro
import pandas as pd
from multiprocessing import Pool, cpu_count

def worker_uploader(c: pd.DataFrame) -> int:
    dataRequest.set_data_on_sql(df= c, nomeTabelaDestino= "surgeries_rgo", if_exists= "append")
    return len(c)

def main():
    print("Inciando downloader Cirurgias 4")
    colunas_download = {
        "created_at": ("surgeries_rgo.created_at", "date"),
        "record_id": ("surgeries_rgo.record_id", "integer"), 
        "attendance_id": ("surgeries_rgo.attendance_id", "integer"), 
        "attendance_type": ("surgeries_rgo.attendance_type", "text"),
        "provider_name": ("surgeries_rgo.provider_name", "text"),
        "creation_date": ("surgeries_rgo.creation_date", "timestamp"),
        "close_date": ("surgeries_rgo.close_date", "timestamp"),
        "surgery_description": ("surgeries_rgo.surgery_description", "text"),
        "id_hospital": ("surgeries_rgo.id_hospital","integer"),
    }

    colunas_destino = {k: v[1] for k, v in colunas_download.items()}
    select_fields = [f"{v[0]}::{v[1]} AS {k}" for k, v in colunas_download.items()]
    
    query_dowloader = f"""
        select 
            {', '.join(select_fields)} 
        FROM surgeries_rgo
    """
    replace = True
    try:
        query_last_dowloaded_date = """
            SELECT 
                created_at 
            FROM surgeries_rgo
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
            DROP TABLE IF EXISTS surgeries_rgo;
            CREATE UNLOGGED TABLE surgeries_rgo (
                {', '.join([f'{k} {v}' for k, v in colunas_destino.items()])}
            );
        """
        dataRequest.execute(replace_query)

    create_index_wellhead = """CREATE INDEX IF NOT EXISTS idx_surgeries_rgo_created_at_record_id ON surgeries_rgo (id_hospital,(created_at::date), record_id);"""
    dataRequest.execute(create_index_wellhead, isWellheadEngine= True)
    create_index_local = """CREATE INDEX IF NOT EXISTS idx_surgeries_rgo_created_at_record_id ON surgeries_rgo (created_at, record_id);"""
    dataRequest.execute(create_index_local)

    df = dataRequest.get_data(queryText= query_dowloader, chunck= 100000, isWellheadEngine=True)
    count = 0
    with Pool(4) as pool:
        for result in pool.imap_unordered(worker_uploader, df):
            count += result
    
    print(f"Baixado no total: {count} linhas em surgeries_rgo - downloader Cirurgias 4")

if __name__ == "__main__":
    main()