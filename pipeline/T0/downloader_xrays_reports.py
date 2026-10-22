from ImpararePackage import dataRequest
from ImpararePackage import maestro
import pandas as pd

def main():
    print("Inicinado downloader_xrays_reports")
    colunas_download = {
        "created_at": "date",
        "record_id": "integer",
        "xray_exam_description": "text",
        "xray_content": "text",
        "xray_request_date": "timestamp",
        "xray_delivery_date": "timestamp",
        "attendance_type": "text",
        "id_hospital": "integer"
    }
    query_dowloader = f"""
        SELECT 
           {', '.join([f'{k}::{v}' for k, v in colunas_download.items()])}
        FROM xrays_reports
        WHERE xray_exam_description IS NOT NULL
            AND xray_request_date IS NOT NULL
            AND xray_delivery_date IS NOT NULL
    """

    replace = True
    try:
        query_last_dowloaded_date = """
            SELECT 
                created_at 
            FROM xrays_reports
            ORDER BY created_at DESC
            LIMIT 1
        """
        df = dataRequest.get_data(queryText= query_last_dowloaded_date, chunck= None)

        last_date = df.iloc[0]["created_at"]
        if last_date is not None and not pd.isna(last_date):
            query_dowloader += f" AND date(created_at) > '{last_date}'"
            replace = False
    except:
        print(f"Erro na busca da ultima data, baixando tudo novamente")

    # Forçando buscar tudo novamente
    replace = True
    if replace:
        replace_query = f"""
            DROP TABLE IF EXISTS xrays_reports;
            CREATE UNLOGGED TABLE xrays_reports (
                {', '.join([f'{k} {v}' for k, v in colunas_download.items()])}
            );
        """
        dataRequest.execute(replace_query)
    
    create_index_wellhead = """CREATE INDEX IF NOT EXISTS idx_xrays_reports_created_at_record_id ON xrays_reports (id_hospital, (created_at::date), record_id);"""
    dataRequest.execute(create_index_wellhead, isWellheadEngine= True)
    create_index_local = """CREATE INDEX IF NOT EXISTS idx_xrays_reports_created_at_record_id ON xrays_reports (created_at, record_id);"""
    dataRequest.execute(create_index_local)
    # print(query_downloader)

    df = dataRequest.get_data(queryText= query_dowloader, chunck= 100000, isWellheadEngine=True)
    count = 0
    for c in df:
        count += len(c)
        dataRequest.set_data_on_sql(df= c, nomeTabelaDestino= "xrays_reports", if_exists= "append")

    print(f"Baixado no total: {count} linhas em xrays_reports - downloader_xrays_reports")
    
if __name__ == "__main__":
    main()

