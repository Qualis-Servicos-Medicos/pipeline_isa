from ImpararePackage import dataRequest
from ImpararePackage import maestro

def main():
    dataRequest.execute(f"""
        DROP TABLE IF EXISTS imparare2_wellhead_hml_blood_culture_prepared;
        CREATE UNLOGGED TABLE imparare2_wellhead_hml_blood_culture_prepared AS 
            SELECT DISTINCT 
                bcr.record_id AS registro,
                exam_lab_name AS exame,
                attendance_type as tipo_atendimento, 
                laboratory_request_id AS cd_exa_lab, 
                DATE_TRUNC('minute', blood_culture_request_date) as dthr_pedido, 
                DATE_TRUNC('minute', blood_culture_collection_date) as blood_culture_collection_date, 
                -- DATE_TRUNC('minute', blood_culture_delivery_date) as dthr_entrega, 
                -- exam_result_question_order_id AS ordem_amostra, 
                -- exam_result_field_name AS item_exame, 
                -- exam_result_description AS ds_resultado, 
                signature_date,
                colony_obs_description as obs_colonia,
                material_obs_description as obs_material,
                material_description as material_amostra,
                bacteriological_description as resultado_bacteriologico,
                bacterioscopic_description as resultado_bacterioscopico,
                h.id_enterprise
            FROM blood_culture_reports bcr
            INNER JOIN hospitals h 
                ON bcr.id_hospital = h.id_hospital
            INNER JOIN patients_to_update ptu
                ON bcr.record_id = ptu.record_id
                    AND h.id_enterprise = ptu.id_enterprise;

        CREATE INDEX IF NOT EXISTS imparare2_wellhead_hml_blood_culture_prepared_idx_1 ON imparare2_wellhead_hml_blood_culture_prepared(id_enterprise, registro, date(dthr_pedido));
    """)

if __name__ == "__main__":
    main()