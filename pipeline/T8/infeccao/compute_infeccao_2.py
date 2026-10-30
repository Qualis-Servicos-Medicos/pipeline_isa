from ImpararePackage import dataRequest
from ImpararePackage import maestro
import pandas as pd
import threading
from multiprocessing import Pool, cpu_count
import itertools

def worker(c: pd.DataFrame):
    def elk_upload(c: pd.DataFrame):
        client = dataRequest.ELASTICSEARCH_CONNECTION
        c = maestro.keep_columns(df= c, arrayColumns= [
            "id",
            "paciente_id",
            "id_enterprise",
            "id_hospital",
            "dt_infeccao",
            "prob_perc",
            "prob_perc_pnm",
            "pred_pnm",
            "prob_perc_traqueo",
            "pred_traqueo",
            "prob_perc_pav",
            "pred_pav",
            "prob_perc_itu",
            "pred_itu",
            "prob_perc_isc",
            "pred_isc",
            "prob_perc_ipcs",
            "pred_ipcs",
            "prob_perc_comunitaria",
            "pred_comunitaria",
            "prob_perc_iras",
            "pred_iras",
            "dt_inicio",
            "dt_fim"
        ])
        actions = maestro.generate_actions(c, "infeccoes")
        maestro.bulk_upload_with_retry(client, actions, context="infeccao", thread_count=1)

    table = "isa_infeccao"
    job = threading.Thread(target= elk_upload, args=(c.copy(), ))
    job_2 = threading.Thread(target=dataRequest.set_data_on_sql, args=(c, table), kwargs={"if_exists": "append", "isLocal": False})
    job_3 = threading.Thread(target=dataRequest.set_data_on_sql, args=(c, table), kwargs={"if_exists": "append", "isLocal": True})
    
    jobs = [
        job, 
        job_2, 
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

    index_name = "infeccoes"

    if maestro.get_must_update_all_patients() == '1':
        create_query = """
            DROP TABLE IF EXISTS isa_infeccao;
            CREATE UNLOGGED TABLE isa_infeccao (
                id TEXT,
                paciente_id INTEGER,
                id_enterprise SMALLINT,
                id_hospital SMALLINT,
                dt_infeccao TIMESTAMP,
                prob_perc FLOAT4,
                prob_perc_pnm FLOAT4,
                pred_pnm INTEGER,
                prob_perc_traqueo FLOAT4,
                pred_traqueo INTEGER,
                prob_perc_pav FLOAT4,
                pred_pav INTEGER,
                prob_perc_itu FLOAT4,
                pred_itu INTEGER,
                prob_perc_isc FLOAT4,
                pred_isc INTEGER,
                prob_perc_ipcs FLOAT4,
                pred_ipcs INTEGER,
                prob_perc_comunitaria FLOAT4,
                pred_comunitaria INTEGER,
                prob_perc_iras FLOAT4,
                pred_iras INTEGER,
                dt_inicio TIMESTAMP,
                dt_fim TIMESTAMP,
                company_code TEXT,
                company_id TEXT
            );
        """
        dataRequest.execute(create_query, isLocal= True)
        dataRequest.execute(create_query, isLocal= False)
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
                    # front busca "infeccoes" por paciente_id (term); demais campos so sao retornados
                    "dynamic": "strict",
                    "properties": {
                        "id": {"type": "keyword", "index": False, "doc_values": False},
                        "paciente_id": {"type": "integer"},
                        "id_enterprise": {"type": "short"},
                        "id_hospital": {"type": "short", "index": False, "doc_values": False},
                        "dt_infeccao": {"type": "date", "index": False, "doc_values": False},
                        "prob_perc": {"type": "float", "index": False, "doc_values": False},
                        "prob_perc_pnm": {"type": "float", "index": False, "doc_values": False},
                        "pred_pnm": {"type": "integer", "index": False, "doc_values": False},
                        "prob_perc_traqueo": {"type": "float", "index": False, "doc_values": False},
                        "pred_traqueo": {"type": "integer", "index": False, "doc_values": False},
                        "prob_perc_pav": {"type": "float", "index": False, "doc_values": False},
                        "pred_pav": {"type": "integer", "index": False, "doc_values": False},
                        "prob_perc_itu": {"type": "float", "index": False, "doc_values": False},
                        "pred_itu": {"type": "integer", "index": False, "doc_values": False},
                        "prob_perc_isc": {"type": "float", "index": False, "doc_values": False},
                        "pred_isc": {"type": "integer", "index": False, "doc_values": False},
                        "prob_perc_ipcs": {"type": "float", "index": False, "doc_values": False},
                        "pred_ipcs": {"type": "integer", "index": False, "doc_values": False},
                        "prob_perc_comunitaria": {"type": "float", "index": False, "doc_values": False},
                        "pred_comunitaria": {"type": "integer", "index": False, "doc_values": False},
                        "prob_perc_iras": {"type": "float", "index": False, "doc_values": False},
                        "pred_iras": {"type": "integer", "index": False, "doc_values": False},
                        "dt_inicio": {"type": "date", "index": False, "doc_values": False},
                        "dt_fim": {"type": "date", "index": False, "doc_values": False},
                    }
                }
            )
            maestro.wait_for_index_health(client, index_name)
    else:
        # Drop local table
        dataRequest.execute("DELETE FROM isa_infeccao WHERE (paciente_id, id_enterprise) in (select distinct record_id, id_enterprise from patients_to_update)", isLocal= True)
        
        #Busca IDS para deleção
        df = dataRequest.get_data(queryText= f"SELECT distinct record_id::text, id_enterprise FROM patients_to_update", chunck= None)

        ids = ""
        for i in range(len(df)):
            ids += f"({df.iloc[i]['record_id']}, {df.iloc[i]['id_enterprise']}),"
        ids = ids.strip(",")
        # Drop Banco aws
        dataRequest.execute(f"DELETE FROM isa_infeccao WHERE (paciente_id, id_enterprise) in ({ids})", isLocal= False)

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
            print(f"Deletados {resp['deleted']} infeccao do lote de {len(lote)} pacientes. Total deletados até agora: {total}")
        
        client.indices.refresh(index=index_name)
        print(f"Deletados {total} infeccao no total para {len(df)} pacientes.")


    append_query = """
        SELECT 
            id, 
            paciente_id, 
            s.id_enterprise,
            to_timestamp(dt_infeccao::text || ' 00:00:00', 'YYYY-MM-DD hh24:mi:ss')::timestamp as dt_infeccao, 
            prob_perc, 
            prob_perc_pnm, 
            pred_pnm, 
            prob_perc_traqueo, 
            pred_traqueo, 
            prob_perc_pav, 
            pred_pav, 
            prob_perc_itu, 
            pred_itu, 
            prob_perc_isc, 
            pred_isc, 
            prob_perc_ipcs, 
            pred_ipcs, 
            prob_perc_comunitaria,
            pred_comunitaria,
            prob_perc_iras,
            pred_iras,
            to_timestamp(dt_inicio::text || ' 00:00:00', 'YYYY-MM-DD hh24:mi:ss')::timestamp as dt_inicio, 
            to_timestamp(dt_fim::text || ' 00:00:00', 'YYYY-MM-DD hh24:mi:ss')::timestamp as dt_fim,
            c.id_hospital
        FROM imparare2_isa_infeccao_v2 s
        INNER JOIN imparare_patient_company_treatment c 
            ON s.paciente_id = c.record_id
	            AND s.id_enterprise = c.id_enterprise 
	            AND s.dt_infeccao BETWEEN c.attendance_date AND c.discharge_date + INTERVAL '1 DAY';
    """
    
    df_iterator = dataRequest.get_data(queryText= append_query)

    with Pool(4) as pool:
        for _ in pool.imap_unordered(worker, df_iterator):
            pass



if __name__ == "__main__":
    main()