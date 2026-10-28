from ImpararePackage import dataRequest
            
def main():
    query = f"""
        DROP TABLE IF EXISTS imparare2_internacoes_v2_stacked_by_cd_atendimento;
                
        CREATE UNLOGGED TABLE imparare2_internacoes_v2_stacked_by_cd_atendimento AS
            with int as (
                SELECT 
                    record_id AS registro,
                    attendance_id AS cd_atendimento,
                    attendance_date AS dthr_atendimento,
                    MAX(nmconvenio) AS nmconvenio,
                    MAX(unidade) AS unidade,
                    MAX("TIPOINT_dku_lst") AS tipo_intern,
                    MAX(dt_alta_dku_lst) AS dthr_alta,
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
            ), last_and_next_int as (
                select 
                    int.id_enterprise, 
                    int.cd_atendimento,
                    max(int2.cd_atendimento) as previous,
                    min(int3.cd_atendimento) as next
                from int 
                left join int int2
                    on int.id_enterprise  = int2.id_enterprise 
                        and int.registro = int2.registro 
                        and int2.cd_atendimento < int.cd_atendimento 
                left join int int3
                    on int.id_enterprise  = int3.id_enterprise 
                        and int.registro = int3.registro 
                        and int3.cd_atendimento > int.cd_atendimento 
                group by int.id_enterprise, int.cd_atendimento
            ), final_ints as (
                select 
                    int.registro,
                    int.cd_atendimento,
                    case when previous_int.cd_atendimento is not null and (int.dthr_atendimento::date - previous_int.dthr_alta::date) <= 1 then (
                        previous_int.cd_atendimento 
                    ) else (
                        null
                    ) end as discart_cd_atendimento,
                    case when previous_int.cd_atendimento is not null and (int.dthr_atendimento::date - previous_int.dthr_alta::date) <= 1 then (
                        previous_int.dthr_atendimento
                    ) else (
                        int.dthr_atendimento
                    ) end dthr_atendimento,
                    int.nmconvenio,
                    int.unidade,
                    int.tipo_intern,
                    coalesce(int.dthr_alta, coalesce(next_int.dthr_atendimento, case when int.tipo_intern =  'A' then int.dthr_atendimento else (NOW() - interval '1 day')::timestamp end)) as dthr_alta,
                    int.alta,
                    int.los,
                    int.id_enterprise
                from int
                left join last_and_next_int
                    on int.id_enterprise = last_and_next_int.id_enterprise 
                        and int.cd_atendimento = last_and_next_int.cd_atendimento 
                left join int as previous_int
                    on last_and_next_int.id_enterprise = previous_int.id_enterprise
                        and last_and_next_int.previous = previous_int.cd_atendimento
                left join int as next_int
                    on last_and_next_int.id_enterprise = next_int.id_enterprise
                        and last_and_next_int.next = next_int.cd_atendimento
                order by int.cd_atendimento asc
            )
            select 
                registro,
                cd_atendimento,
                dthr_atendimento,
                nmconvenio,
                unidade,
                tipo_intern,
                dthr_alta,
                alta,
                (dthr_alta::date - dthr_atendimento::date)::smallint as los,
                id_enterprise
            from final_ints
            where (cd_atendimento, id_enterprise) not in (select distinct discart_cd_atendimento as cd_atendimento, id_enterprise from final_ints where discart_cd_atendimento is not null);
        
        CREATE INDEX IF NOT EXISTS imparare2_internacoes_v2_stacked_by_cd_atendimento_idx on imparare2_internacoes_v2_stacked_by_cd_atendimento(id_enterprise, registro, cd_atendimento, dthr_atendimento, dthr_alta);
    """

    dataRequest.execute(query)

if __name__ == "__main__":
    main()