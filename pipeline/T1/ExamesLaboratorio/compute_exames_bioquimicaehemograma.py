import unicodedata

from ImpararePackage import dataRequest, maestro
from multiprocessing import Pool, cpu_count
import pandas as pd
import re

def tratar_resultado_exame(valor):
    texto = str(valor).strip().upper()
    termos_negativos = ["NEGATIV", "NAO DETECT", "NÃO DETECT", "NOT DETEC", "NORNAL", "AUSENT", "NAO REAGENTE", "NÃO REAGENTE"]
    termos_positivos = ["POSITIV", "DETECT", "REAGENTE", "ALTERA", "PRESENT", "INCONC", "INDETERM"] #O QUE É P RESULTADO "ALTA" PARA PCR DE VRUS RESPIRATORIO?
    numeros_limpos = re.sub(r'[^0-9.,]', '', texto)

    if any(termo in texto for termo in termos_negativos):
        return 0
    elif any(termo in texto for termo in termos_positivos):
        return 1
    
    numeros_limpos = re.sub(r'[^0-9.,]', '', texto)
    if not numeros_limpos:
        return None
    try:
        if ',' in numeros_limpos and '.' in numeros_limpos:
            numeros_limpos = numeros_limpos.replace('.', '').replace(',', '.')
        elif ',' in numeros_limpos:
            numeros_limpos = numeros_limpos.replace(',', '.')
        return float(numeros_limpos)
    except ValueError:
        return None #força a só tratar os tipos de resultado elencados na função, vai dar nulo para qualquer outro resultado

def normalizar_texto(texto) -> str:
    if texto is None:
        return ""
    texto_sem_acento = unicodedata.normalize('NFD', str(texto)).encode('ascii', 'ignore').decode("utf-8")
    return texto_sem_acento.strip().upper()

def transpose(row):

    tipo = row['tipo']
    nome = row['exam_lab_name']
    valor = row['valor']

    if 'LEUCOC' in tipo and 'HEMOGRAMA' in nome:
        row['leucocitos'] = valor
    elif tipo == 'RDW':
        row['rdw'] = valor
    elif 'SEGMENTADO' in tipo and 'HEMOGRAMA' in nome:
        row['neutrofilo'] = valor
    elif ('RESULTADO' in tipo or 'PCR' in tipo) and 'PROTEINA C REATIVA' in nome:
        row['pcr'] = valor
    elif 'CLOSTRIDIUM' in nome:
        row['clostridium'] = valor
    elif 'MRSA' in nome:
        row['mrsa'] = valor
    elif 'MYCO' in nome:
        row['outras_bacterias'] = valor
    elif not 'ROTAV' in nome and not 'ZIKA' in nome and not 'ADENO' in nome and not 'EPSTEIN' in nome and any(term in nome for term in ['VI','COVID', 'RESPI']):
        row['virus_resp'] = valor
    elif any(term in nome for term in ['ROTAV', 'ZIKA', 'EPSTEIN', 'CITOMEG', 'DENGUE']):
        row['outros_virus'] = valor
    elif not 'EPSTEIN' in nome and any(term in nome for term in ['BAAR']):
        row['baar'] = valor
    elif any(term in nome for term in ['ASPERG', 'CRYPT']):
        row['fungos'] = valor
    elif 'PROT' in tipo and'LIQUOR' in nome:
        row['proteina_liquor'] = valor
    elif 'GLICOSE' in tipo and'LIQUOR' in nome:
        row['glicose_liquor'] = valor
    else:
        #print(f"deu ruim: {nome} - {tipo} - {valor}")
        print (normalizar_texto(tipo))
        
    return row

def worker(c:pd.DataFrame):
    c['valor'] = c['valor'].apply(tratar_resultado_exame).astype(float)
    c[['leucocitos', 'rdw', 'neutrofilo', 'clostridium', 'mrsa', 'virus_resp', 'outros_virus', 'proteina_liquor', 'glicose_liquor', 'pcr', 'fungos', 'baar', 'outras_bacterias']] = None

    c ['tipo']= c.apply(lambda x: normalizar_texto(x['tipo']), axis=1)
    c ['exam_lab_name']= c.apply(lambda x: normalizar_texto(x['exam_lab_name']), axis=1)
    c = c.apply(transpose, axis= 1)
    
    c[['leucocitos', 'rdw', 'neutrofilo', 'glicose_liquor', 'proteina_liquor', 'pcr']] = c[['leucocitos', 'rdw', 'neutrofilo', 'glicose_liquor', 'proteina_liquor', 'pcr']].astype(float)
    c.drop(columns=['tipo', 'valor', 'exam_lab_name'], inplace = True)

    dataRequest.set_data_on_sql(c, nomeTabelaDestino= 'hemograma_bioquimica_pivot', if_exists= 'append')


def main():
    replace =True

    if replace:
        create_query = """
            DROP TABLE IF EXISTS hemograma_bioquimica_pivot;
            CREATE UNLOGGED TABLE hemograma_bioquimica_pivot (
                registro INTEGER,
                laboratory_request_date TIMESTAMP,
                leucocitos FLOAT,
                rdw FLOAT,
                neutrofilo FLOAT,
                clostridium FLOAT,
                mrsa FLOAT,
                outras_bacterias FLOAT,
                fungos FLOAT,
                baar FLOAT,
                virus_resp FLOAT,
                outros_virus FLOAT,
                pcr FLOAT,
                proteina_liquor FLOAT,
                glicose_liquor FLOAT,
                id_enterprise SMALLINT
            );

            CREATE INDEX IF NOT EXISTS hemograma_bioquimica_pivot_idx_1 ON hemograma_bioquimica_pivot(id_enterprise, registro, date(laboratory_request_date));
        """
        dataRequest.execute(create_query)

    append_query = f"""
        SELECT 
            er.record_id as registro, 
            laboratory_request_date,
            exam_lab_name,
            er.exam_result_description as valor,
            exam_result_field_name as tipo,
            h.id_enterprise::SMALLINT
        FROM exams_reports er
        INNER JOIN hospitals h 
            on er.id_hospital = h.id_hospital
        INNER JOIN patients_to_update ptu
            ON er.record_id = ptu.record_id
                AND h.id_enterprise = ptu.id_enterprise
        WHERE  (
                (LOWER(exam_lab_name) = 'hemograma' and exam_result_field_name in ('GLOBAL DE LEUCOCITOS', 'RDW', 'SEGMETADO NEUTROFILO', 'Contagem de leucócitos', 'Leucócitos', 'Segmentados')) 
                or (er.exam_lab_name in ('PCR (PROTEINA C REATIVA)', 'PCR - Proteína C Reativa') and er.exam_result_field_name in ('RESULTADO', 'PCR - Proteína C Reativa'))
                or er.exam_result_field_name ilike'%prot%li%'
                or er.exam_result_field_name ilike'%glic%quor%'
                or (er.exam_lab_name in ('ROTINA DE LIQUIDO CEFALORRAQUIDIANO (LIQUOR)', 'Rotina de Líquor') and (er.exam_result_field_name ilike '%PROTE%' or UPPER(er.exam_result_field_name) = 'GLICOSE'))
                or er.exam_lab_name ilike '%clostr%'
                or er.exam_lab_name ilike '%mrsa%'
                or er.exam_lab_name ilike '%crypt%'
                or er.exam_lab_name ilike '%asperg%'
                or er.exam_lab_name ilike '%baar%'
                or er.exam_lab_name ilike '%citomeg%'
                or er.exam_lab_name ilike '%myco%'
                or er.exam_lab_name ilike '%rotav%'
                or er.exam_lab_name ilike '%dengue%'
                or er.exam_lab_name ilike '%zika%'
                or (er.exam_lab_name ilike '%sinci%'and er.exam_result_field_name = 'RESULTADO')
                or (er.exam_lab_name ilike '%covid%' and er.exam_result_field_name ~* '(resultado|influenza|sars)')
                or er.exam_lab_name in ('PAINEL INF RESPIRATÓRIAS VIRAIS, MYCOPLASMA E BORDETELLA', 'Painel Respiratório Plus - Detecção Por PCR')
            );
    """

    df_iterator = dataRequest.get_data(queryText= append_query, chunck= 2000)
    with Pool(processes= cpu_count()) as pool:
        for _ in pool.imap_unordered(worker, df_iterator):
            pass

if __name__ == "__main__":
    main()