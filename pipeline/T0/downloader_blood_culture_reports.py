from ImpararePackage import dataRequest
from ImpararePackage import maestro
import pandas as pd
from multiprocessing import Pool, cpu_count

def worker_uploader(c: pd.DataFrame) -> int:
    dataRequest.set_data_on_sql(df= c, nomeTabelaDestino= "blood_culture_reports", if_exists= "append")
    return len(c)

def main():
    print ("Iniciando downloader_blood_culture_reports")
    colunas_download = {
        "created_at": ("blood_culture_reports.created_at", "date"),
        "record_id": ("blood_culture_reports.record_id", "integer"),
        "attendance_type": ("blood_culture_reports.attendance_type", "text"), 
        "exam_lab_name": ("blood_culture_reports.exam_lab_name", "text"),
        "laboratory_request_id": ("blood_culture_reports.laboratory_request_id", "integer"), 
        "blood_culture_request_date": ("blood_culture_reports.blood_culture_request_date", "timestamp"), 
        "blood_culture_collection_date": ("blood_culture_reports.blood_culture_collection_date", "timestamp"),
        "signature_date": ("blood_culture_reports.signature_date", "timestamp"),
        "colony_obs_description": ("blood_culture_reports.colony_obs_description", "text"),
        "material_obs_description": ("blood_culture_reports.material_obs_description", "text"),
        "material_description": ("blood_culture_reports.material_description", "text"),
        "bacteriological_description": ("blood_culture_reports.bacteriological_description", "text"),
        "bacterioscopic_description": ("blood_culture_reports.bacterioscopic_description", "text"),
        "id_hospital": ("blood_culture_reports.id_hospital", "integer"),
    }

    colunas_destino = {k: v[1] for k, v in colunas_download.items()}
    select_fields = [f"{v[0]}::{v[1]} AS {k}" for k, v in colunas_download.items()]
    
    query_dowloader = f"""
        SELECT 
            {', '.join(select_fields)}
        FROM blood_culture_reports
    """

    replace = True
    try:
        query_last_dowloaded_date = """
            SELECT 
                created_at 
            FROM blood_culture_reports
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
        print(f"Erro na busca da ultima data de criacao, baixando tudo novamente")

    if replace:
        replace_query = f"""
            DROP TABLE IF EXISTS blood_culture_reports;
            CREATE UNLOGGED TABLE blood_culture_reports (
                {', '.join([f'{k} {v}' for k, v in colunas_destino.items()])}
            );
        """
        dataRequest.execute(replace_query)

    create_index_wellhead = """CREATE INDEX IF NOT EXISTS idx_blood_culture_reports_created_at_record_id ON blood_culture_reports (id_hospital, created_at, record_id);"""
    dataRequest.execute(create_index_wellhead, isWellheadEngine= True)
    create_index_local = """CREATE INDEX IF NOT EXISTS idx_blood_culture_reports_created_at_record_id ON blood_culture_reports (created_at, record_id);"""
    dataRequest.execute(create_index_local)

    df = dataRequest.get_data(queryText= query_dowloader, chunck= 100000, isWellheadEngine=True)

    count = 0
    with Pool(4) as pool:
        for result in pool.imap_unordered(worker_uploader, df):
            count += result
        
    print(f"Baixado no total: {count} linhas em blood_culture_reports - downloader_blood_culture_reports")

if __name__ == "__main__":
    main()