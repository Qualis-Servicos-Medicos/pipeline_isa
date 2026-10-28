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
                MAX(ci.proba_1)::float4                                          AS prob_perc,
                0::float4                                                   AS prob_perc_pnm, 
                0::int4                                                     AS pred_pnm,
                0::float4                                                   AS prob_perc_traqueo, 
                0::int4                                                     AS pred_traqueo,      
                0::float4                                                   AS prob_perc_pav, 
                0::int4                                                     AS pred_pav,
                0::float4                                                   AS prob_perc_itu, 
                0::int4                                                     AS pred_itu,
                MAX(isc.proba_1)::float4                                    AS prob_perc_isc, 
                (CASE WHEN MAX(isc.proba_1) IS NOT NULL AND MAX(isc.proba_1) >= 0.5 THEN 1 ELSE 0 END)::int4 AS pred_isc,
                0::float4                                                   AS prob_perc_ipcs, 
                0::int4                                                     AS pred_ipcs,
                (1 - MAX(ccir.proba_1))::float4 AS prob_perc_comunitaria,
                (CASE WHEN MAX(ccir.proba_1) IS NOT NULL AND  (1 - MAX(ccir.proba_1)) > 0.5 THEN 1 ELSE 0 END)::int4 AS pred_comunitaria,
                MAX(ccir.proba_1)::float4 AS prob_perc_iras,
                (CASE WHEN MAX(ccir.proba_1) IS NOT NULL AND MAX(ccir.proba_1) >= 0.5 THEN 1 ELSE 0 END)::int4 AS pred_iras,
                (ci.dt_infeccao - INTERVAL '3 day')::date AS dt_inicio,
                (ci.dt_infeccao + INTERVAL '3 day')::date AS dt_fim
            FROM imparare2_new_isa_infeccao AS ci 
                LEFT JOIN imparare2_new_isa_set_scored_casos_comunitaria_or_iras_rescaled ccir
                    ON ci.paciente_id = ccir.prontuario
                        AND ci.id_enterprise = ccir.id_enterprise
                        AND ccir.dia between ci.dt_infeccao - INTERVAL '3 day' AND ci.dt_infeccao + INTERVAL '3 day'
                LEFT JOIN imparare2_new_isa_set_scored_casos_isc_or_others_rescaled isc
                    ON ci.paciente_id = isc.prontuario
                        AND ci.id_enterprise = isc.id_enterprise
                        AND isc.dia between ci.dt_infeccao - INTERVAL '3 day' AND ci.dt_infeccao + INTERVAL '3 day'
            group by ci.paciente_id, ci.dt_infeccao, ci.id_enterprise;
    """)

if __name__ == "__main__":
    main()