from ImpararePackage import dataRequest

def main():
    dataRequest.execute('DROP TABLE IF EXISTS imparare2_cirurgias_grouped_day_joined')
    dataRequest.execute("""
        SET synchronous_commit = off;
        CREATE UNLOGGED TABLE imparare2_cirurgias_grouped_day_joined AS
            SELECT DISTINCT 
                c1.patient_id AS "REGISTRO",
                c1.data AS "DATA",
                c1.tempo_cirurgia_dia AS tempo_cirurgia_dia,
                c1.count_procedimentos_dia::SMALLINT AS count_procedimentos_dia,
                c2.laudos_dia AS laudos_dia,
                c1.surgery_infection_risky,
                c1.id_enterprise::SMALLINT AS id_enterprise
            FROM imparare2_t1_cirurgias_3_4 c1
            INNER JOIN imparare2_t1_cirurgias_4_6 c2
                ON c1.patient_id = c2.patient_id
                    AND c1.data = c2.data
                    AND c1.id_enterprise = c2.id_enterprise
        """)
if __name__ == "__main__":
    main()