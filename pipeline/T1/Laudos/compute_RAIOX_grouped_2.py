from ImpararePackage import dataRequest, maestro
from multiprocessing import Pool, cpu_count
import pandas as pd

def worker(c = pd.DataFrame):
    
    c = maestro.to_str_format(df= c, column= "laudos_dia")

    tuplas = [("None", "")]
    c = maestro.replace_values_list(df= c, column= "laudos_dia", arrayDeTuplas= tuplas)

    c = maestro.normalize(df= c, column= "laudos_dia")

    c = maestro.trim(df= c, column= "laudos_dia")

    tuplas = [
        (r"\n", r". "), (r"\|", r". "), (r"\s\.\s", r". "), (r"\s\s", r". "), (r"\.+", r"."), (r" +", r" ")
    ]
    c = maestro.replace_values_list(df= c, column= "laudos_dia", arrayDeTuplas= tuplas, regex=True) 

    dataRequest.set_data_on_sql(df= c, nomeTabelaDestino= "imparare2_raiox_computed", if_exists= "append")

def main():
    replace = True

    if replace:
        create_query = """
            DROP TABLE IF EXISTS imparare2_raiox_computed;
            CREATE UNLOGGED TABLE imparare2_raiox_computed (
                record_id INTEGER,
                data DATE,
                laudos_dia TEXT,
                count_laudos_dia SMALLINT,
                id_enterprise SMALLINT
            );                
        """
        dataRequest.execute(create_query)
    
    append_query = """
        SELECT 
            RX.record_id, 
            date(RX.xray_request_date) AS data,
            string_agg(RX.xray_content,' | ' order by RX.xray_request_date) AS laudos_dia,
            count(*) AS count_laudos_dia,
            h.id_enterprise AS id_enterprise
        FROM xrays_reports AS RX
        JOIN hospitals AS h
            ON RX.id_hospital = h.id_hospital
        INNER JOIN patients_to_update ptu
            ON RX.record_id = ptu.record_id
                AND h.id_enterprise = ptu.id_enterprise
        WHERE RX.xray_content IS NOT NULL
        GROUP BY RX.record_id , date(RX.xray_request_date), h.id_enterprise 
    """
    
    df_iterator = dataRequest.get_data(queryText= append_query, chunck= 2000)
    with Pool(processes= cpu_count()) as pool:
        for _ in pool.imap_unordered(worker, df_iterator):
            pass
    
if __name__ == "__main__":
    main()