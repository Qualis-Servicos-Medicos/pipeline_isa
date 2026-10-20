from ImpararePackage import dataRequest
from ImpararePackage import maestro
from datetime import datetime
from dateutil.relativedelta import relativedelta
import pandas as pd
from multiprocessing import Pool, cpu_count


# TODO: Manter visao aqui para possiveis erros de janelas, periodo entre atendimento e alta que devem ter janelas criadas.
def worker(c:pd.DataFrame):
    df_filtered = c[c['dthr_alta'].isna()]
    linesToDrop = []
    # TODO: como melhorar isso aqui? Talvez fazer via sql seja melhor
    for index in df_filtered.index:
        df_paciente = c[c['registro'] == c.iloc[index]['registro']]
        possiveis_datas = df_paciente[df_paciente['dthr_atendimento'] > c.iloc[index]['dthr_atendimento']]
        if len(possiveis_datas) > 0:
            possiveis_datas.sort_values('dthr_atendimento', ascending= True, inplace= True)
            day = possiveis_datas.iloc[0]['dthr_atendimento']
            day = (day - relativedelta(days= 1))
            c.loc[index, 'dthr_alta'] = day
        else:
            df_por_dia = df_paciente[df_paciente['dthr_atendimento'].dt.day == c.iloc[index]['dthr_atendimento'].day] 
            df_por_mes = df_por_dia[df_por_dia['dthr_atendimento'].dt.month == c.iloc[index]['dthr_atendimento'].month]
            df_por_ano = df_por_mes[df_por_mes['dthr_atendimento'].dt.year == c.iloc[index]['dthr_atendimento'].year]
            if len(df_por_ano) > 1:
                linesToDrop.append(index)
            else:
                today = datetime.now()
                today = (today - relativedelta(days= 1))
                day = datetime(year= today.year, month= today.month, day= today.day, hour= 23, minute= 59, second= 59)
                c.loc[index, 'dthr_alta'] = day

    c.drop(index= linesToDrop, inplace= True)

    destinos = ["los"]
    referencias = [["dthr_atendimento", "dthr_alta"]]
    c = maestro.difference_time_between_columns_days(df= c, arrayColunasDestino= destinos, arrayColunasReferencia= referencias)
    
    dataRequest.set_data_on_sql(c, nomeTabelaDestino= "imparare2_internacoes_v2_stacked_by_cd_atendimento", if_exists= "append")
            
def main():
    replace =True

    if replace:
        create_query = """
            DROP TABLE IF EXISTS imparare2_internacoes_v2_stacked_by_cd_atendimento;
            CREATE UNLOGGED TABLE imparare2_internacoes_v2_stacked_by_cd_atendimento (
                registro INTEGER,
                cd_atendimento INTEGER,
                dthr_atendimento TIMESTAMP,
                dthr_alta TIMESTAMP,
                nmconvenio TEXT,
                unidade TEXT,
                tipo_intern TEXT,
                alta TEXT,
                los INTEGER,
                id_enterprise SMALLINT
            );
        """
        dataRequest.execute(create_query)

    append_query = f"""
        SELECT 
            record_id AS registro,
            attendance_id AS cd_atendimento,
            attendance_date AS dthr_atendimento,
            MAX(nmconvenio) AS nmconvenio,
            MAX(unidade) AS unidade,
            MAX("TIPOINT_dku_lst") AS tipo_intern,
            COALESCE(MAX(dt_alta_dku_lst), (NOW() - interval '1 day')::timestamp) AS dthr_alta,
            MAX("ALTA_dku_lst") AS alta,
            NULL AS los,
            id_enterprise
        FROM (
            SELECT DISTINCT 
                a.record_id, 
                attendance_id, 
                attendance_date, 
                hospital_discharge_date,
                LAST_VALUE(health_insurance_name) OVER (PARTITION BY a.record_id, h.id_enterprise, attendance_id, attendance_date ORDER BY created_at ASC ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS nmconvenio,
                LAST_VALUE(unity_code_and_description) OVER (PARTITION BY a.record_id, h.id_enterprise, attendance_id, attendance_date ORDER BY created_at ASC ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS unidade,
                LAST_VALUE(hospitalization_type) OVER (PARTITION BY a.record_id, h.id_enterprise, attendance_id, attendance_date ORDER BY created_at ASC ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS "TIPOINT_dku_lst",
                LAST_VALUE(hospital_discharge_date) OVER (PARTITION BY a.record_id, h.id_enterprise, attendance_id, attendance_date ORDER BY created_at ASC ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS dt_alta_dku_lst,
                LAST_VALUE(hospital_discharge_description) OVER (PARTITION BY a.record_id, h.id_enterprise, attendance_id, attendance_date ORDER BY created_at ASC ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS "ALTA_dku_lst",
                h.id_enterprise
            FROM hospitalization a
            INNER JOIN hospitals h
                ON a.id_hospital = h.id_hospital
            INNER JOIN patients_to_update ptu
                ON a.record_id = ptu.record_id
                    AND h.id_enterprise = ptu.id_enterprise
            WHERE a.id_hospital IS NOT NULL
        )
        GROUP BY record_id, id_enterprise, attendance_id, attendance_date
        ORDER BY record_id;
    """
    
    df_iterator = dataRequest.get_data(queryText= append_query, chunck= 20000)
    
    with Pool(processes= cpu_count()) as pool:
        for _ in pool.imap_unordered(worker, df_iterator):
            pass

if __name__ == "__main__":
    main()