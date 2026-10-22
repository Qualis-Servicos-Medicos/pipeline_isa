from ImpararePackage import dataRequest
from ImpararePackage import maestro
import pandas as pd
from multiprocessing import Pool, cpu_count

def worker_uploader(c: pd.DataFrame) -> int:
    dataRequest.set_data_on_sql(df= c, nomeTabelaDestino= "evolutions", if_exists= "append")
    return len(c)

def main():
    print ("Iniciando downloader_Evolution")
    colunas_download = {
        "record_id": ("evolutions.record_id", "integer"),
        "created_at": ("evolutions.created_at", "date"),
        "provider_profile": ("evolutions.provider_profile", "text"),
        "attendance_type": ("evolutions.attendance_type", "text"),
        "evolution_date": ("evolutions.evolution_date", "timestamp"),
        "unity_code_and_description": ("evolutions.unity_code_and_description", "text"),
        "evolution_description": ("evolutions.evolution_description", "text"),
        "id_hospital": ("evolutions.id_hospital", "integer"),
    }
    colunas_destino = {k: v[1] for k, v in colunas_download.items()}
    select_fields = [f"{v[0]}::{v[1]} AS {k}" for k, v in colunas_download.items()]

    query_dowloader = f"""
        SELECT 
           {', '.join(select_fields)}
        FROM evolutions
    """

    replace = True
    try:
        query_last_dowloaded_date = """
            SELECT created_at FROM evolutions
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
            DROP TABLE IF EXISTS evolutions;
            CREATE UNLOGGED TABLE evolutions (
                {', '.join([f'{k} {v}' for k, v in colunas_destino.items()])}
            );
        """
        dataRequest.execute(replace_query)

        # Index para otimizar busca nas proximas queries
        dataRequest.execute("CREATE INDEX IF NOT EXISTS idx_evo_group_by ON evolutions(record_id, provider_profile, evolution_date, unity_code_and_description, attendance_type);")

    create_index_wellhead = """CREATE INDEX IF NOT EXISTS idx_evolutions_created_at_record_id ON evolutions (id_hospital,(created_at::date), record_id);""" #tirado company_code do index
    dataRequest.execute(create_index_wellhead, isWellheadEngine= True)
    create_index_local = """CREATE INDEX IF NOT EXISTS idx_evolutions_created_at_record_id ON evolutions (created_at, record_id);"""
    dataRequest.execute(create_index_local)

    df = dataRequest.get_data(queryText= query_dowloader, chunck= 100000, isWellheadEngine=True)
    count = 0
    with Pool(4) as pool:
        for result in pool.imap_unordered(worker_uploader, df):
            count += result
    
    print(f"Baixado no total: {count} linhas em evolutions - downloader_Evolution")

if __name__ == "__main__":
    main()