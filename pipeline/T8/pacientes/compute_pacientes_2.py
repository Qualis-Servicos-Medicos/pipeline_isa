from ImpararePackage import dataRequest
from ImpararePackage import maestro
import pandas as pd
import threading
from multiprocessing import Pool, cpu_count
import itertools

def worker(c: pd.DataFrame):

    novosNomes = {
        "registro": "id",
        "dt_nascimento_parsed": "dt_nascimento",
    }
    c = maestro.rename_columns(df= c, DictColumns= novosNomes)
        
    tuplas = [("NA", "Não Identificado")]
    c = maestro.replace_values_list(df= c, column= "nome", arrayDeTuplas= tuplas, exect= True)

    c["nome"] = c.apply(lambda x: str(x["id"]) if(x["id"] == "Não Identificado") else str(x["id"]) + " - " + str(x["nome"]), axis= 1)
        
    # c = maestro.incrise_by_n_hours(df= c, column= "dt_nascimento", hours= 3)

    def elk_upload(c: pd.DataFrame):
        client = dataRequest.ELASTICSEARCH_CONNECTION
        c = maestro.keep_columns(df= c, arrayColumns= [
            "id",
            "id_enterprise",
            "sexo",
            "dt_nascimento",
            "idade_hoje",
            "nome"
         ])
        actions = maestro.generate_actions(c, "pacientes")
        maestro.bulk_upload_with_retry(client, actions, context="pacientes", thread_count=1)
    
    table = "isa_pacientes"
    job = threading.Thread(target= elk_upload, args=(c.copy(), ))
    # job_2 = threading.Thread(target=dataRequest.set_data_on_sql, args=(c, table), kwargs={"if_exists": "append", "isLocal": False})
    job_3 = threading.Thread(target=dataRequest.set_data_on_sql, args=(c, table), kwargs={"if_exists": "append", "isLocal": True})
    
    jobs = [
        job, 
        #job_2, 
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

    index_name = "pacientes"
    if maestro.get_must_update_all_patients() == '1':
        create_query = """
            DROP TABLE IF EXISTS isa_pacientes;
            CREATE UNLOGGED TABLE isa_pacientes (
                id INTEGER,
                id_enterprise SMALLINT,
                nome TEXT,
                dt_nascimento TIMESTAMP,
                sexo TEXT,
                idade_hoje smallint,
                idade_dias_hoje int4,
                id_hospital SMALLINT
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
                }
            )
            maestro.wait_for_index_health(client, index_name)
    else:
        # Drop local table
        dataRequest.execute("DELETE FROM isa_pacientes WHERE (id, id_enterprise) in (select distinct record_id, id_enterprise from patients_to_update)", isLocal= True)
        
        #Busca IDS para deleção
        df = dataRequest.get_data(queryText= f"SELECT distinct record_id::text, id_enterprise FROM patients_to_update", chunck= None)

        # Drop Banco aws
        ids = ""
        for i in range(len(df)):
            ids += f"({df.iloc[i]['record_id']}, {df.iloc[i]['id_enterprise']}),"
        ids = ids.strip(",")
        dataRequest.execute(f"DELETE FROM isa_pacientes WHERE (id, id_enterprise) in ({ids})", isLocal= False)

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
            print(f"Deletados {resp['deleted']} pacientes do lote de {len(lote)} pacientes. Total deletados até agora: {total}")

        client.indices.refresh(index=index_name)
        print(f"Deletados {total} pacientes no total para {len(df)} pacientes.")

    append_query = """ 
        WITH s AS (
            SELECT DISTINCT         
                I.registro, 
                I.id_enterprise,
                I.sexo, 
                I.dt_nascimento_parsed,
                EXTRACT(YEAR FROM AGE(date_trunc('day', ld.dia), I.dt_nascimento_parsed))::smallint AS idade_hoje,
                date(ld.dia) - date(I.dt_nascimento_parsed) AS idade_dias_hoje,
                pr.patient_name as nome,
                pr.id_hospital
            FROM imparare2_pacientes_prepared as I
            INNER JOIN (
                select
                    prontuario,
                    id_enterprise,
                    max(dia) as dia
                FROM imparare2_dataset_label_full
                GROUP BY prontuario, id_enterprise
            ) ld
                ON ld.prontuario = I.registro
                	and ld.id_enterprise = i.id_enterprise                   
            LEFT JOIN (
	            select 
	            	pr.*, 
	            	h.id_enterprise, 
	            	row_number() over(partition by h.id_enterprise, pr.record_id order by created_at desc) as rn 
	        	from patients_records pr
	        	inner join hospitals h
	        		on pr.id_hospital = h.id_hospital
            ) as pr
            	ON I.registro = pr."record_id"
            		and pr.id_enterprise = i.id_enterprise 
            		and pr.rn = 1
        )
        SELECT DISTINCT
            s.*
        FROM s;
    """

    df_iterator = dataRequest.get_data(queryText= append_query)

    with Pool(4) as pool:
        for _ in pool.imap_unordered(worker, df_iterator):
            pass
        

if __name__ == "__main__":
    main()