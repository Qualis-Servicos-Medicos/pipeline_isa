from ImpararePackage import dataRequest
from ImpararePackage import maestro
import pandas as pd
from multiprocessing import Pool, cpu_count

def process_chunck(c: pd.DataFrame):
    objects = []
    c['aval_dt_infec'] = pd.to_datetime(c['aval_dt_infec'])
    
    for i in c.index:
        row = c.iloc[i]
        infeccao = row['tipo_infeccao']
        outra_infec = row['outra_infec']
        dt_infeccao = row['aval_dt_infec']
        paciente_id = row['paciente_id']
        id_enterprise = row['id_enterprise']

        if infeccao == 'sem infecção':
            for j in range(1, 4):
                objects.append({
                    "registro": paciente_id,
                    "id_enterprise": id_enterprise,
                    "dt_infeccao": dt_infeccao + pd.Timedelta(days= j),
                    "tipo_infeccao": infeccao
                })
                objects.append({
                    "registro": paciente_id,
                    "id_enterprise": id_enterprise,
                    "dt_infeccao": dt_infeccao - pd.Timedelta(days= j),
                    "tipo_infeccao": infeccao
                })

            objects.append({
                "registro": paciente_id,
                "id_enterprise": id_enterprise,
                "dt_infeccao": dt_infeccao,
                "tipo_infeccao": infeccao
            })
        else:
            for j in range(7): 
                objects.append({
                    "registro": paciente_id,
                    "id_enterprise": id_enterprise,
                    "dt_infeccao": dt_infeccao + pd.Timedelta(days= j),
                    "tipo_infeccao": infeccao if infeccao != 'outra' else outra_infec
                })
    
    df = pd.DataFrame(objects)

    df_encoded = pd.get_dummies(df, columns=['tipo_infeccao'], prefix= "", prefix_sep= "")
    if 'sem infecção' not in df_encoded.columns:
        df_encoded['sem infecção'] = False

    df_encoded['caso infeccao'] = df_encoded['sem infecção'].apply(lambda x: False if x else True)
    print(df_encoded['caso infeccao'].value_counts())
    if 'comunitaria' not in df_encoded.columns:
        df_encoded['comunitaria'] = False
    
    df_encoded['caso infeccao hospitalar'] = df_encoded.apply(lambda x: x['caso infeccao'] and not x['comunitaria'], axis= 1)
    
    dataRequest.set_data_on_sql(df= df_encoded, nomeTabelaDestino= "new_avaliacao_padrao_ouro", if_exists= "append")

def main():
    case_nomes_outra_infec = """
        CASE
            WHEN TRIM(ia.outra_infec) = 'enterocolite' THEN 'Enterocolite'
            WHEN TRIM(ia.outra_infec) = 'Infecção da cavidade oral' THEN 'Infecção de cavidade oral'
            ELSE ia.outra_infec
        END
    """
    unique_infeccoes_query = f"""
        SELECT 
            distinct
            case when tipo_infeccao = 'outra' then {case_nomes_outra_infec} 
                else tipo_infeccao end as tipo_infeccao
        FROM isa_avaliacao ia
        -- WHERE ia.avaliacao_responsavel = 'stephani_materdei_hmg'
        order by tipo_infeccao
    """
    df_unique_infeccoes = dataRequest.get_data(queryText= unique_infeccoes_query, isLocal= False, chunck= None)
    infections = df_unique_infeccoes['tipo_infeccao'].unique().tolist()

    create_query = """
        DROP TABLE IF EXISTS new_avaliacao_padrao_ouro;
        CREATE UNLOGGED TABLE new_avaliacao_padrao_ouro (
            registro INTEGER,
            id_enterprise SMALLINT,
            dt_infeccao DATE,
            "caso infeccao" BOOLEAN DEFAULT FALSE,
            "caso infeccao hospitalar" BOOLEAN DEFAULT FALSE,
    """
    for infection in infections:
        create_query += f'"{infection}" BOOLEAN DEFAULT FALSE, \n'
    create_query = create_query.strip(', \n')
    create_query += ");"
    dataRequest.execute(create_query)
    
    query_get_avaliacoes = f"""
        SELECT 
            distinct
            ia.paciente_id, 
            ia.aval_dt_infec::DATE,
            ia.tipo_infeccao,
            {case_nomes_outra_infec} as outra_infec,
            h.id_enterprise
        FROM isa_avaliacao ia
        INNER JOIN hospital h
            ON ia.id_hospital = h.id_hospital
        WHERE ia.avaliacao_responsavel != 'stephani_hmg_2'
            and ia.avaliacao_data < '2026-10-25'
        order by tipo_infeccao
    """
    df = dataRequest.get_data(queryText= query_get_avaliacoes, isLocal= False)
    
    with Pool(cpu_count()) as pool:
        for _ in pool.imap_unordered(process_chunck, df):
            pass
    
if __name__ == "__main__":
    main()