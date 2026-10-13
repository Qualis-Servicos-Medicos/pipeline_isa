from ImpararePackage import dataRequest
from ImpararePackage import maestro
import pandas as pd
import threading

def main(c: pd.DataFrame):

    deParaInterface = {
        "OXIGÊNIO (L/MIN)" : "O2", 
        "O2": "O2",
        
        "FIO2 %" : "FIO2", 
        "FIO2" : "FIO2",

        "SAT.O2 %" : "OXIMETRIA", 
        "ST" : "OXIMETRIA",
        "OXIMETRIA": "OXIMETRIA",

        "F.C." : "FC", 
        "FC" : "FC",

        "F.R." : "FR", 
        "FR" : "FR",

        "PA." : "PA",
        "PA" : "PA",

        "P.A.M" : "PAM", 
        "PAM" : "PAM",

        "P.A. DIASTOLICA" : "PAD", 
        "P.A.D." : "PAD",
        "PAD" : "PAD",

        "P.A.S." : "PAS",
        "PAS" : "PAS", 

        "TEMP." : "TEMP",
        "TEM" : "TEMP",
        "TEMP" : "TEMP",

        "PEWS FC ACORDADO" : "PEWS ACORDADO",
        "PEWS FC DORMINDO" : "PEWS DORMINDO",

        "PEEP" : "PEEP",

        "PESO (KG)" : "PESO",
        "PESO" : "PESO",

        "GLICEMIA CAPILAR" : "HGT",

        "ECG (GLASGOW)" : "ECG GLASGOW",

        "BCF" : "BCF",
    }
    c["tipo_sinal"] = c["tipo_sinal"].map(deParaInterface)
    c["tipo_sinal"].dropna(axis= 0)

    deParaInterface = {
        "GRAUS CELSIUS (Cº)" : "GRAUS CELSIUS"
    }
    c["unimedida"] = c["unimedida"].map(deParaInterface)

    c["criterio"] = c.apply(lambda x: "sim" if(
        (x["tipo_sinal"] == 'TEMP' and (x["valor"] >= 38.0 or x["valor"] <= 35.0)) # Regra que indica temperatura alterada
        or (x["tipo_sinal"] == 'FR' and x["valor"] > 20) # Regra que indica FR alterada
        or (x["tipo_sinal"] == 'FC' and (x["valor"] < 60.0 or x["valor"] > 100.0)) 
        or (x["tipo_sinal"] == 'OXIMETRIA' and (x["valor"] < 95.0 or x["valor"] > 100.0)) 
        or (x["tipo_sinal"] == 'PAD' and x["valor"] > 85.0) 
        or (x["tipo_sinal"] == 'PAS' and (x["valor"] < 90.0 or x["valor"] > 130.0)) 
        or (x["tipo_sinal"] == 'DOR' and x["valor"] > 4.0) 
        or (x["tipo_sinal"] == 'HGT' and (x["valor"] < 70.0 or x["valor"] > 99.0)) 
        or (x["tipo_sinal"] == 'PAM' and (x["valor"] < 70.0 or x["valor"] > 100.0)) 
        or (x["tipo_sinal"] == 'BCF' and (x["valor"] < 110.0 or x["valor"] > 160.0)) 
        or (x["tipo_sinal"] == 'BCF - D' and (x["valor"] < 110.0 or x["valor"] > 160.0))
        ) else "não", axis =1)

    c["valor"] = c["valor"].astype(str)
    
    def elk_upload(c: pd.DataFrame):
        client = dataRequest.ELASTICSEARCH_CONNECTION
        c = maestro.keep_columns(df= c, arrayColumns= ["id", "paciente_id", "id_enterprise", "tipo_sinal", "dthr_coleta", "valor", "unimedida", "perfil", "ordem", "criterio"])
        actions = maestro.generate_actions(c, "sinais-vitais")
        maestro.bulk_upload_with_retry(client, actions, context="sinal_vital", thread_count=1)
    
    job = threading.Thread(target= elk_upload, args=(c, ))
    job_3 = threading.Thread(target=dataRequest.set_data_on_sql, args=(c, "isa_sinal_vital"), kwargs={"if_exists": "append", "isLocal": True})
    
    jobs = [
        job, 
        job_3
    ]
    for j in jobs:
        j.start()
    
    for j in jobs:
        j.join()