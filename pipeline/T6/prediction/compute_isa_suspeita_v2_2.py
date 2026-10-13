from ImpararePackage import dataRequest

def main():
    query = """
        SET synchronous_commit = off;

        DROP TABLE IF EXISTS imparare2_isa_suspeita_midstep;

        CREATE UNLOGGED TABLE imparare2_isa_suspeita_midstep AS
            SELECT 
                prontuario, 
                id_enterprise, 
                month_start, 
                month_end, 
                month_quadrant, 
                dia as first_date, 
                proba_1 as max_prob, 
                rescaled_proba_1
            FROM(
                SELECT i.prontuario, i.id_enterprise, i.month_start, i.month_end, i.month_quadrant, 
                (SELECT i3.dia
                    FROM imparare2_new_isa_set_scored_casos_infeccao_rescaled i3
                    WHERE i.prontuario = i3.prontuario
                        AND i.id_enterprise = i3.id_enterprise
                        AND i.month_quadrant = i3.month_quadrant
                        AND i3.dia >= i.month_start
                        AND i3.dia <= i.month_end
                    ORDER BY i3.proba_1 DESC
                    LIMIT 1) dia,
                (SELECT i3.proba_1
                    FROM imparare2_new_isa_set_scored_casos_infeccao_rescaled i3
                    WHERE i.prontuario = i3.prontuario
                        AND i.id_enterprise = i3.id_enterprise
                        AND i.month_quadrant = i3.month_quadrant
                        AND i3.dia >= i.month_start
                        AND i3.dia <= i.month_end
                    ORDER BY i3.proba_1 DESC
                    LIMIT 1) proba_1,
                (SELECT i3.rescaled_proba_1
                    FROM imparare2_new_isa_set_scored_casos_infeccao_rescaled i3
                    WHERE i.prontuario = i3.prontuario
                        AND i.id_enterprise = i3.id_enterprise
                        AND i.month_quadrant = i3.month_quadrant
                        AND i3.dia >= i.month_start
                        AND i3.dia <= i.month_end
                    ORDER BY i3.proba_1 DESC
                    LIMIT 1) rescaled_proba_1
                FROM imparare2_new_isa_set_scored_casos_infeccao_rescaled as i
            ) a 
            GROUP BY prontuario, id_enterprise, month_start, month_end, month_quadrant, dia, proba_1, rescaled_proba_1;

        CREATE INDEX IF NOT EXISTS imparare2_isa_suspeita_midstep_2_idx ON imparare2_isa_suspeita_midstep(id_enterprise, prontuario, month_start, month_end);
    """
    dataRequest.execute(queryText= query)

    query = """
        SET synchronous_commit = off;

        DROP TABLE IF EXISTS imparare2_isa_suspeita_midstep_max;

        CREATE UNLOGGED TABLE imparare2_isa_suspeita_midstep_max AS
            SELECT 
                prontuario, 
                id_enterprise, 
                month_start, 
                month_end, 
                (SELECT i.first_date
                    FROM imparare2_isa_suspeita_midstep i
                    WHERE m.prontuario = i.prontuario 
                        AND m.id_enterprise = i.id_enterprise
                        AND m.month_start = i.month_start
                    ORDER BY i.max_prob DESC
                    LIMIT 1) as first_date,
                (SELECT i.month_quadrant
                    FROM imparare2_isa_suspeita_midstep i
                    WHERE m.prontuario = i.prontuario 
                        AND m.id_enterprise = i.id_enterprise
                        AND m.month_start = i.month_start
                    ORDER BY i.max_prob DESC
                    LIMIT 1) as month_quadrant,
                (SELECT i.max_prob
                    FROM imparare2_isa_suspeita_midstep i
                    WHERE m.prontuario = i.prontuario 
                        AND m.id_enterprise = i.id_enterprise
                        AND m.month_start = i.month_start
                    ORDER BY i.max_prob DESC
                    LIMIT 1) as max_prob, 
                (SELECT i.rescaled_proba_1
                    FROM imparare2_isa_suspeita_midstep i
                    WHERE m.prontuario = i.prontuario 
                        AND m.id_enterprise = i.id_enterprise
                        AND m.month_start = i.month_start
                    ORDER BY i.max_prob DESC
                    LIMIT 1) as rescaled_proba_1
            FROM imparare2_isa_suspeita_midstep m
            GROUP BY prontuario, id_enterprise, month_start, month_end
            ORDER BY prontuario, id_enterprise, month_start, first_date;

        CREATE INDEX IF NOT EXISTS imparare2_isa_suspeita_midstep_max_1_idx ON imparare2_isa_suspeita_midstep_max(id_enterprise, prontuario, month_start, month_end);
    """
    dataRequest.execute(queryText= query)

    query = """
        SET synchronous_commit = off;

        DROP TABLE IF EXISTS imparare2_isa_suspeita_v2;

        CREATE UNLOGGED TABLE imparare2_isa_suspeita_v2 AS
            SELECT 
                DISTINCT *
            FROM(
                SELECT 
                    s.prontuario as paciente_id, 
                    s.id_enterprise as id_enterprise,
                    i."cd_atendimento",
                    i."dthr_atendimento" as dthr_internacao,
                    i."dthr_alta" as dthr_alta,
                    s.first_date::date as dt_infeccao, 
                    s.max_prob as prob_perc,
                    s.max_prob as max_prob,
                    s."first_date"::date
                FROM (
                    SELECT 
                        prontuario, 
                        id_enterprise,
                        month_start, 
                        month_end,
                        first_date, 
                        month_quadrant, 
                        max_prob, 
                        rescaled_proba_1
                    FROM public.imparare2_isa_suspeita_midstep_max
                    UNION
                    SELECT 
                        midstep.prontuario, 
                        midstep.id_enterprise,
                        midstep.month_start, 
                        midstep.month_end, 
                        midstep.first_date, 
                        midstep.month_quadrant, 
                        midstep.max_prob, 
                        midstep.rescaled_proba_1
                    FROM imparare2_isa_suspeita_midstep midstep
                    LEFT JOIN imparare2_isa_suspeita_midstep_max midstep_max 
                        ON midstep.prontuario = midstep_max.prontuario
                            AND midstep.month_start = midstep_max.month_start
                            AND midstep.month_end = midstep_max.month_end
                            AND midstep.id_enterprise = midstep_max.id_enterprise
                            AND (midstep.month_quadrant = midstep_max.month_quadrant + 2
                                OR midstep.month_quadrant = midstep_max.month_quadrant - 2)
                        WHERE midstep_max.* IS NOT NULL
                ) s
                JOIN imparare2_internacoes_v2_stacked_by_cd_atendimento i  
                    ON s.prontuario = i.registro
                        and s.id_enterprise = i.id_enterprise
                        and s.first_date::timestamp BETWEEN DATE_TRUNC('day', i.dthr_atendimento)::timestamp AND DATE_TRUNC('day', COALESCE(i."dthr_alta", now()))::timestamp
                ORDER BY s.prontuario, s.month_start, s.month_end, s.first_date
            ) a;
            
        create index imparare2_isa_suspeita_v2_idx on imparare2_isa_suspeita_v2(paciente_id, id_enterprise, dt_infeccao);
    """
    dataRequest.execute(queryText= query)

if __name__ == "__main__":
    main()