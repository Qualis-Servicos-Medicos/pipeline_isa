from ImpararePackage import maestro
from ImpararePackage import dataRequest
from multiprocessing import Pool, cpu_count
import pandas as pd

def worker(c = pd.DataFrame):

    c = maestro.parse_date(df= c, column= "dt_nascimento", dayfirst=True)#, format="%d/%m/%Y")
    c = maestro.remove_columns(df= c, column= "dt_nascimento")
    
    dataRequest.set_data_on_sql(df= c, nomeTabelaDestino= "imparare2_pacientes_prepared", if_exists= "append")

def main():
    replace = True

    if replace:
        create_query ="""
            DROP TABLE IF EXISTS "imparare2_pacientes_prepared";
            CREATE UNLOGGED TABLE "imparare2_pacientes_prepared" (
                registro INTEGER,
                nome_paciente TEXT,
                sexo TEXT,
                dt_nascimento_parsed TIMESTAMP,
                count INTEGER,
                id_enterprise SMALLINT
            );
        """
        dataRequest.execute(create_query)
                
    append_query = f"""
        SELECT 
            record_id AS registro,
            MAX(patient_name) AS nome_paciente,
            MAX("SEXO_dku_lst") AS sexo,
            TO_CHAR(MAX(birthdate_dku_lst),'DD/MM/YYYY') AS dt_nascimento,
            COUNT(*) AS count,
            id_enterprise
        FROM (
            SELECT 
                record_id, 
                sex, 
                TO_CHAR(birthdate,'DD/MM/YYYY') AS birthdate, 
                LAST_VALUE(patient_name) OVER (PARTITION BY record_id, h.id_enterprise ORDER BY record_id, h.id_enterprise ASC ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS patient_name,
                LAST_VALUE(sex) OVER (PARTITION BY record_id, h.id_enterprise ORDER BY record_id, h.id_enterprise ASC ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS "SEXO_dku_lst",
                LAST_VALUE(birthdate) OVER (PARTITION BY record_id, h.id_enterprise ORDER BY record_id, h.id_enterprise  ASC ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS birthdate_dku_lst,
                h.id_enterprise
            FROM patients_records pr
            JOIN hospitals h
                ON pr.id_hospital = h.id_hospital
            INNER JOIN patients_to_update ptu
                ON pr.record_id = ptu.record_id
                    AND h.id_enterprise = ptu.id_enterprise
        ) dku__subquery
        GROUP BY registro, id_enterprise;
    """
    df_iterator = dataRequest.get_data(queryText= append_query, chunck=2000)
    with Pool(processes= cpu_count()) as pool:
        for _ in pool.imap_unordered(worker, df_iterator):
            pass
    
if __name__ == "__main__":
    main()

