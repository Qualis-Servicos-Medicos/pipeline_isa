from multiprocessing import Pool, cpu_count
from ImpararePackage import dataRequest
import pandas as pd
import traceback
def worker(c: pd.DataFrame):
    try:
        CRITERIOS = [
            {
                "idade_min": 0,  
                "idade_max": 2,  

                "temp_min": 35,
                "temp_max": 37.5,  

                "pas_min": 90,
                "pas_max": float("inf"),
                
                "fr_min": 30,
                "fr_max": 60, 
                
                "fc_min": 100, 
                "fc_max": 180, 

                "hgt_min": 60,
                "hgt_max": 140
            },
            {
                "idade_min": 2,  
                "idade_max": 12,   

                "temp_min": 35,
                "temp_max": 38,

                "pas_min": 90,
                "pas_max": float("inf"),
                
                "fr_min": 30,
                "fr_max": 50, 
                
                "fc_min": 100,
                "fc_max": 150,

                "hgt_min": 60,
                "hgt_max": 140
            },
            {
                "idade_min": 12, 
                "idade_max": 24,   

                "temp_min": -float("inf"),
                "temp_max": 38,

                "pas_min": 90,
                "pas_max": float("inf"),
                
                "fr_min": 20,
                "fr_max": 40, 
                
                "fc_min": 70,
                "fc_max": 140,

                "hgt_min": 70,
                "hgt_max": 140
            },
            {
                "idade_min": 24, 
                "idade_max": 72,   

                "temp_min": -float("inf"),
                "temp_max": 38,

                "pas_min": 90,
                "pas_max": float("inf"),
                
                "fr_min": 20,
                "fr_max": 30, 
                
                "fc_min": 60, 
                "fc_max": 120, 

                "hgt_min": 70,
                "hgt_max": 140
            },
            {
                "idade_min": 72, 
                "idade_max": 96,   

                "temp_min": -float("inf"),
                "temp_max": 38,

                "pas_min": 90,
                "pas_max": float("inf"),
                
                "fr_min": 16,
                "fr_max": 25, 
                
                "fc_min": 60, 
                "fc_max": 110, 

                "hgt_min": 70,
                "hgt_max": 140
            },
            {
                "idade_min": 96, 
                "idade_max": 144,  

                "temp_min": -float("inf"),
                "temp_max": 38,

                "pas_min": 90,
                "pas_max": float("inf"),
                
                "fr_min": 12,
                "fr_max": 20, 
                
                "fc_min": 50,
                "fc_max": 100,

                "hgt_min": 70,
                "hgt_max": 140
            },
            {
                "idade_min": 144, 
                "idade_max": float("inf"), 
                
                "temp_min": -float("inf"),
                "temp_max": 38,

                "pas_min": 90,
                "pas_max": float("inf"),
                
                "fr_min": 12,
                "fr_max": 20, 
                
                "fc_min": 50, 
                "fc_max": 100, 

                "hgt_min": 70,
                "hgt_max": 140
            },
        ]

        def criterio(row):
            def verificar_alteracao(minimo: int | float, maximo: int | float, limite_min: int | float, limite_max: int | float) -> bool:
                if pd.isna(minimo) and pd.isna(maximo):
                    return None

                minimo_alterado: bool = (not pd.isna(minimo) and minimo < limite_min)

                maximo_alterado: bool = (not pd.isna(maximo) and maximo > limite_max)

                return minimo_alterado or maximo_alterado

            idade = row["idade_meses"]

            regra = next(
                r for r in CRITERIOS
                if r["idade_min"] <= idade < r["idade_max"]
            )

            if pd.isna(row["FC_max"]):
                row["FC_ALTA"] = None
            else:
                row["FC_ALTA"] = row["FC_max"] > regra["fc_max"]

            if pd.isna(row["FC_min"]):
                row["FC_BAIXA"] = None
            else:
                row["FC_BAIXA"] = row["FC_min"] < regra["fc_min"]

            row["FC_ALTERADA"] = verificar_alteracao(
                row["FC_min"], 
                row["FC_max"], 
                regra["fc_min"], 
                regra["fc_max"]
            )

            row["FR_ALTERADO"] = verificar_alteracao(
                row["FR_min"], 
                row["FR_max"], 
                regra["fr_min"], 
                regra["fr_max"]
            )

            row["TEMP_ALTERADA"] = verificar_alteracao(
                row["TEMP_min"],
                row["TEMP_max"],
                regra["temp_min"],
                regra["temp_max"],
            )

            row["HGT_ALTERADO"] = verificar_alteracao(
                row["HGT_min"],
                row["HGT_max"],
                regra["hgt_min"],
                regra["hgt_max"],
            )

            row["PAS_ALTERADO"] = verificar_alteracao(
                row["PAS_min"],
                row["PAS_max"],
                regra["pas_min"],
                regra["pas_max"],
            )

            return row
        
        c = c.apply(criterio, axis= 1)
        
        c.drop(columns=['birthdate'], inplace= True)
        dataRequest.set_data_on_sql(df= c, nomeTabelaDestino= "imparare2_dataset_enfermagem_categ", if_exists= "append")
    except Exception as e:
        print(f"Erro ao processar o chunk: {traceback.format_exc()}")
        return
    
def main():
    replace = True

    if replace:
        create_query = """
            DROP TABLE IF EXISTS imparare2_dataset_enfermagem_categ;
            CREATE UNLOGGED TABLE imparare2_dataset_enfermagem_categ (
                registro INTEGER,
                dia date,
                id_enterprise SMALLINT,
                idade_dias FLOAT,
                idade_meses FLOAT,
                "FC_min" FLOAT,
                "FC_max" FLOAT,
                "FR_min" FLOAT,
                "FR_max" FLOAT,
                "HGT_min" FLOAT,
                "HGT_max" FLOAT,
                "OXIMETRIA_min" FLOAT,
                "OXIMETRIA_max" FLOAT,
                "PAD_min" FLOAT,
                "PAD_max" FLOAT,
                "PAM_min" FLOAT,
                "PAM_max" FLOAT,
                "PAS_min" FLOAT,
                "PAS_max" FLOAT,
                "TEMP_min" FLOAT,
                "TEMP_max" FLOAT,
                "O2_min" FLOAT,
                "O2_max" FLOAT,
                "FIO2_min" FLOAT,
                "FIO2_max" FLOAT,
                "PEEP_min" FLOAT,
                "PEEP_max" FLOAT,
                "TEMP_ALTERADA" BOOLEAN,
                "FC_ALTERADA" BOOLEAN, 
                "FC_ALTA" BOOLEAN, 
                "FC_BAIXA" BOOLEAN,
                "HGT_ALTERADO" BOOLEAN,
                "FR_ALTERADO" BOOLEAN,
                "PAS_ALTERADO" BOOLEAN,
                "SINAIS_VITAIS_count_total" SMALLINT
            );
        """
        dataRequest.execute(create_query)

    append_query = """
        select 
            * 
        from (
            select 
                registro AS registro,
                dia::date AS dia,
                de.id_enterprise::SMALLINT AS id_enterprise,
                MIN("FC") AS "FC_min",
                MAX("FC") AS "FC_max",
                MIN("FR") AS "FR_min",
                MAX("FR") AS "FR_max",
                MIN("HGT") AS "HGT_min",
                MAX("HGT") AS "HGT_max",
                MIN("OXIMETRIA") AS "OXIMETRIA_min",
                MAX("OXIMETRIA") AS "OXIMETRIA_max",
                MIN("PAD") AS "PAD_min",
                MAX("PAD") AS "PAD_max",
                MIN("PAM") AS "PAM_min",
                MAX("PAM") AS "PAM_max",
                MIN("PAS") AS "PAS_min",
                MAX("PAS") AS "PAS_max",
                MIN("TEMP") AS "TEMP_min",
                MAX("TEMP") AS "TEMP_max",
                MIN("O2") AS "O2_min",
                MAX("O2") AS "O2_max",
                MIN("FIO2") AS "FIO2_min",
                MAX("FIO2") AS "FIO2_max",
                MIN("PEEP") AS "PEEP_min",
                MAX("PEEP") AS "PEEP_max",
                COUNT(*) AS "SINAIS_VITAIS_count_total",
                pr.birthdate,
                (de.dia - pr.birthdate) as idade_dias,
                ((de.dia - pr.birthdate) / 30.44)::smallint as idade_meses
            from imparare2_sinalvitais_pivot de
            INNER join (
                select distinct record_id, birthdate, h.id_enterprise from patients_records p inner join hospitals h on p.id_hospital = h.id_hospital 
            ) pr
                on de.registro = pr.record_id
                    and de.id_enterprise = pr.id_enterprise
            GROUP BY registro, pr.birthdate, de.id_enterprise, dia
        ) a
        where idade_dias >= 0
    """
    df_iterator = dataRequest.get_data(queryText= append_query, chunck= 2000)
  
    with Pool(processes= cpu_count()) as pool:
        for _ in pool.imap_unordered(worker, df_iterator):
            pass

if __name__ == "__main__":
    main()