from ImpararePackage import dataRequest

def main():
    dataRequest.execute("""
        SET synchronous_commit = off;

        DROP TABLE IF EXISTS imparare2_isa_infeccao_v2;

        CREATE UNLOGGED TABLE imparare2_isa_infeccao_v2 AS
            SELECT  distinct
                ci.paciente_id::text || '_' || ci.dt_infeccao::text || '_' || ci.id_enterprise::text AS id,
                ci.paciente_id::int4                                        AS paciente_id, 
                ci.id_enterprise::int2                                      AS id_enterprise,
                ci.dt_infeccao::date                                        AS dt_infeccao, 
                ci.proba_1::float4                                          AS prob_perc,
                0::float4                                                   AS prob_perc_pnm, 
                0::int4                                                     AS pred_pnm,
                0::float4                                                   AS prob_perc_traqueo, 
                0::int4                                                     AS pred_traqueo,      
                0::float4                                                   AS prob_perc_pav, 
                0::int4                                                     AS pred_pav,
                0::float4                                                   AS prob_perc_itu, 
                0::int4                                                     AS pred_itu,
                0::float4                                                   AS prob_perc_isc, 
                0::int4                                                     AS pred_isc,
                0::float4                                                   AS prob_perc_ipcs, 
                0::int4                                                     AS pred_ipcs,
                (1 - ccir.proba_1)::float4 AS prob_perc_comunitaria,
                (CASE WHEN ccir.proba_1 IS NOT NULL AND  (1 - ccir.proba_1) > 0.5 THEN 1 ELSE 0 END)::int4 AS pred_comunitaria,
                ccir.proba_1::float4 AS prob_perc_iras,
                (CASE WHEN ccir.proba_1 IS NOT NULL AND ccir.proba_1 >= 0.5 THEN 1 ELSE 0 END)::int4 AS pred_iras,
                (ci.dt_infeccao - INTERVAL '3 day')::date AS dt_inicio,
                (ci.dt_infeccao + INTERVAL '3 day')::date AS dt_fim
            FROM imparare2_new_isa_infeccao AS ci 
                LEFT JOIN imparare2_new_isa_set_scored_casos_comunitaria_or_iras_rescaled ccir
                    ON ci.paciente_id = ccir.prontuario
                        AND ci.dt_infeccao = ccir.dia;
    """)

if __name__ == "__main__":
    main()