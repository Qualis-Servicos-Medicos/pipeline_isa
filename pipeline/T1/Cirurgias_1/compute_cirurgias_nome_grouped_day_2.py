from ImpararePackage import dataRequest

def main():
    dataRequest.execute('DROP TABLE IF EXISTS "imparare2_t1_cirurgias_3_4"')
    dataRequest.execute("""
        SET synchronous_commit = off;
        CREATE UNLOGGED TABLE imparare2_t1_cirurgias_3_4 AS
            SELECT CIR.patient_id
            , CIR.dt_procedimento as data
            , sum(CIR.tempo_de_cirurgia) as tempo_cirurgia_dia
            , count(*) as count_procedimentos_dia
            , max(surgery_infection_risky) as surgery_infection_risky
            , CIR.id_enterprise
        FROM imparare2_t1_cirurgias_3_3 CIR
        GROUP BY CIR.patient_id, CIR.id_enterprise, CIR.dt_procedimento;
    """)

if __name__ == "__main__":
    main()