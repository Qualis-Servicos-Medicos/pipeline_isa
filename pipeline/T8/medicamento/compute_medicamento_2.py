from ImpararePackage import dataRequest
from ImpararePackage import maestro
import pandas as pd
import threading
from multiprocessing import Pool, cpu_count
import itertools

def worker(c: pd.DataFrame):
    def elk_upload(c: pd.DataFrame):
        client = dataRequest.ELASTICSEARCH_CONNECTION
        c["paciente_id"] = c["patient_id"]
        c = maestro.keep_columns(df= c, arrayColumns= [
            "id",
            "codigo_prescricao",
            "dthr_prescricao",
            "medicamento",
            "dose",
            "unidade",
            "frequencia",
            "via",
            "paciente_id",
            "id_enterprise"
        ])
        actions = maestro.generate_actions(c, "medicamentos")
        maestro.bulk_upload_with_retry(client, actions, context="medicamento", thread_count=1)

    table = "isa_medicamento"
    
    jobs = [
        threading.Thread(target= elk_upload, args=(c.copy(), )), 
        threading.Thread(target=dataRequest.set_data_on_sql, args=(c, table), kwargs={"if_exists": "append", "isLocal": True})
    ]
    for j in jobs:
        j.start()
    
    for j in jobs:
        j.join()


def main():
    client = dataRequest.ELASTICSEARCH_CONNECTION
    print(client.cluster.health())
    print(client.ping())

    index_name = "medicamentos"
    if maestro.get_must_update_all_patients() == '1':
        create_query = """
            DROP TABLE IF EXISTS isa_medicamento;
            CREATE UNLOGGED TABLE isa_medicamento (
                id TEXT,
                patient_id INTEGER,
                id_enterprise SMALLINT,
                codigo_prescricao INTEGER,
                dthr_prescricao TIMESTAMP,
                medicamento TEXT,
                dose TEXT,
                unidade TEXT,
                frequencia TEXT,
                via TEXT,
                tipo_atendimento TEXT,
                ordem TEXT,
                criterio TEXT
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
                            "durability": "async",
                            "sync_interval": "30s"
                        }
                    }
                },
                mappings={
                    # front busca "medicamentos" por paciente_id (term); demais campos so sao retornados
                    "dynamic": "strict",
                    "properties": {
                        "id": {"type": "keyword", "index": False, "doc_values": False},
                        "codigo_prescricao": {"type": "integer", "index": False, "doc_values": False},
                        "dthr_prescricao": {"type": "date", "index": False, "doc_values": False},
                        "medicamento": {"type": "text", "index": False},
                        "dose": {"type": "keyword", "index": False, "doc_values": False},
                        "unidade": {"type": "keyword", "index": False, "doc_values": False},
                        "frequencia": {"type": "keyword", "index": False, "doc_values": False},
                        "via": {"type": "keyword", "index": False, "doc_values": False},
                        "paciente_id": {"type": "integer"},
                        "id_enterprise": {"type": "short"}
                    }
                }
            )
            maestro.wait_for_index_health(client, index_name)
    else:
        # Drop local table
        dataRequest.execute("DELETE FROM isa_medicamento WHERE (patient_id, id_enterprise) in (select distinct record_id, id_enterprise from patients_to_update)", isLocal= True)
        
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
            print(f"Deletados {resp['deleted']} medicamentos do lote de {len(lote)} pacientes. Total deletados até agora: {total}")

        client.indices.refresh(index=index_name)
        print(f"Deletados {total} medicamentos no total para {len(df)} pacientes.")

    append_query= """
       SELECT 
            registro::varchar || '_' || s.id_enterprise::varchar || '_' || dthr_prescricao::varchar || '_' || atb::varchar || '_' || dose::varchar || '_' || attendance_type::varchar  || '_' || unidade::varchar  || '_' || frequencia::varchar  || '_' || via::varchar as id, 
            registro as patient_id, 
            s.id_enterprise,
            null as codigo_prescricao,
            DTHR_PRESCRICAO as dthr_prescricao, 
            atb as medicamento,
            dose,
            unidade,
            frequencia,
            via,
            attendance_type as tipo_atendimento,
            null as ordem,
            null as criterio
        FROM imparare2_prescricoesantibiotico_prepared s;
    """
    df_iterator = dataRequest.get_data(queryText= append_query)

    with Pool(4) as pool:
        for _ in pool.imap_unordered(worker, df_iterator):
            pass

if __name__ == "__main__":
    main()