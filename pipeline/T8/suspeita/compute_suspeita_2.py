from ImpararePackage import dataRequest, maestro

def main():
    if maestro.get_must_update_all_patients() == "1":
        create_query = """
            DROP TABLE IF EXISTS isa_suspeita;
            CREATE UNLOGGED TABLE isa_suspeita (
                id TEXT, 
                paciente_id INTEGER,
                id_enterprise SMALLINT,
                cd_atendimento INTEGER, 
                dthr_alta TIMESTAMP, 
                dt_infeccao TIMESTAMP,
                prob_perc FLOAT4, 
                max_prob FLOAT4, 
                criterio TEXT, 
                dthr_internacao TIMESTAMP, 
                id_hospital smallint
            );
            """
        dataRequest.execute(create_query, isLocal= True)
        # dataRequest.execute(create_query, isLocal= False)
    else:
        # Drop local table
        dataRequest.execute("DELETE FROM isa_suspeita WHERE (paciente_id, id_enterprise) in (select distinct record_id, id_enterprise from patients_to_update)", isLocal= True)
        
        #Busca IDS para deleção
        df = dataRequest.get_data(queryText= f"SELECT distinct record_id, id_enterprise FROM patients_to_update", chunck= None)

        ids = ""
        for i in range(len(df)):
            ids += f"({df.iloc[i]['record_id']}, {df.iloc[i]['id_enterprise']}),"
        ids = ids.strip(",")
        dataRequest.execute(f"DELETE FROM isa_suspeita WHERE (paciente_id, id_enterprise) in ({ids})", isLocal= False)


    append_query = """
        SELECT DISTINCT
            s.paciente_id::text || '_' || s.id_enterprise::text || '_' || s.cd_atendimento::text || '_' || s.dt_infeccao::text as id, 
            s.paciente_id, 
            s.id_enterprise,
            s.cd_atendimento, 
            s.dthr_alta, 
            s.dt_infeccao,
            s.prob_perc, 
            s.max_prob, 
            null as criterio, 
            s.dthr_internacao,
            c.id_hospital
        FROM imparare2_isa_suspeita_v2 as s 
        LEFT JOIN imparare2_company_code c 
            ON s.paciente_id = c.record_id
            AND s.id_enterprise = c.id_enterprise
            AND DATE(s.dt_infeccao) between DATE(c.attendance_date)
            AND coalesce(c.hospital_discharge_date, (
                SELECT min(c2.attendance_date)
                FROM imparare2_company_code c2
                WHERE c2.record_id = c.record_id AND c2.attendance_id > c.attendance_id
                GROUP BY c2.record_id 
            ), now()) + INTERVAL '1 day';
    """

    pos = 0
    df = dataRequest.get_data(queryText= append_query)
    for c in df:
        c["id_hospital"] = c["id_hospital"].astype("Int64")
        # Salvando no local
        dataRequest.set_data_on_sql(df= c, nomeTabelaDestino= "isa_suspeita", isLocal= True, if_exists= "append")
        # Salvando no remoto
        # dataRequest.set_data_on_sql(df= c, nomeTabelaDestino= "isa_suspeita", isLocal= False, if_exists= "append")
        pos += 1

if __name__ == "__main__":
    main()