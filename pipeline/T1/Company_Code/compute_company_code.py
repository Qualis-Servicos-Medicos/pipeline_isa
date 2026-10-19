from ImpararePackage import dataRequest
from ImpararePackage import maestro
from multiprocessing import Pool, cpu_count
import pandas as pd

def worker(c:pd.DataFrame):
    dataRequest.set_data_on_sql(df= c, nomeTabelaDestino= "imparare2_company_code", if_exists= "append")


def main():
    dataRequest.execute('CREATE INDEX IF NOT EXISTS hospitalization_record_id_idx ON  hospitalization (record_id); ', isWellheadEngine= True)
    
    dataRequest.execute('CREATE INDEX IF NOT EXISTS hospitalization_attendance_id_idx ON  hospitalization (attendance_id); ', isWellheadEngine= True)
    replace =True

    if replace:
        create_query = """
            DROP TABLE IF EXISTS imparare2_company_code;
            CREATE UNLOGGED TABLE imparare2_company_code (
                record_id INTEGER,
                attendance_id INTEGER,
                attendance_date DATE,
                hospital_discharge_date DATE,
                id_hospital smallint,
                id_enterprise smallint
            );

            create index imparare2_company_code_idx on imparare2_company_code(record_id, id_enterprise, attendance_date, attendance_id);
        """
        dataRequest.execute(create_query)

    append_query = f"""
        select 
            distinct on (
                a.record_id, 
                a.attendance_id,
                a.attendance_date,
                h.id_hospital
            )
            a.record_id, 
            a.attendance_id,
            a.attendance_date,
            a.hospital_discharge_date,
            h.id_hospital,
            h.id_enterprise
        FROM hospitalization a
        INNER JOIN hospitals as h
        	on a.id_hospital = h.id_hospital
        INNER JOIN patients_to_update ptu
            ON a.record_id = ptu.record_id
                AND h.id_enterprise = ptu.id_enterprise
    """
    
    df_iterator = dataRequest.get_data(queryText= append_query, chunck= 2000)
    with Pool(processes= cpu_count()) as pool:
        for _ in pool.imap_unordered(worker, df_iterator):
            pass


if __name__ == "__main__":
    main()