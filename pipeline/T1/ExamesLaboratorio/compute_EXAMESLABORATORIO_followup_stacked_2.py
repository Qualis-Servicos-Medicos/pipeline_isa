from ImpararePackage import dataRequest, maestro

def main():
    dataRequest.execute(f"""
        SET synchronous_commit = off;
        DROP TABLE IF EXISTS imparare2_exameslaboratorio_followup_stacked;
        CREATE UNLOGGED TABLE imparare2_exameslaboratorio_followup_stacked AS
        SELECT 
            DISTINCT * 
        FROM (
            SELECT DISTINCT
                laboratory_request_date::varchar|| ' ' ||laboratory_request_delivery_date::varchar|| ' ' ||er.record_id::varchar|| ' ' ||h.id_enterprise::varchar|| ' ' ||exam_lab_name|| ' ' ||exam_result_field_name|| ' ' ||COALESCE(exam_result_description::varchar, '1') as id,
                er.record_id AS registro,
                exam_lab_name AS exame,
                laboratory_request_date AS dthr_pedido,
                laboratory_request_delivery_date AS dthr_entrega,
                exam_result_field_name AS item_exame,
                exam_result_description AS ds_resultado,
                'I' as tipo_atendimento,
                h.id_enterprise,
                0::smallint as gmr
            FROM exams_reports er
            JOIN hospitals h 
            	ON er.id_hospital = h.id_hospital
            INNER JOIN patients_to_update ptu
                ON er.record_id = ptu.record_id
                    AND h.id_enterprise = ptu.id_enterprise
            WHERE exam_result_description IS NOT NULL
            UNION ALL
            SELECT
                dthr_pedido::varchar|| ' ' ||signature_date::varchar|| ' ' ||registro::varchar|| ' ' ||id_enterprise::varchar|| ' ' ||exame|| ' ' ||'OBSERVAÇÃO DO MATERIAL'|| ' ' ||COALESCE(material_amostra::varchar, '1')|| ' ' ||COALESCE(tipo_atendimento::varchar, '1') as id,
                registro, 
                exame,
                dthr_pedido,
                signature_date AS dthr_entrega, 
                'OBSERVAÇÃO DO MATERIAL' AS item_exame, 
                obs_material as ds_resultado,  
                tipo_atendimento,
                id_enterprise,
                0::smallint as gmr
            FROM imparare2_wellhead_hml_blood_culture_prepared p
            WHERE obs_material IS NOT NULL
            UNION ALL
            SELECT
                dthr_pedido::varchar|| ' ' ||signature_date::varchar|| ' ' ||registro::varchar|| ' ' ||id_enterprise::varchar|| ' ' ||exame|| ' ' ||'OBSERVAÇÃO DA COLÔNIA'|| ' ' ||COALESCE(material_amostra::varchar, '1')|| ' ' ||COALESCE(tipo_atendimento::varchar, '1') as id,
                registro, 
                exame,
                dthr_pedido,
                signature_date AS dthr_entrega, 
                'OBSERVAÇÃO DA COLÔNIA' AS item_exame, 
                obs_colonia as ds_resultado,            
                tipo_atendimento,
                id_enterprise,
                0::smallint as gmr
            FROM imparare2_wellhead_hml_blood_culture_prepared p
            WHERE obs_colonia is not null
            UNION ALL
            SELECT
                dthr_pedido::varchar|| ' ' ||signature_date::varchar|| ' ' ||registro::varchar|| ' ' ||id_enterprise::varchar|| ' ' ||exame|| ' ' ||'BACTERIOLÓGICO'|| ' ' ||COALESCE(material_amostra::varchar, '1')|| ' ' ||COALESCE(tipo_atendimento::varchar, '1') as id,
                registro, 
                exame,
                dthr_pedido,
                signature_date AS dthr_entrega, 
                'BACTERIOLÓGICO' AS item_exame, 
                resultado_bacteriologico AS ds_resultado,            
                tipo_atendimento,
                id_enterprise,
                0::smallint as gmr
            FROM imparare2_wellhead_hml_blood_culture_prepared p
            WHERE resultado_bacteriologico IS NOT NULL
            UNION ALL
            SELECT
                dthr_pedido::varchar|| ' ' ||signature_date::varchar|| ' ' ||registro::varchar|| ' ' ||id_enterprise::varchar|| ' ' ||exame|| ' ' ||'BACTERIOSCÓPICO'|| ' ' ||COALESCE(material_amostra::varchar, '1')|| ' ' ||COALESCE(tipo_atendimento::varchar, '1') as id,
                registro, 
                exame,
                dthr_pedido,
                signature_date AS dthr_entrega, 
                'BACTERIOSCÓPICO' AS item_exame, 
                resultado_bacterioscopico AS ds_resultado,            
                tipo_atendimento,
                id_enterprise,
                0::smallint as gmr
            FROM imparare2_wellhead_hml_blood_culture_prepared p
            WHERE resultado_bacterioscopico IS NOT NULL
            UNION ALL
            SELECT  
                dthr_pedido::varchar|| ' ' ||signature_date::varchar|| ' ' ||registro::varchar|| ' ' ||id_enterprise::varchar|| ' ' ||exame|| ' ' ||'MATERIAL'|| ' ' ||COALESCE(material_amostra::varchar, '1')|| ' ' ||COALESCE(tipo_atendimento::varchar, '1') as id,
                registro, 
                exame,
                dthr_pedido,
                signature_date AS dthr_entrega, 
                'MATERIAL' AS item_exame, 
                material_amostra as ds_resultado,            
                tipo_atendimento,
                id_enterprise,
                0::smallint as gmr
            FROM imparare2_wellhead_hml_blood_culture_prepared p
            where material_amostra is not null
        ) a;
    """)

if __name__ == "__main__":
    main()