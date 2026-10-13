from ImpararePackage import maestro
from ImpararePackage import dataRequest
import unicodedata as ud
import pandas as pd
import threading

def main(c: pd.DataFrame):
    c["id_hospital"] = c["id_hospital"].astype("Int32")
    def process(row):
        resultado = row['resultado'].lower()
        exame = row['exame'].lower()

        positivo = "não"
        if((resultado.find('positiv') > -1) and (exame.find('cultura') > -1)):
            positivo = "sim"

        return positivo

    def process2(row):
        resultado = row['resultado'].lower()
        exame = row['exame'].lower()

        if(exame.find('covid') > -1):
            if(((str(resultado).find('positiv') > -1) or (str(resultado).find('reag') > -1) or (str(resultado).find('detec') > -1)) 
                and not ((str(resultado).find('não') > -1) or (str(resultado).find('not') > -1))):
                return "sim"
        else:
            return "não"

    resultado_parse = {
        "P": "Positivo",
        "N": "Negativo",
        "R": "Resistente",
        "S": "Sensível"
    }
    c = maestro.remove_columns(df= c, arrayColumns= ["exame_id"])
    c['resultado'] = c['resultado'].map(resultado_parse).fillna(c['resultado'])

    def validaLeucos(x: pd.Series) -> bool:
        if not (x['item_exame'].lower().find('leuc') > -1):
            return False

        valor = x['resultado']
        if not isinstance(valor, (int, float)):
            try:
                valor = float(valor)
            except ValueError:
                return False

        return (valor >= 12000 or valor <= 4000) 

    c["criterio"] = c.apply(lambda x: 'sim' if(
        validaLeucos(x)
        or (x['exame'].lower().find('cultura')  > -1)
        or (x['item_exame'].lower().find('bacteriol')  > -1) or (x['item_exame'].lower().find('bacterios')  > -1)
        or (x['exame'].lower().find('covid') > -1) 
        or (x['exame'].lower().find('clostrid')  > -1)
    ) else 'não', axis= 1)

    c["positivo"] = c.apply(process, axis= 1)
    
    c["pcr_covid"] = c.apply(process2, axis= 1)

    gmr_parse = {
        "1": "sim",
        "0": "não",
        True: "sim",
        False: "não" 
    }
    c['gmr'] = c['gmr'].map(gmr_parse).fillna('não')

    exame_replace = {
        "GLOBAL DE LEUCOCITOS": "LEUCÓCITOS"
    }
    c["item_exame"] = c["item_exame"].str.upper().map(exame_replace).fillna(c["item_exame"])

    novosNomes = {"paciente_id":"patient_id"}
    c = maestro.rename_columns(df= c, DictColumns= novosNomes)

    def elk_upload(c: pd.DataFrame):
        client = dataRequest.ELASTICSEARCH_CONNECTION
        c["paciente_id"] = c["patient_id"]
        c = maestro.keep_columns(df= c, arrayColumns= [
            "id",
            "exame",
            "item_exame",
            "dthr_pedido",
            "dthr_entrega",
            "resultado",
            "positivo",
            "ordem",
            "criterio",
            "gmr",
            "paciente_id",
            "id_enterprise"
        ])
        actions = maestro.generate_actions(c, "exames")
        maestro.bulk_upload_with_retry(client, actions, context="exame", thread_count=1)

    job = threading.Thread(target= elk_upload, args=(c.copy(), ))
    job_3 = threading.Thread(target=dataRequest.set_data_on_sql, args=(c, "isa_exame"), kwargs={"if_exists": "append", "isLocal": True})
    
    jobs = [
        job, 
        job_3
    ]
    for j in jobs:
        j.start()
    
    for j in jobs:
        j.join()