from ImpararePackage import dataRequest
from ImpararePackage import maestro
from multiprocessing import Pool, cpu_count
import itertools
from worker_compute_exame import main as worker

def main():
    client = dataRequest.ELASTICSEARCH_CONNECTION
    print(client.cluster.health())
    print(client.ping())

    index_name = "exames"
    if maestro.get_must_update_all_patients() == '1':
        create_query = """
            DROP TABLE IF EXISTS isa_exame;
            CREATE UNLOGGED TABLE isa_exame (
                id TEXT,
                patient_id INTEGER,
                id_enterprise SMALLINT,
                exame TEXT,
                item_exame TEXT,
                dthr_pedido TIMESTAMP,
                dthr_entrega TIMESTAMP,
                resultado TEXT,
                tipo_atendimento TEXT,
                ordem_amostra TEXT,
                data_assinatura TIMESTAMP,
                ordem TEXT,
                criterio TEXT,
                gmr TEXT,
                positivo TEXT,
                pcr_covid TEXT,
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
                    # front busca "exames" por paciente_id (term); demais campos so sao retornados
                    "dynamic": "strict",
                    "properties": {
                        "id": {"type": "keyword", "index": False, "doc_values": False},
                        "exame": {"type": "text", "index": False},
                        "item_exame": {"type": "text", "index": False},
                        "dthr_pedido": {"type": "date", "index": False, "doc_values": False},
                        "dthr_entrega": {"type": "date", "index": False, "doc_values": False},
                        "resultado": {"type": "text", "index": False},
                        "positivo": {"type": "keyword", "index": False, "doc_values": False},
                        "ordem": {"type": "keyword", "index": False, "doc_values": False},
                        "criterio": {"type": "keyword", "index": False, "doc_values": False},
                        "gmr": {"type": "keyword", "index": False, "doc_values": False},
                        "paciente_id": {"type": "integer"},
                        "id_enterprise": {"type": "short"}
                    }
                }
            )
            maestro.wait_for_index_health(client, index_name)
    else:
        # Drop local table
        dataRequest.execute("DELETE FROM isa_exame WHERE (patient_id, id_enterprise) in (select distinct record_id, id_enterprise from patients_to_update)", isLocal= True)

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
            print(f"Deletados {resp['deleted']} exames do lote de {len(lote)} pacientes. Total deletados até agora: {total}")
        client.indices.refresh(index=index_name)
        print(f"Deletados {total} exames no total para {len(df)} pacientes.")
    
    append_query = """
        SELECT 
            s.id,
            s.registro as patient_id,
            s.id_enterprise,
            s.exame,
            s.item_exame,
            s.dthr_pedido,
            s.dthr_entrega,
            s.ds_resultado as resultado,
            s.tipo_atendimento,
            null as ordem_amostra,
            null as data_assinatura,
            null as ordem,
            null as criterio,
            null as gmr,
            null as positivo,
            null as pcr_covid,
            c.id_hospital
        FROM imparare2_exameslaboratorio_followup_stacked s
        LEFT JOIN imparare2_company_code c 
            ON s.registro = c.record_id
                AND s.id_enterprise = c.id_enterprise
                AND DATE(s.dthr_pedido) between DATE(c.attendance_date)
                AND coalesce(c.hospital_discharge_date, (
                    SELECT min(c2.attendance_date)
                    FROM imparare2_company_code c2
                    WHERE c2.record_id = c.record_id AND c2.attendance_id > c.attendance_id
                    GROUP BY c2.record_id 
                ), now()) + INTERVAL '1 day'
        WHERE s.ds_resultado is not null;
    """

    df_iterator = dataRequest.get_data(queryText= append_query)

    with Pool(8) as pool:
        for _ in pool.imap_unordered(worker, df_iterator):
            pass

if __name__ == "__main__":
    main()
