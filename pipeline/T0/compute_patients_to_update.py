from ImpararePackage import dataRequest

def main():
    print("Executando compute_patients_to_update.py")
    dataRequest.execute("""
        CREATE TABLE IF NOT EXISTS pipeline_execution_log(
            id SERIAL PRIMARY KEY,
            execution_date DATE NOT NULL DEFAULT CURRENT_DATE
        );

        DROP TABLE IF EXISTS patients_to_update;
        
        CREATE TABLE patients_to_update AS (
            SELECT 
                DISTINCT 
                    record_id,
                    id_enterprise
            FROM (
                SELECT 
                    DISTINCT record_id, h.id_enterprise 
                FROM evolutions e
                inner join hospitals h 
                    on e.id_hospital = h.id_hospital
                WHERE e.created_at > coalesce((SELECT execution_date FROM pipeline_execution_log pel ORDER BY id DESC LIMIT 1), DATE('2022-01-01')) - interval '1 day'
                UNION ALL
                SELECT 
                    DISTINCT record_id, h.id_enterprise 
                FROM exams_reports e
                inner join hospitals h 
                    on e.id_hospital = h.id_hospital
                WHERE e.created_at > coalesce((SELECT execution_date FROM pipeline_execution_log pel ORDER BY id DESC LIMIT 1), DATE('2022-01-01')) - interval '1 day'
                UNION ALL
                SELECT 
                    DISTINCT record_id , h.id_enterprise 
                FROM hospitalization e
                inner join hospitals h 
                    on e.id_hospital = h.id_hospital
                WHERE e.created_at > coalesce((SELECT execution_date FROM pipeline_execution_log pel ORDER BY id DESC LIMIT 1), DATE('2022-01-01')) - interval '1 day'
                UNION ALL
                SELECT 
                    DISTINCT record_id, h.id_enterprise
                FROM patients_records e
                inner join hospitals h 
                    on e.id_hospital = h.id_hospital
                WHERE e.created_at > coalesce((SELECT execution_date FROM pipeline_execution_log pel ORDER BY id DESC LIMIT 1), DATE('2022-01-01')) - interval '1 day'
                UNION ALL
                SELECT 
                    DISTINCT record_id, h.id_enterprise 
                FROM prescriptions e
                inner join hospitals h 
                    on e.id_hospital = h.id_hospital
                WHERE e.created_at > coalesce((SELECT execution_date FROM pipeline_execution_log pel ORDER BY id DESC LIMIT 1), DATE('2022-01-01')) - interval '1 day'
                UNION ALL
                SELECT 
                    DISTINCT record_id, h.id_enterprise
                FROM surgeries_rgo e
                inner join hospitals h 
                    on e.id_hospital = h.id_hospital
                WHERE e.created_at > coalesce((SELECT execution_date FROM pipeline_execution_log pel ORDER BY id DESC LIMIT 1), DATE('2022-01-01')) - interval '1 day'
                UNION ALL
                SELECT 
                    DISTINCT record_id, h.id_enterprise
                FROM surgeries_rgo_names e
                inner join hospitals h 
                    on e.id_hospital = h.id_hospital
                WHERE e.created_at > coalesce((SELECT execution_date FROM pipeline_execution_log pel ORDER BY id DESC LIMIT 1), DATE('2022-01-01')) - interval '1 day'
                UNION ALL
                SELECT 
                    DISTINCT record_id, h.id_enterprise
                FROM vital_signs e
                inner join hospitals h 
                    on e.id_hospital = h.id_hospital
                WHERE e.created_at > coalesce((SELECT execution_date FROM pipeline_execution_log pel ORDER BY id DESC LIMIT 1), DATE('2022-01-01')) - interval '1 day'
                UNION ALL
                SELECT 
                    DISTINCT record_id, h.id_enterprise
                FROM xrays_reports e
                inner join hospitals h 
                    on e.id_hospital = h.id_hospital
                WHERE e.created_at > coalesce((SELECT execution_date FROM pipeline_execution_log pel ORDER BY id DESC LIMIT 1), DATE('2022-01-01')) - interval '1 day'
            ) a
        );

        CREATE INDEX idx_patients_to_update on patients_to_update(record_id, id_enterprise);
    """)

if __name__ == "__main__":
    main()