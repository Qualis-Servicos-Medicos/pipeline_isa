from ImpararePackage import dataRequest, maestro
import pandas as pd
import re
import unicodedata
from multiprocessing import Pool, cpu_count

def worker(c: pd.DataFrame):

    def normalize_text(value):
        if pd.isna(value):
            return ""
        text = str(value)
        text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8')
        text = text.upper()
        text = re.sub(r'[^A-Z0-9\s/\-]', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text


    def normalize_item_exame(value):
        text = normalize_text(value)
        if not text:
            return 'NAO_INFORMADO'

        if re.search(r'LEUC', text):
            return 'LEUCOCITOS'
        if re.search(r'SEGMENT|NEUTRO', text):
            return 'SEGMENTADO NEUTROFILO'
        if re.search(r'BACTERIOL', text):
            return 'BACTERIOLÓGICO'
        if re.search(r'BACTERIOS', text):
            return 'BACTERIOSCÓPICO'
        if re.search(r'OBSERVACAO.*MATERIAL', text):
            return 'OBSERVACAO DO MATERIAL'
        if re.search(r'OBSERVACAO.*COLONIA', text):
            return 'OBSERVACAO DA COLONIA'
        if re.search(r'MATERIAL', text):
            return 'MATERIAL'

        return text

    c['exame'] = c['exame'].apply(normalize_text)
    c['item_exame'] = c['item_exame'].apply(normalize_item_exame)
    if 'ds_resultado' in c.columns:
        c['ds_resultado'] = c['ds_resultado'].fillna('').apply(normalize_text)
    dataRequest.set_data_on_sql(df= c, nomeTabelaDestino= "imparare2_exameslaboratorio_followup_stacked", if_exists= "append", isLocal= True)


#create separado e worker para normalização - item_exame e exame, ao menos. campo resultado precisa aém de normalização de manejo do sinal (, ou .)
def main():
    replace = True

    if replace:
        create_query = """
            DROP TABLE IF EXISTS imparare2_exameslaboratorio_followup_stacked;
            CREATE UNLOGGED TABLE imparare2_exameslaboratorio_followup_stacked (
                id TEXT,
                registro INTEGER,
                exame TEXT,
                dthr_pedido TIMESTAMP,
                dthr_entrega TIMESTAMP,
                item_exame TEXT,
                ds_resultado TEXT,
                tipo_atendimento TEXT,
                id_enterprise SMALLINT,
                gmr SMALLINT
            );
        """
        dataRequest.execute(create_query)
        
    append_query = f"""
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
    """

    df_iterator = dataRequest.get_data(queryText= append_query, chunck= 20000)
        
    with Pool(processes=cpu_count()) as pool:
        for _ in pool.imap_unordered(worker, df_iterator):
            pass
    
if __name__ == "__main__":
    main()