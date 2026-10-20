from ImpararePackage import dataRequest
from ImpararePackage import maestro
from multiprocessing import Pool
import pandas as pd

def worker(c:pd.DataFrame):
  
    c["tmp_start"] = c["dthr_procedimento"].astype(str)
    c["tmp_end"] = c["dthr_fim_procedimento"].astype(str)
    c["registro"] = c["record_id"].astype(str)
    referencia = [["registro", "tmp_start", "tmp_end"]]
    destino = ["chave_procedimento"]
    separadores = [""]
    c =maestro.concatenate_columns(df= c, arrayDeReferencias= referencia, arrayDestinos= destino, arraySeparadores= separadores)

    novosNomes = {
            "record_id": "patient_id",
            "surgery_description": "nome_procedimento",
            #"provider_id": "prestador",
            "provider_name": "nome_medico", 
            "attendance_type": "tipo_atendimento",
            "attendance_id": "id_atendimento"
        }
    c = maestro.rename_columns(df= c, DictColumns= novosNomes)

    colunas = ["tmp_start", "tmp_end", "registro", "attendance_id"]
    c = maestro.remove_columns(df= c, arrayColumns= colunas)
    
    c = maestro.difference_time_between_columns(df= c, colunaInicio= "dthr_procedimento", colunaFim= "dthr_fim_procedimento")
    
    c = maestro.remove_nan(df= c, arrayColumns= ["tempo_de_cirurgia", "dthr_fim_procedimento"])

    c = maestro.replace_values_list(df= c, arrayColumns= ["chave_procedimento"], arrayDeTuplas= [(" ", "")])
    
    dataRequest.set_data_on_sql(df= c, nomeTabelaDestino= "imparare2_t1_cirurgias_3_3", if_exists= "append")

def main():
    replace =True

    if replace:
        create_query = """
            DROP TABLE IF EXISTS imparare2_t1_cirurgias_3_3;
            CREATE UNLOGGED TABLE imparare2_t1_cirurgias_3_3 (
                patient_id INTEGER,
                tipo_atendimento TEXT,  
                id_atendimento INTEGER,
                -- surgery_notice_id INTEGER, 
                nome_procedimento TEXT, 
                dthr_procedimento TIMESTAMP, 
                dt_procedimento DATE ,
                dthr_fim_procedimento TIMESTAMP, 
                -- prestador INTEGER, 
                nome_medico TEXT,
                chave_procedimento TEXT,
                tempo_de_cirurgia FLOAT,
                id_enterprise INTEGER
            );    
        """   
        dataRequest.execute(create_query)

    append_query = f"""
        SELECT 
            surgeries_rgo_names.record_id, 
            attendance_id,
            surgery_description, 
            DATE_TRUNC('minute', "surgery_start_date")::timestamp as dthr_procedimento, 
            surgery_start_date::date as "dt_procedimento",
            DATE_TRUNC('minute', "surgery_end_date")::timestamp as dthr_fim_procedimento, 
            provider_name, 
            attendance_type,
            h.id_enterprise
        FROM surgeries_rgo_names
        INNER JOIN hospitals h 
            ON surgeries_rgo_names.id_hospital = h.id_hospital
        INNER JOIN patients_to_update ptu
            ON surgeries_rgo_names.record_id = ptu.record_id
                AND h.id_enterprise = ptu.id_enterprise
        GROUP BY surgeries_rgo_names.record_id, 
                h.id_enterprise,
                attendance_id, 
                surgery_description,
                surgery_start_date, 
                surgery_start_date::date,
                surgery_end_date,
                provider_name, 
                attendance_type;
    """

    df_iterator = dataRequest.get_data(queryText= append_query, chunck= 2000)
    
    with Pool(processes=4) as pool:
        for _ in pool.imap_unordered(worker, df_iterator):
            pass

if __name__ == "__main__":
    main()
