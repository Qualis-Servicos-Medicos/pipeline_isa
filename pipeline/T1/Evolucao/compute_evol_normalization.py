from ImpararePackage import dataRequest
from ImpararePackage import maestro
import pandas as pd
from multiprocessing import Pool, cpu_count

def worker(c:pd.DataFrame):
    
    # Limpeza de marcadores tipo ( a ), ( b )
    c["new_sentence"] = c["sentence_original"].str.replace(r"\(\s*\w\s*\)", "", regex=True)
    
    # Normalização Maestro
    c = maestro.trim(df=c, column="new_sentence")

    tuplas = [
        (r"\r|\n", ". "),
        (r"\s+", " "),
    ]
    c = maestro.replace_values_list(df=c, arrayDeTuplas=tuplas, column="new_sentence", regex=True)
    c = maestro.normalize(df=c, column="new_sentence")

    # --- SALVAMENTO ---
    dataRequest.set_data_on_sql(df=c, nomeTabelaDestino="imparare2_evolucao_anon_data_trunc", if_exists="append")

def main():
    replace =True

    if replace:
        create_query = """
            DROP TABLE if exists imparare2_evolucao_anon_data_trunc;

            CREATE UNLOGGED TABLE imparare2_evolucao_anon_data_trunc (
                registro INTEGER NULL,
                perfil TEXT NULL,
                unidade TEXT NULL,
                sentence_original TEXT NULL,
                new_sentence TEXT NULL,
                tipo_atendimento TEXT NULL,
                dthr_evolucao TIMESTAMP NULL,
                data_dia DATE NULL,
                id_enterprise INTEGER NULL
            );

            CREATE INDEX IF NOT EXISTS imparare2_evolucao_anon_data_trunc_idx_1  ON imparare2_evolucao_anon_data_trunc(registro, id_enterprise, data_dia);
        """
        dataRequest.execute(create_query)

    append_query = """
        SELECT 
            e.record_id AS registro,
            provider_profile AS perfil, 
            evolution_date AS dthr_evolucao,
            evolution_date::date as data_dia,
            unity_code_and_description AS unidade, 
            STRING_AGG(distinct evolution_description, '. ')  AS sentence_original,
            attendance_type AS tipo_atendimento,
            h.id_enterprise
        FROM evolutions e
        inner join hospitals h
            ON e.id_hospital = h.id_hospital
        inner join patients_to_update ptu
            ON e.record_id = ptu.record_id
                AND h.id_enterprise = ptu.id_enterprise
        GROUP BY e.record_id, h.id_enterprise, provider_profile, evolution_date, unity_code_and_description, attendance_type
    """

    df_iterator = dataRequest.get_data(queryText= append_query, chunck= 10000)
    with Pool(processes= cpu_count()) as pool:
        for _ in pool.imap_unordered(worker, df_iterator):
            pass

if __name__ == "__main__":
    main()