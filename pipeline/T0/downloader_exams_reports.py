from ImpararePackage import dataRequest
from ImpararePackage import maestro
import pandas as pd
from multiprocessing import Pool, cpu_count

def worker_uploader(c: pd.DataFrame) -> int:
    dataRequest.set_data_on_sql(df= c, nomeTabelaDestino= "exams_reports", if_exists= "append")
    return len(c)

def main():
    print ("Iniciando downloader_exams_reports")
    colunas_download = {
        "record_id": ("exams_reports.record_id", "integer"),
        "created_at": ("exams_reports.created_at", "date"),
        "exam_lab_name": ("exams_reports.exam_lab_name", "text"),
        "laboratory_request_date": ("exams_reports.laboratory_request_date", "timestamp"),
        "laboratory_request_delivery_date": ("exams_reports.laboratory_request_delivery_date", "timestamp"),
        "exam_result_field_name": ("exams_reports.exam_result_field_name", "text"),
        "exam_result_description": ("exams_reports.exam_result_description", "text"),
        "id_hospital": ("exams_reports.id_hospital", "integer"),
    }

    colunas_destino = {k: v[1] for k, v in colunas_download.items()}
    select_fields = [f"{v[0]}::{v[1]} AS {k}" for k, v in colunas_download.items()]
    
    query_dowloader = f"""
        SELECT DISTINCT
        {', '.join(select_fields)}
        FROM exams_reports
        WHERE laboratory_request_date IS NOT NULL
            AND laboratory_request_delivery_date IS NOT NULL
    """

    replace = True
    try:
        query_last_dowloaded_date = """
            SELECT 
                created_at 
            FROM exams_reports
            ORDER BY created_at DESC
            LIMIT 1
        """
        df = dataRequest.get_data(queryText= query_last_dowloaded_date, chunck= None)

        last_date = df.iloc[0]["created_at"]
        if last_date is not None and not pd.isna(last_date):
            query_dowloader += f" AND date(created_at) > '{last_date}'"
            print(f"Buscando todos os dados novos desde: {last_date}")
            replace = False
    except:
        print(f"Erro na busca da ultima data de liberação, baixando tudo novamente")

    if replace:
        replace_query = f"""
            DROP TABLE IF EXISTS exams_reports;
            CREATE UNLOGGED TABLE exams_reports (
                {', '.join([f'{k} {v}' for k, v in colunas_destino.items()])}
            );
        """
        dataRequest.execute(replace_query)

    create_index_wellhead = """CREATE INDEX IF NOT EXISTS idx_exams_reports_created_at_record_id ON exams_reports (id_hospital,(created_at::date), record_id);"""
    dataRequest.execute(create_index_wellhead, isWellheadEngine= True)
    create_index_local = """CREATE INDEX IF NOT EXISTS idx_exams_reports_created_at_record_id ON exams_reports (created_at, record_id);"""
    dataRequest.execute(create_index_local)
    print(f"Query de download: {query_dowloader}")

    df = dataRequest.get_data(queryText= query_dowloader, chunck= 100000, isWellheadEngine=True)
    count = 0
    with Pool(4) as pool:
        for result in pool.imap_unordered(worker_uploader, df):
            count += result
    
    print(f"Baixado no total: {count} linhas em exams_reports - downloader_exams_reports")


if __name__ == "__main__":
    main()