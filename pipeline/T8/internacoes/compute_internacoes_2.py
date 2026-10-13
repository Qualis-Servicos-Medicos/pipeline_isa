from multiprocessing.pool import Pool
from ImpararePackage import dataRequest
from ImpararePackage import maestro
import pandas as pd


def worker(c = pd.DataFrame):
    #c, pos = args
    c = maestro.remove_columns(df= c, arrayColumns= ["tipo_intern", "tipo_clinica", "especialidade", "unidade", "nmconvenio"])

    c = maestro.fillnan(df= c, arrayColumns=["alta", "los"],arraySubstitui=["Ainda internado ou não consta no sistema", "-1"])

    novosNomes = {
        "registro": "paciente_id",
        "alta": "tipo_alta",
        "dthr_alta": "dthr_alta",
        "los": "tempo_estadia",
        "dthr_atendimento": "dthr_atendimento",
        "cd_atendimento": "cd_atendimento"
    }
    c = maestro.rename_columns(df= c, DictColumns= novosNomes)

    # Salvando no remoto
    # dataRequest.set_data_on_sql(df= c, nomeTabelaDestino= "isa_internacoes", isLocal=  False, if_exists= "append")
    # Salvando no local
    dataRequest.set_data_on_sql(df= c, nomeTabelaDestino= "isa_internacoes", isLocal=  True, if_exists= "append")


def main():
    if maestro.get_must_update_all_patients() == '1':
        create_query = """
            DROP TABLE IF EXISTS isa_internacoes;
            CREATE UNLOGGED TABLE isa_internacoes (
                id TEXT,
                paciente_id INTEGER,
                id_enterprise SMALLINT,
                cd_atendimento INTEGER,
                dthr_atendimento TIMESTAMP,
                dthr_alta TIMESTAMP,
                tipo_alta TEXT,
                tempo_estadia INTEGER
            );
        """
        dataRequest.execute(create_query, isLocal= True)
        # dataRequest.execute(create_query, isLocal= False)
    else:
        # Drop local table
        dataRequest.execute("DELETE FROM isa_internacoes WHERE (paciente_id, id_enterprise) in (select distinct record_id, id_enterprise from patients_to_update)", isLocal= True)
        
        #Busca IDS para deleção
        df = dataRequest.get_data(queryText= f"SELECT distinct record_id::text, id_enterprise FROM patients_to_update", chunck= None)

        # Drop Banco aws
        ids = ""
        for i in range(len(df)):
            ids += f"({df.iloc[i]['record_id']}, {df.iloc[i]['id_enterprise']}),"
        ids = ids.strip(",")
        dataRequest.execute(f"DELETE FROM isa_internacoes WHERE (paciente_id, id_enterprise) in ({ids})", isLocal= False)

    append_query = """
        SELECT DISTINCT
            s.registro::text || '_' || s.id_enterprise::text || '_' || s.cd_atendimento::text as id,
            s.*
        FROM imparare2_internacoes_v2_stacked_by_cd_atendimento s
    """
    df_iterator = dataRequest.get_data(queryText= append_query, chunck= 2000)

    with Pool(processes= 4) as pool:
        for _ in pool.imap_unordered(worker, df_iterator):
            pass

    

if __name__ == "__main__":
    main()