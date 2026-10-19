from ImpararePackage import maestro
from ImpararePackage import dataRequest
import unicodedata
import pandas as pd
from multiprocessing import Pool
import threading
import itertools

# Esta função recebe uma STRING e retorna uma STRING sem acentos
def worker (c: pd.DataFrame):
    def remove_accents(input_str):
        if not isinstance(input_str, str):
            return input_str  # Or you can choose to return an empty string or handle differently
        # Normalize the input string using NFD decomposition
        if input_str is not None:
            nfkd_form = unicodedata.normalize('NFD', input_str)
            # Filter out the non-spacing marks
            return ''.join(c for c in nfkd_form if unicodedata.category(c) != 'Mn')
        else:
            return ''
        
    c['laudo_texto'] = c['laudo_texto'].apply(remove_accents)

    def elk_upload(c: pd.DataFrame):
        client = dataRequest.ELASTICSEARCH_CONNECTION
        c["paciente_id"] = c["patient_id"]
        c = maestro.keep_columns(df= c, arrayColumns= [
            "id",
            "codigo_laudo",
            "descricao_laudo",
            "dthr_pedido",
            "dthr_entrega_laudo",
            "laudo_texto",
            "ordem",
            "criterio",
            "paciente_id",
            "id_enterprise",
        ])
        actions = maestro.generate_actions(c, "laudos")
        maestro.bulk_upload_with_retry(client, actions, context="laudo", thread_count=1)

    table = "isa_laudo"
    job = threading.Thread(target= elk_upload, args=(c.copy(), ))
    job_3 = threading.Thread(target=dataRequest.set_data_on_sql, args=(c, table), kwargs={"if_exists": "append", "isLocal": True})
    
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

    index_name = "laudos"
    if maestro.get_must_update_all_patients() == '1':
        create_query = """
            DROP TABLE IF EXISTS isa_laudo;
            CREATE UNLOGGED TABLE isa_laudo (
                id TEXT,
                patient_id INTEGER,
                id_enterprise SMALLINT,
                codigo_laudo INTEGER,
                descricao_laudo TEXT,
                dthr_pedido TIMESTAMP,
                dthr_entrega_laudo TIMESTAMP,
                laudo_texto TEXT,
                tipo_atendimento TEXT,
                ordem TEXT,
                criterio TEXT,
                id_hospital SMALLINT
            );
        """
        dataRequest.execute(create_query, isLocal= False)
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
                            "durability": "async",
                            "sync_interval": "30s"
                        }
                    }
                },
                mappings={
                    # front busca "laudos" por paciente_id (term); demais campos so sao retornados
                    "dynamic": "strict",
                    "properties": {
                        "id": {"type": "keyword", "index": False, "doc_values": False},
                        "codigo_laudo": {"type": "integer", "index": False, "doc_values": False},
                        "descricao_laudo": {"type": "keyword", "index": False, "doc_values": False},
                        "dthr_pedido": {"type": "date", "index": False, "doc_values": False},
                        "dthr_entrega_laudo": {"type": "date", "index": False, "doc_values": False},
                        "laudo_texto": {"type": "text", "index": False},
                        "ordem": {"type": "keyword", "index": False, "doc_values": False},
                        "criterio": {"type": "keyword", "index": False, "doc_values": False},
                        "paciente_id": {"type": "integer"},
                        "id_enterprise": {"type": "short"}
                    }
                }
            )
            maestro.wait_for_index_health(client, index_name)

    else:
        # Drop local table
        dataRequest.execute("DELETE FROM isa_laudo WHERE (patient_id, id_enterprise) in (select distinct record_id, id_enterprise from patients_to_update)", isLocal= True)
        
        #Busca IDS para deleção
        df = dataRequest.get_data(queryText= f"SELECT distinct record_id, id_enterprise FROM patients_to_update", chunck= None)
        
        # Drop ELK index
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
            print(f"Deletados {resp['deleted']} laudos do lote de {len(lote)} pacientes. Total deletados até agora: {total}")

        client.indices.refresh(index=index_name)
        print(f"Deletados {total} laudos no total para {len(df)} pacientes.")

    append_query = """
        SELECT 
            xr.xray_request_date::varchar || '_' || h.id_enterprise::varchar || '_' || xr.xray_delivery_date::varchar || '_' || xr.record_id::varchar || '_' || xr.xray_exam_description::varchar || '_' || xr.attendance_type::varchar as id, 
            xr.record_id as patient_id,
            h.id_enterprise,
            null as codigo_laudo, 
            xr.xray_exam_description as descricao_laudo, 
            xr.xray_request_date as dthr_pedido, 
            xr.xray_delivery_date as dthr_entrega_laudo, 
            LOWER(xr.xray_content::text) as laudo_texto, 
            xr.attendance_type as tipo_atendimento, 
            null as ordem, 
            null as criterio,
            h.id_hospital
        FROM xrays_reports xr
		inner join hospitals h
		    on h.id_hospital = xr.id_hospital;
    """
    
    df_iterator = dataRequest.get_data(queryText= append_query)

    with Pool(processes= 4) as pool:
        for _ in pool.imap_unordered(worker, df_iterator):
            pass

if __name__ == "__main__":
    main()