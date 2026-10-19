from ImpararePackage import dataRequest, maestro
import pandas as pd
from multiprocessing import Pool

def worker(c: pd.DataFrame):
    dataRequest.set_data_on_sql(df= c, nomeTabelaDestino= "isa_pacientes_companies", if_exists= "append", isLocal= False)
    dataRequest.set_data_on_sql(df= c, nomeTabelaDestino= "isa_pacientes_companies", if_exists= "append", isLocal= True)

def main():
    if maestro.get_must_update_all_patients() == "1":
        create_query = """
            DROP TABLE IF EXISTS isa_pacientes_companies;
            CREATE UNLOGGED TABLE isa_pacientes_companies (
                paciente_id int4,
                id_hospital smallint,
                id_enterprise smallint
            );
        """
        dataRequest.execute(create_query, isLocal= False)
        dataRequest.execute(create_query, isLocal= True)
    else:
        # Drop local table
        dataRequest.execute("DELETE FROM isa_pacientes_companies WHERE (paciente_id, id_enterprise) in (select distinct record_id, id_enterprise from patients_to_update)", isLocal= True)
        
        #Busca IDS para deleção
        df = dataRequest.get_data(queryText= f"SELECT distinct record_id::text, id_enterprise FROM patients_to_update", chunck= None)

        ids = ""
        for i in range(len(df)):
            ids += f"({df.iloc[i]['record_id']}, {df.iloc[i]['id_enterprise']}),"
        ids = ids.strip(",")
        dataRequest.execute(f"DELETE FROM isa_pacientes_companies WHERE (paciente_id, id_enterprise) in ({ids})", isLocal= False)

    append_query = """ 
        SELECT DISTINCT
            record_id as paciente_id,
            id_hospital,
            id_enterprise
        FROM imparare_patient_company_treatment;
    """

    df_iterator = dataRequest.get_data(queryText= append_query)

    with Pool(4) as pool:
        for _ in pool.imap_unordered(worker, df_iterator):
            pass

if __name__ == "__main__":
    main()