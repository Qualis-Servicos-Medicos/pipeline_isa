import pandas as pd
import numpy as np
import re
from ImpararePackage import dataRequest
from ImpararePackage import maestro
import json
from multiprocessing import Pool, cpu_count
import threading
import itertools
from elasticsearch.helpers import parallel_bulk

def regex_search(c):
    #regex_num = r'(?<!\w)[0-9]+[.,]?[0-9]*'
    #regex_num = (r'([\d]*[.,]{0,1}[\d]+)')
    regex_substring = r'(\[FISIOTERAPEUTA[^\[]+)'
    
    if c == 'peep': 
        regex_results = r'((?<!\w)peep(?![a-z])[^\[]{0,5}([0-9]+([\.][0-9]*)?|[\.][0-9]+))'
        #regex_num = r'\d{1,3}[\.]?[\d{1,3}]*'
        regex_num = r'(\d{1,3})(\.\d{1,3})?'
        #regex_substring = (r'(FISIOTERAPEUTA)[^\[]*((?<!\w)peep(?![a-z]).{0,5}([0-9]+([.][0-9]*)?|[.][0-9]+))')
        #regex_num = (r'[0-9]+((\.|\,)[0-9]*)?')
    
    elif c == 'fio2': 
        regex_results = r'((?<!\w)fio(2|²)(?![a-z])[^\[]{0,5}([0-9]+([\.][0-9]*)?|[\.][0-9]+))'
        regex_num = r'(\b)(\d{1,3})(\.\d{1,3})?'
        #regex_substring = (r'(FISIOTERAPEUTA)[^\[]*((?<!\w)fio(2|²)(?![a-z]).{0,5}([0-9]+([.][0-9]*)?|[.][0-9]+))\%')
        #regex_num = (r'[0-9]+((\.|\,)[0-9]*)?')
    
    #elif c == 'spo2': 
        #regex_results = (r'((?<!\w)spo(2|²)(?![a-z]).{0,5}([0-9]+([.][0-9]*)?|[.][0-9]+))')
        #regex_num = (r'[0-9]+((\.|\,)[0-9]*)?')        
        
    return regex_results, regex_num, regex_substring

def search_num_terms(termos_texto, regex_results, regex_num, regex_substring):
    regex_fisio = re.compile(regex_substring)
    fisio = re.findall(regex_fisio, str(termos_texto))
    
    if(not fisio):
        return []
    else:      
        regex_results = re.compile(regex_results)
        num_result = re.findall(regex_results, str(fisio))
        if(not num_result):
            return []
        else:
            if(isinstance(num_result[0], tuple)):
                num_result  = [list(filter(None, i)) for i in num_result]
                num_result = [i[0] for i in num_result]

            regex_num = re.compile(regex_num)
            num_result = re.findall(regex_num, str(num_result))
            if(not num_result):
                return []
            else:
                if(isinstance(num_result[0], tuple)):
                    #return num_result[0]
                    num_result  = [list(filter(None, i)) for i in num_result]
                    num_result = [i[0] for i in num_result]

                num_result = [x.replace(",", ".") for x in num_result]

                num_result = np.array(num_result)
                num_result = num_result.astype(float)
                return num_result
    
def json_criteria_init(dataset):
    """cria uma coluna com valores do tipo 'inválido' (ou vazio) no dataframe para cada criterio"""
    json_column_name = 'criterios_extraidos'
    dataset[json_column_name] = json.dumps({})
    dataset['col_aux'] = ''
    return dataset

def search_criterias(row):
    criteria = ['peep', 'fio2']#, 'spo2']
    json_column_name = 'criterios_extraidos'
    termos_texto = row['col_aux']
    json_column_dict = {}

    for cri in criteria:
        #regex_results, regex_num = regex_search(c)
        regex_results, regex_num, regex_substring = regex_search(cri)
        term_num_list = search_num_terms(termos_texto, regex_results, regex_num, regex_substring)
        json_column_dict[cri] = list(set(term_num_list))

    row[json_column_name] = json.dumps(json_column_dict)
    return row

def worker(c: pd.DataFrame):
    c['termos_texto'] = c['termos_texto'].astype(str)  # Ensure it's a string type
    c['termos_texto'] = c['termos_texto'].apply(lambda x: x.encode('utf-8').decode('ascii', 'ignore') if isinstance(x, str) else '')
    c = json_criteria_init(c)

    #applicado o sentenizador a coluna 'termos_texto' do dataframe      
    c['col_aux'] = c['termos_texto'].apply(lambda x: maestro.split_sentences(str(x) if not isinstance(x, str) else x)).astype(str)

    # adiciona a coluna de critérios no dataset com arrays vazios (ex: df['peep']=[], df['fio2']=[], df['spo2']=[], etc.)
    c = c.apply(search_criterias, axis = 1)
    c['prontuario'] = c['prontuario'].astype(int)
    c['id_enterprise'] = pd.to_numeric(c['id_enterprise'], errors='coerce').astype('Int64')
    c['id_hospital'] = pd.to_numeric(c['id_hospital'], errors='coerce').astype('Int64')
    
    c = maestro.remove_columns(df= c, arrayColumns= ["col_aux"])

    def elk_upload(c: pd.DataFrame):
        client = dataRequest.ELASTICSEARCH_CONNECTION
        c["paciente_id"] = c["prontuario"]
        c = maestro.keep_columns(df= c, arrayColumns= ["id", "prontuario", "id_enterprise", "id_hospital", "paciente_id", "dt_encontro", "local_encontro", "termos_texto", "termos_achados", "criterios_extraidos", "texto_evolucao_agg"])
            
        actions = maestro.generate_actions(c, "encontros")
        for success, info in parallel_bulk(
            client,
            actions,
            raise_on_error=False,
            raise_on_exception=False
        ):
            if not success:
                print(f'🔴🔴🔴 Documento falhou em sinais vitais:{info} 🔴🔴🔴')

    job = threading.Thread(target= elk_upload, args=(c.copy(), ))
    job_3 = threading.Thread(target=dataRequest.set_data_on_sql, args=(c, "isa_encontro"), kwargs={"if_exists": "append", "isLocal": True})
    
    jobs = [
        job,
        job_3
    ]
    for j in jobs:
        j.start()
    
    for j in jobs:
        j.join()

def main():
    client = dataRequest.ELASTICSEARCH_CONNECTION
    print(client.cluster.health())
    print(client.ping())

    index_name = "encontros"
    if maestro.get_must_update_all_patients() == '1':
        create_query = """
            DROP TABLE IF EXISTS isa_encontro;
            CREATE UNLOGGED TABLE isa_encontro (
                id TEXT,
                prontuario INTEGER,
                id_enterprise SMALLINT,
                dt_encontro TIMESTAMP,
                local_encontro TEXT,
                termos_texto TEXT,
                texto_evolucao_agg TEXT,
                termos_achados TEXT,
                id_hospital SMALLINT,
                criterios_extraidos TEXT
            );
        """
        # dataRequest.execute(create_query, isLocal= False)
        dataRequest.execute(create_query, isLocal= True)

        client.options(ignore_status=[400, 404]).indices.delete(index=index_name)
        
        if not client.indices.exists(index=index_name):
            print("Criando index", index_name)
            client.indices.create(
                index=index_name,
                settings={
                    "index": {
                        "max_result_window": 100000,
                        "number_of_shards": 1,
                        "number_of_replicas": 0,
                        "refresh_interval": "30s",
                        "translog": {
                            "durability": "async", # não faz fsync a cada request, só periodicamente
                            "sync_interval": "30s"
                        }
                    }
                },
                mappings= {
                    "dynamic": "strict",
                    "properties": {
                        # o front busca "encontros" por prontuario (term) + dt_encontro (range);
                        # paciente_id nao e usado nessa query, so nos outros indices
                        "id": {
                            "type": "keyword",
                            "index": False,
                            "doc_values": False
                        },
                        "prontuario": {
                            "type": "integer"
                        },
                        "id_enterprise": {
                            "type": "short"
                        },
                        "id_hospital": {
                            "type": "short",
                            "index": False,
                            "doc_values": False
                        },
                        "paciente_id": {
                            "type": "integer",
                            "index": False,
                            "doc_values": False
                        },
                        "dt_encontro": {
                            "type": "date"
                        },
                        "local_encontro": {
                            "type": "keyword", 
                            "index": False, 
                            "doc_values": False
                        },
                        # "company_id": {
                        #     "type": "keyword", 
                        #     "index": False, 
                        #     "doc_values": False
                        # },
                        "termos_texto": {
                            "type": "text", 
                            "index": False
                        },
                        "termos_achados": {
                            "type": "text", 
                            "index": False
                        },
                        "texto_evolucao_agg": {
                            "type": "text", 
                            "index": False
                        },
                        "criterios_extraidos": {
                            "type": "keyword", 
                            "index": False, 
                            "doc_values": False
                        },
                    }
                }
            )
    else: # Vamos deletar somente os dados dos pacientes que serão adicionados
        # Drop local table
        dataRequest.execute("DELETE FROM isa_encontro WHERE (prontuario, id_enterprise) in (select distinct record_id, id_enterprise from patients_to_update)", isLocal= True)

        # Drop ELK index
        df = dataRequest.get_data(queryText= f"SELECT distinct record_id, id_enterprise FROM patients_to_update", chunck= None)
        
        def chunks(seq, n):
            """Yield successive n-sized chunks from seq."""
            for i in range(0, len(seq), n):
                yield seq[i:i + n]

        total= 0
        for lote in chunks(df, 1000):
            resp = client.delete_by_query(
                index= index_name,
                query= {
                    "bool": {
                        "should": [
                            {
                                "bool": {
                                    "filter": [
                                        {"term": {"id_enterprise": ent}},
                                        {"terms": {"prontuario": grupo["record_id"].tolist()}},
                                    ]
                                }
                            }
                            for ent, grupo in lote.groupby("id_enterprise")
                        ], 
                        "minimum_should_match": 1
                    }
                },
                conflicts= "proceed",
                refresh= False,
                slices= "auto"
            )
            total += resp['deleted']
            print(f"Deletados {resp['deleted']} encontros do lote de {len(lote)} pacientes. Total deletados até agora: {total}")
        
        client.indices.refresh(index=index_name)
        print(f"Deletados {total} encontros no total para {len(df)} pacientes.")
    
    append_query = """
        SELECT distinct 
            isa_encontro.registro::varchar || '_' || isa_encontro.id_enterprise::varchar || '_' || isa_encontro.data_dia::varchar || '_' || isa_encontro.unidade_fst::varchar || '_' || isa_encontro.unidade_lst::varchar as id,
            isa_encontro.registro AS prontuario,
            c.id_hospital::SMALLINT as id_hospital,
            isa_encontro.id_enterprise::SMALLINT AS id_enterprise,
            isa_encontro.data_dia AS dt_encontro,
            isa_encontro.unidade_fst AS local_encontro,
            evolucao.termos_texto AS termos_texto,
            evolucao.texto_evolucao_agg AS texto_evolucao_agg,
            evolucao.termos_achados AS termos_achados
        FROM imparare2_evolucao_grouped isa_encontro
        LEFT JOIN imparare2_evol_sent_pos_grouped_dthr_prepared evolucao
            ON isa_encontro.registro = evolucao.registro
                AND isa_encontro.id_enterprise = evolucao.id_enterprise 
                AND isa_encontro.data_dia = evolucao.dthr_evolucao::date
        LEFT JOIN imparare_patient_company_treatment c 
            ON isa_encontro.registro = c.record_id
                AND c.id_enterprise = isa_encontro.id_enterprise
                AND isa_encontro.data_dia between c.attendance_date AND c.discharge_date + interval '1 day'
    """
    df_iterator = dataRequest.get_data(queryText= append_query)

    with Pool(4) as pool:
        for _ in pool.imap_unordered(worker, df_iterator):
            pass


if __name__ == "__main__":
    main()