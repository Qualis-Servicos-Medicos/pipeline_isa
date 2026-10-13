from ImpararePackage import dataRequest
from ImpararePackage import maestro
import pandas as pd
import threading
from multiprocessing import Pool, cpu_count
import itertools

def worker(c: pd.DataFrame):
    c["id_hospital"] = c["id_hospital"].astype("Int32")
    c = maestro.incrise_by_n_hours(df= c, arrayColumns= ["dthr_criacao", "dthr_procedimento", "dthr_fim_procedimento"], hours= 3)
    c = maestro.remove_columns(df= c, column= "id_cirurgia")
    c = maestro.to_float(df= c, arrayColumns= ["tempo_cirurgia"])

    def elk_upload(c: pd.DataFrame):
        client = dataRequest.ELASTICSEARCH_CONNECTION
       
        c["paciente_id"] = c["patient_id"]
        c = maestro.keep_columns(df= c, arrayColumns= [
            "id",
            "perfil",
            "dthr_criacao",
            "dthr_procedimento",
            "dthr_fim_procedimento",
            "tempo_cirurgia",
            "texto_cirurgia",
            "paciente_id",
            "id_enterprise",
            "nome_medico",
            "nome_procedimentos"
         ])
        actions = maestro.generate_actions(c, "procedimentos")
        maestro.bulk_upload_with_retry(client, actions, context="procedimento", thread_count=1)

    job = threading.Thread(target= elk_upload, args=(c.copy(), ))
    job_3 = threading.Thread(target=dataRequest.set_data_on_sql, args=(c, "isa_procedimento"), kwargs={"if_exists": "append", "isLocal": True})
    
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

    index_name = "procedimentos"
    if maestro.get_must_update_all_patients() == '1':
        create_query = """
            DROP TABLE IF EXISTS isa_procedimento;
            CREATE UNLOGGED TABLE isa_procedimento (
                id TEXT,
                perfil TEXT,
                patient_id INTEGER,
                id_enterprise SMALLINT,
                dthr_criacao DATE,
                dthr_procedimento TIMESTAMP,
                dthr_fim_procedimento TIMESTAMP,
                tempo_cirurgia FLOAT,
                texto_cirurgia TEXT,
                nome_medico TEXT,
                nome_procedimentos TEXT,
                tipo_atendimento TEXT,
                ordem TEXT,
                criterio TEXT,
                id_hospital SMALLINT
            );
        """
        dataRequest.execute(create_query, isLocal= True)
        # dataRequest.execute(create_query, isLocal= False)
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
                    # front busca "procedimentos" por paciente_id (term); demais campos so sao retornados
                    "dynamic": "strict",
                    "properties": {
                        "id": {"type": "keyword", "index": False, "doc_values": False},
                        "perfil": {"type": "keyword", "index": False, "doc_values": False},
                        "dthr_criacao": {"type": "date", "index": False, "doc_values": False},
                        "dthr_procedimento": {"type": "date", "index": False, "doc_values": False},
                        "dthr_fim_procedimento": {"type": "date", "index": False, "doc_values": False},
                        "tempo_cirurgia": {"type": "float", "index": False, "doc_values": False},
                        "texto_cirurgia": {"type": "text", "index": False},
                        "paciente_id": {"type": "integer"},
                        "id_enterprise": {"type": "short"},
                        "nome_medico": {"type": "keyword", "index": False, "doc_values": False},
                        "nome_procedimentos": {"type": "text", "index": False},
                    }
                }
            )
            maestro.wait_for_index_health(client, index_name)

    else:
        # Drop local table
        dataRequest.execute("DELETE FROM isa_procedimento WHERE (patient_id, id_enterprise) in (select distinct record_id, id_enterprise from patients_to_update)", isLocal= True)
        
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
            print(f"Deletados {resp['deleted']} procedimentos do lote de {len(lote)} pacientes. Total deletados até agora: {total}")

        client.indices.refresh(index=index_name)
        print(f"Deletados {total} procedimentos no total para {len(df)} pacientes.")
    
    append_query = """
        SELECT 
            s.patient_id::text || '_' || s.id_enterprise || '_' || s.dthr_procedimento::text || '_' || s.nome_procedimento as id,
            null as perfil,
            s.patient_id:: integer as patient_id,
            s.id_enterprise,
            null::date as dthr_criacao,
            s.dthr_procedimento::timestamp as dthr_procedimento, 
            s.dthr_fim_procedimento::timestamp as dthr_fim_procedimento,
            s.tempo_de_cirurgia:: float as tempo_cirurgia,
            s.texto_cirurgia:: text as texto_cirurgia,
            s.nome_medico:: text as nome_medico,
            s.nome_procedimento:: text as nome_procedimentos,
            null as tipo_atendimento,
            null as ordem,
            null as criterio,
            c.id_hospital
        FROM imparare2_cirurgias_union_gamb s
        LEFT JOIN imparare2_company_code c 
            ON s.patient_id = c.record_id
                AND s.id_enterprise = c.id_enterprise
                AND DATE(s.dthr_procedimento) between DATE(c.attendance_date)
                AND coalesce(c.hospital_discharge_date, (
                    SELECT min(c2.attendance_date)
                    FROM imparare2_company_code c2
                    WHERE c2.record_id = c.record_id AND c2.attendance_id > c.attendance_id
                    GROUP BY c2.record_id 
                ), now()) + INTERVAL '1 day';
    """
    df_iterator = dataRequest.get_data(queryText= append_query)

    with Pool(4) as pool:
        for _ in pool.imap_unordered(worker, df_iterator):
            pass


if __name__ == "__main__":
    main()