from ImpararePackage import maestro
from ImpararePackage import dataRequest
from multiprocessing import Pool, cpu_count
import itertools
from worker_compute_sinal_vital_2 import main as worker


def main():
    client = dataRequest.ELASTICSEARCH_CONNECTION
    print(client.cluster.health())
    print(client.ping())

    index_name = "sinais-vitais"

    if maestro.get_must_update_all_patients() == "1": 
        create_query = """
            DROP TABLE IF EXISTS isa_sinal_vital;
            CREATE UNLOGGED TABLE isa_sinal_vital (
                id TEXT,
                paciente_id INTEGER,
                id_enterprise SMALLINT,
                tipo_sinal TEXT,
                dthr_coleta TIMESTAMP,
                valor TEXT,
                unimedida TEXT,
                perfil TEXT,
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
                    # front busca "sinais-vitais" por paciente_id (term); demais campos so sao retornados
                    "dynamic": "strict",
                    "properties": {
                        "id": {"type": "keyword", "index": False, "doc_values": False},
                        "paciente_id": {"type": "integer"},
                        "id_enterprise": {"type": "short"},
                        "tipo_sinal": {"type": "keyword", "index": False, "doc_values": False},
                        "dthr_coleta": {"type": "date", "index": False, "doc_values": False},
                        "valor": {"type": "keyword", "index": False, "doc_values": False},
                        "unimedida": {"type": "keyword", "index": False, "doc_values": False},
                        "perfil": {"type": "keyword", "index": False, "doc_values": False},
                        "ordem": {"type": "keyword", "index": False, "doc_values": False},
                        "criterio": {"type": "keyword", "index": False, "doc_values": False},
                    }
                }
            )
            maestro.wait_for_index_health(client, index_name)
    else:
        # Drop local table
        dataRequest.execute("DELETE FROM isa_sinal_vital WHERE (paciente_id, id_enterprise) in (select distinct record_id, id_enterprise from patients_to_update)", isLocal= True)
        
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
            print(f"Deletados {resp['deleted']} sinais vitais do lote de {len(lote)} pacientes. Total deletados até agora: {total}")

        client.indices.refresh(index=index_name)
        print(f"Deletados {total} sinais vitais no total para {len(df)} pacientes.")

    createMidTables = f"""
        drop table if exists mid_isa_sinais_vitais;
        create unlogged table mid_isa_sinais_vitais as (
            SELECT 
                registro::varchar|| '_' ||dthr_coleta::varchar|| '_' ||tipo_registro::varchar|| '_' ||valor_medida::varchar|| '_' ||perfil::varchar|| '_' ||uni_medida::varchar|| '_' ||s.id_enterprise::varchar as id, 
                s.registro as paciente_id, 
                s.tipo_registro as tipo_sinal,
                date(s.dthr_coleta) as dthr_coleta,
                s.valor_medida as valor,
                s.uni_medida as unimedida,
                null as perfil,
                null as tipo_atendimento,
                null as ordem,
                null as criterio,
                s.id_enterprise,
                c.id_hospital
            FROM imparare2_isa_sinal_vital s
            LEFT JOIN imparare2_company_code c 
                ON s.registro = c.record_id
                AND s.id_enterprise = c.id_enterprise
                AND DATE(s.dthr_coleta) between DATE(c.attendance_date)
                AND coalesce(c.hospital_discharge_date, (
                    SELECT min(c2.attendance_date)
                    FROM imparare2_company_code c2
                    WHERE c2.record_id = c.record_id AND c2.attendance_id > c.attendance_id
                    GROUP BY c2.record_id 
                ), now()) + INTERVAL '1 day'
            where s.tipo_registro in (
                'OXIGÊNIO (L/MIN)', 'O2',
                'FIO2 %', 'FIO2', 
                'SAT.O2 %', 'OXIMETRIA', 'ST',
                'F.C.', 'FC',
                'F.R.', 'FR', 
                'PA.', 'PA',
                'P.A.M', 'PAM', 
                'P.A. DIASTOLICA', 'PAD', 'P.A.D.',
                'P.A.S.', 'PAS',
                'TEMP.', 'TEMP', 'TEM',
                'PEWS FC ACORDADO', 'PEWS FC DORMINDO',
                'PEEP',
                'PESO (KG)', 'PESO',
                'GLICEMIA CAPILAR',
                'ECG (GLASGOW)',
                'BCF'
            )
        );
        
        create index idx_mid_isa_sinais_vitais on mid_isa_sinais_vitais(paciente_id, tipo_sinal, dthr_coleta, valor);

        drop table if exists isa_sinais_vitais_paciente_valor;
        create unlogged table isa_sinais_vitais_paciente_valor as (
            select
                paciente_id,
                id_enterprise,
                id_hospital,
                tipo_sinal,
                dthr_coleta,
                min(valor) valor_baixo,
                max(valor) valor_alto
            from mid_isa_sinais_vitais
            where valor is not null
            group by paciente_id, id_enterprise, id_hospital, tipo_sinal, dthr_coleta
        );
        create index idx_isa_sinais_vitais_paciente_valor on isa_sinais_vitais_paciente_valor(paciente_id, id_enterprise, id_hospital, tipo_sinal, dthr_coleta, valor_baixo, valor_alto);
    """
    dataRequest.execute(createMidTables, isLocal= True)

    append_query = """
    select 
        distinct on (a.paciente_id, a.id_enterprise, a.id_hospital, a.tipo_sinal, a.dthr_coleta, a.valor)
        a.*
    from (
        select 
            distinct on (isv.paciente_id, isv.id_enterprise, isv.id_hospital, isv.tipo_sinal, isv.dthr_coleta, isv.valor)
            isv.* 
        from mid_isa_sinais_vitais isv
        join isa_sinais_vitais_paciente_valor isvpv
            on isv.paciente_id = isvpv.paciente_id
            and isv.id_enterprise = isvpv.id_enterprise
            and isv.id_hospital = isvpv.id_hospital
            and isv.tipo_sinal = isvpv.tipo_sinal
            and isv.dthr_coleta = isvpv.dthr_coleta
        where isv.valor = isvpv.valor_baixo
        union all
        select 
            distinct on (isv.paciente_id, isv.id_enterprise, isv.id_hospital, isv.tipo_sinal, isv.dthr_coleta, isv.valor)
            isv.* 
        from mid_isa_sinais_vitais isv
        join isa_sinais_vitais_paciente_valor isvpv
            on isv.paciente_id = isvpv.paciente_id
            and isv.id_enterprise = isvpv.id_enterprise
            and isv.id_hospital = isvpv.id_hospital
            and isv.tipo_sinal = isvpv.tipo_sinal
            and isv.dthr_coleta = isvpv.dthr_coleta
        where isv.valor = isvpv.valor_alto
            and isvpv.valor_alto != isvpv.valor_baixo
    ) a;
    """

    df_iterator = dataRequest.get_data(queryText= append_query)

    with Pool(8) as pool:
        for _ in pool.imap_unordered(worker, df_iterator):
            pass

if __name__ == "__main__":
    main()