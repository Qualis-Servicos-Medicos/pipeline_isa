from ImpararePackage import dataRequest

def main():
    dataRequest.execute('CREATE INDEX IF NOT EXISTS imparare2_cirurgias_grouped_day_joined_idx_1 ON imparare2_cirurgias_grouped_day_joined("REGISTRO", "DATA");')

    dataRequest.execute('DROP TABLE IF EXISTS imparare2_dataset_cirurgias')
    dataRequest.execute("""
        SET synchronous_commit = off;
        CREATE UNLOGGED TABLE imparare2_dataset_cirurgias AS
            SELECT
                pct_dia.registro as prontuario, 
                pct_dia.dia  as dia,
                pct_dia.id_enterprise as id_enterprise,
                (SELECT 
                    string_agg(cr.laudos_dia,' | ' order by cr."DATA") 
                 FROM imparare2_cirurgias_grouped_day_joined AS cr 
                 WHERE pct_dia.registro = cr."REGISTRO" 
                    AND cr."DATA" BETWEEN pct_dia.dia + INTERVAL '1 day' AND pct_dia.dia + INTERVAL '3 day'
                    AND cr.id_enterprise = pct_dia.id_enterprise
                 GROUP BY pct_dia.registro, pct_dia.dia, pct_dia.id_enterprise
                ) AS laudos_cirurgicos_futuro,
                (SELECT 
                	string_agg(cr.laudos_dia, ' | ' order by cr."DATA")
                 FROM imparare2_cirurgias_grouped_day_joined AS cr 
                 WHERE pct_dia.registro = cr."REGISTRO" 
                    AND pct_dia.dia = cr."DATA"
                    AND cr.id_enterprise = pct_dia.id_enterprise
                 GROUP BY pct_dia.registro, pct_dia.dia, pct_dia.id_enterprise
                ) AS laudos_cirurgicos_hoje,
                (SELECT 
                    string_agg(cr.laudos_dia,' | ' order by cr."DATA") 
                 FROM imparare2_cirurgias_grouped_day_joined AS cr 
                 WHERE pct_dia.registro = cr."REGISTRO" 
                    AND cr."DATA" BETWEEN pct_dia.dia - INTERVAL '3 day' AND pct_dia.dia - INTERVAL '1 day'
                    AND cr.id_enterprise = pct_dia.id_enterprise
                 GROUP BY pct_dia.registro, pct_dia.dia, pct_dia.id_enterprise
                ) AS laudos_cirurgicos_passado,
                COALESCE(
                    (SELECT SUM(cr.tempo_cirurgia_dia)
                     FROM imparare2_cirurgias_grouped_day_joined AS cr 
                     WHERE pct_dia.registro = cr."REGISTRO" 
                        AND pct_dia.dia = cr."DATA"
                    	AND cr.id_enterprise = pct_dia.id_enterprise
                     GROUP BY pct_dia.registro, pct_dia.dia, pct_dia.id_enterprise
                ), 0) AS tempo_cirurgia_hoje,
                COALESCE(
                    (SELECT SUM(cr.tempo_cirurgia_dia)
                        FROM imparare2_cirurgias_grouped_day_joined AS cr 
                        WHERE pct_dia.registro = cr."REGISTRO" 
                        AND cr."DATA" BETWEEN pct_dia.dia - INTERVAL '30 day' AND pct_dia.dia
                        AND cr.id_enterprise = pct_dia.id_enterprise
                        GROUP BY pct_dia.registro, pct_dia.dia, pct_dia.id_enterprise
                ), 0) AS tempo_cirurgia_ultimos_30_dias,
                COALESCE(
                    (SELECT SUM(cr.tempo_cirurgia_dia)
                     FROM imparare2_cirurgias_grouped_day_joined AS cr 
                     WHERE pct_dia.registro = cr."REGISTRO" 
                        AND cr."DATA" BETWEEN pct_dia.dia - INTERVAL '90 day' AND pct_dia.dia
                        AND cr.id_enterprise = pct_dia.id_enterprise
                     GROUP BY pct_dia.registro, pct_dia.dia, pct_dia.id_enterprise
                ), 0) AS tempo_cirurgia_ultimos_90_dias,
                COALESCE(
                    (SELECT sum(cr.count_procedimentos_dia::numeric) as laudo_exame_imagem_count 
                     FROM imparare2_cirurgias_grouped_day_joined AS cr 
                     WHERE pct_dia.registro = cr."REGISTRO" 
                        AND pct_dia.dia = cr."DATA"
                    	AND cr.id_enterprise = pct_dia.id_enterprise
                     GROUP BY pct_dia.registro, pct_dia.dia, pct_dia.id_enterprise
               ), 0) AS count_laudos_cirurgias_hoje,
               COALESCE(
                    (SELECT
               		  true
                     FROM imparare2_cirurgias_grouped_day_joined AS cr 
                     WHERE pct_dia.registro = cr."REGISTRO" 
                        AND cr."DATA" BETWEEN pct_dia.dia - INTERVAL '30 day' AND pct_dia.dia
                    	AND cr.id_enterprise = pct_dia.id_enterprise
               	    limit 1
               ), false) AS cirurgia_dentro_ultimos_30_dias,
               (select MAX(surgery_infection_risky) from (SELECT
                        cr.surgery_infection_risky
                    FROM imparare2_cirurgias_grouped_day_joined AS cr 
                    WHERE pct_dia.registro = cr."REGISTRO" 
                        AND cr."DATA" BETWEEN pct_dia.dia - INTERVAL '30 day' AND pct_dia.dia
                        AND cr.id_enterprise = pct_dia.id_enterprise) )as surgery_infection_risky_past_30_days,
               COALESCE(
                    (SELECT
               		  true
                     FROM imparare2_cirurgias_grouped_day_joined AS cr 
                     WHERE pct_dia.registro = cr."REGISTRO" 
                        AND cr."DATA" BETWEEN pct_dia.dia - INTERVAL '90 day' AND pct_dia.dia
                        AND cr.id_enterprise = pct_dia.id_enterprise 
               	    limit 1
               ), false) AS cirurgia_dentro_ultimos_90_dias,
               (select MAX(surgery_infection_risky) from (SELECT
                        cr.surgery_infection_risky
                    FROM imparare2_cirurgias_grouped_day_joined AS cr 
                    WHERE pct_dia.registro = cr."REGISTRO" 
                        AND cr."DATA" BETWEEN pct_dia.dia - INTERVAL '90 day' AND pct_dia.dia
                        AND cr.id_enterprise = pct_dia.id_enterprise) )as surgery_infection_risky_past_90_days,
                (pct_dia.dia - (select MAX(dia) from (
                	select 
                		"DATA" as dia 
            		from imparare2_cirurgias_grouped_day_joined cg 
					WHERE pct_dia.registro = cg."REGISTRO" 
						AND cg.surgery_infection_risky = 0
						AND cg.id_enterprise = pct_dia.id_enterprise
                        AND cg."DATA" BETWEEN pct_dia.dia - INTERVAL '90 day' AND pct_dia.dia
            		)
        		)) as days_since_risky_zero,
        		(pct_dia.dia - (select MAX(dia) from (
                	select 
                		"DATA" as dia 
            		from imparare2_cirurgias_grouped_day_joined cg 
					WHERE pct_dia.registro = cg."REGISTRO" 
						AND cg.surgery_infection_risky = 1
						AND cg.id_enterprise = pct_dia.id_enterprise
                        AND cg."DATA" BETWEEN pct_dia.dia - INTERVAL '90 day' AND pct_dia.dia
            		)
        		)) as days_since_risky_one,
        		(pct_dia.dia - (select MAX(dia) from (
                	select 
                		"DATA" as dia 
            		from imparare2_cirurgias_grouped_day_joined cg 
					WHERE pct_dia.registro = cg."REGISTRO" 
						AND cg.surgery_infection_risky = 2
						AND cg.id_enterprise = pct_dia.id_enterprise
                        AND cg."DATA" BETWEEN pct_dia.dia - INTERVAL '90 day' AND pct_dia.dia
            		)
        		)) as days_since_risky_two,
        		(pct_dia.dia - (select MAX(dia) from (
                	select 
                		"DATA" as dia 
            		from imparare2_cirurgias_grouped_day_joined cg 
					WHERE pct_dia.registro = cg."REGISTRO" 
						AND cg.surgery_infection_risky = 3
						AND cg.id_enterprise = pct_dia.id_enterprise
                        AND cg."DATA" BETWEEN pct_dia.dia - INTERVAL '90 day' AND pct_dia.dia
            		)
        		)) as days_since_risky_thre,
        		(pct_dia.dia - (select MAX(dia) from (
                	select 
                		"DATA" as dia 
            		from imparare2_cirurgias_grouped_day_joined cg 
					WHERE pct_dia.registro = cg."REGISTRO" 
						AND cg.surgery_infection_risky = 4
						AND cg.id_enterprise = pct_dia.id_enterprise
                        AND cg."DATA" BETWEEN pct_dia.dia - INTERVAL '90 day' AND pct_dia.dia
            		)
        		)) as days_since_risky_four,
        		(select 
        			laudos_dia 
    			from imparare2_cirurgias_grouped_day_joined cg
    			where pct_dia.registro = cg."REGISTRO"
					AND cg.id_enterprise = pct_dia.id_enterprise
                    AND cg."DATA" BETWEEN pct_dia.dia - INTERVAL '90 day' AND pct_dia.dia
                    ORDER BY "DATA" desc
                    limit 1) as last_cirgury_description
            FROM imparare2_dataset_label pct_dia
            LEFT JOIN imparare2_cirurgias_grouped_day_joined cj
                on pct_dia.registro = cj."REGISTRO"
                    and pct_dia.id_enterprise = cj.id_enterprise
                    and pct_dia.dia = cj."DATA";
    """)
    dataRequest.execute('CREATE INDEX IF NOT EXISTS idx_cir_reg_dia ON imparare2_dataset_cirurgias (id_enterprise, prontuario, dia);')
    
if __name__ == "__main__":
    main()