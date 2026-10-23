import pandas as pd
pd.options.mode.chained_assignment = None
import numpy as np
from datetime import timedelta
from datetime import datetime
import re
import unicodedata
from ImpararePackage import regexPattern
import re
import time
import pandas as pd
from typing import List, Tuple, Any, Literal
from ImpararePackage import dataRequest
from elasticsearch.helpers import parallel_bulk

import warnings

warnings.filterwarnings("ignore", category=UserWarning, module="pandas")
CRITERIOS_TEMPORAL_SUFFIX = ["_futuro", "_hoje", "_passado"]
# CRITERIOS_FEATURE_EXTRACTION_MODELO = [
#     'ronco', 
#     'tosse', 'cavita', 'opac', 'infil', 'fibrose_cistica', 'sec_pur_pulmonar', 'secr_traq', 'secr', 'puru', 'hemoptise', 'leucemia', 'esplenectomia', 'febre', 'consol', 'linfoma', 'o2',
#     "acinetobacter", "amarelada", "aspiracao", "crepitante", "enterobacter", "enterococcus", "hemophylus", "hipertermia", "imunossuprimido", "infeccao", "klebsiella", "leucocitose", "leucopenia", "moraxella", "pneumococcus", "pseudomonas", "sibilos", "intubacao",
#     "staphylococcus_aureus", "sepse_pulmonar", "sepse_respiratoria", "sepse_urinaria", "padrao_ventilatorio", "insuficiencia_ventilatoria", "esforco_ventilatorio", "lavado_broncoalveolar", "derrame_pleural", "escherichia_coli", "choque_septico", "dor_pleuritica", "dor_ventilatorio_dependente", "ventilacao_mecanica", "iot", "pav",
#     "eritema", "hiperemia", "mediastinite", "staphylococcus_coagulase_negativo", "supuracao", "rubor", "mal_estar", "abscesso", "calor", "dreno", "edema", "endocardite", "antibiotico", "bacteriologico", "deiscencia", "resistente", "taquicardia",
#     "cateter", "cateter_arterial", "cateter_urinario", "cvc", "cateter_venoso_periferico", "instabilidade", "oliguria", "hipotensao", "anuria", "bacteremia", "bacteriuria", "disuria", "leucocituria", "nitrito", "svd", "tsa", "choque", "staphylococcus", "e_coli", "colecao", "tremor", "calafrio",
#     "pos_operatorio", "dor_suprapubica", "foco_urinario", "colite_pseudomembranosa", "vomito", "shigella", "salmonela", "nausea", "dor_cabeca", "dor_abdominal", "diarreia",  "urgencia_urinaria", "urgencia_miccional", "sondagem_alivio", "sondagem_vesical", "urocultura", "piuria",
#     "albumina", "press_parc_co2", "creatinina", "glicose", "hemoglobina", "plaquetas", "bilirrubina", "lesao_pulmonar", "atelectasia", "fratura", "freq_cardiaca", "saturacao_sangue", "temperatura",
#     "sibilancia", "cardiomegalia",  "pneumonia",  "pneumotorax",  "freq_respiratoria",   "pressao_sanguinea",  "hemocultura",  "clostridium",  "hipotermia",  "apneia",  "bradicardia",  "streptococcus_viridans",  "consciencia", "hcm", 
#     "hgm", "covid",  "peep",  "fio2",  "spo2",  "pcr_covid", "sne",  "desnutricao",  "sedacao",  "vsg",  "fosfatase_alcalina",  "ldh",  "cetamina",  "propofol",  "clorpromazina",  "fentanil", 
#     "pancuronio", "noradrenalina", "diazepan", "lorazepan","flumazenil", "clonidina", "npt", "cateter_monolumen", "cateter_duplolumen", "cateter_triplolumen", "portocath", "cateter_hickmann", "shilley", "obesidade", "diabetes", "neutropenia", 
#     # Tirados:
#     "endoftalmite", "legionella", "ph_sangue", "yersinia", "clorose", "bicarbonato", "calcio", "potassio", "sodio", "propionibacterium", "cryptococcus", "pneumocystis", "histoplasma", "paracoccidioides", "bacteroides",
#     "broncograma_aereo", "avc", "candida", "fusobacterium", "peptostreptococcus", "corynebacterium", "bacillus", "aerococcus", "coccidioides", "veillonella", "campylobacter", "giardia", "tabagismo",
#     'dpoc',
#     # Novos:
#     "pneumatose", "piora_troca_gasosa", "fontanela_abaulada", "glicose_liquor", "prote_liquor", "leuco_liquor", "bacteria_liquor", "irritabilidade", "cultura_liquor",
#     "hipoativ", "dren_serosa", "necrose_intestinal", "intestino_fixo", "sangue_fezes", "convulsao", "pneumoperitonio", "dist_abdominal", "asp_bilioso", 
#     # "pcr",
#     "letargia", "int_glicose", 
#     # "int_alimentar",
# ]

CRITERIOS_FEATURE_EXTRACTION_MODELO = [
    "apneia",
    "hipoativ",
    "hipertermia",
    "bradicardia",
    "secrecao",
    "vomito",
    "perfuracao",
    "pneumatose",
    "hiperemia",
    "estase_gastr",
    "desc_respirat",
    "distensao_abdominal",
    "hipocorado",
    "acesso_venoso",
    "ronco",
    "tosse",
    "cavita",
    "opac",
    "infil",
    "sec_pur_pulmonar",
    "secr_traq", 
    "puru", 
    "febre", 
    "consol", 
    "o2", 
    "amarelada", 
    "aspiracao", 
    "broncograma_aereo", 
    "crepitante",
    "imunossuprimido",
    "infeccao", 
    "leucocitose", 
    "leucopenia", 
    "sibilos",
    "intubacao",
    "sepse_pulmonar",
    "sepse_respiratoria",
    "sepse_urinaria",
    "padrao_ventilatorio",
    "lavado_broncoalveolar",
    "derrame_pleural",
    "choque_septico",
    "dor_pleuritica",
    "dor_ventilatorio_dependente",
    "ventilacao_mecanica",
    "iot",
    "pav",
    "endoftalmite",
    "mediastinite",
    "supuracao",
    "rubor",
    "mal_estar",
    "abscesso",
    "calor",
    "dreno",
    "edema",
    "endocardite",
    "antibiotico",
    "bacteriologico",
    "deiscencia",
    "taquicardia",
    "cateter",
    "cateter_arterial",
    "cateter_urinario",
    "cvc",
    "cateter_venoso_periferico",
    "instabilidade",
    "leucocituria",
    "nitrito",
    "svd",
    "tsa",
    "choque",
    "colecao",
    "tremor",
    "calafrio",
    "pos_operatorio",
    "dor_suprapubica",
    "foco_urinario",
    "colite_pseudomembranosa",
    "nausea",
    "dor_cabeca",
    "dor_abdominal",
    "diarreia",
    "urgencia_urinaria",
    "urgencia_miccional",
    "sondagem_alivio",
    "sondagem_vesical",
    "urocultura",
    "piuria",
    "plaquetas",
    "lesao_pulmonar",
    "pneumonia",
    "atelectasia",
    "pneumotorax",
    "freq_respiratoria",
    "freq_cardiaca",
    "pressao_sanguinea",
    "saturacao_sangue",
    "hemocultura",
    "clostridium",
    "sibilancia",
    "hipotermia",
    "consciencia",
    "peep",
    "fio2",
    "spo2",
    "temperatura",
]

CRITERIOS_INTERFACE = [ 
    "ronco", "tosse", "cavita", "opac", "infil", "fibrose_cistica", "sec_pur_pulmonar", 
    "secr_traq", "secrecao", "puru", "dpoc", "hemoptise", "leucemia", "esplenectomia", "febre", 
    "consol", "linfoma", "o2", "acinetobacter", "amarelada", "aspiracao", "broncograma_aereo", 
    "crepitante", "enterobacter", "enterococcus", "hemophylus", "hipertermia", "imunossuprimido", 
    "infeccao", "klebsiella", "legionella", "leucocitose", "leucopenia", "moraxella", "pneumococcus", 
    "pseudomonas", "sibilos", "intubacao", "staphylococcus_aureus", "sepse_pulmonar", "sepse_respiratoria", 
    "sepse_urinaria", "padrao_ventilatorio", "desc_respirat", "lavado_broncoalveolar", 
    "derrame_pleural", "escherichia_coli", "choque_septico", "dor_pleuritica", "dor_ventilatorio_dependente", 
    "ventilacao_mecanica", "iot", "pav", "endoftalmite", "hiperemia", "mediastinite", 
    "staphylococcus_coagulase_negativo", "supuracao", "rubor", "mal_estar", "abscesso", "calor", "dreno", 
    "edema", "endocardite", "antibiotico", "bacteriologico", "deiscencia", "resistente", "taquicardia", "cateter", 
    "cateter_arterial", "cateter_urinario", "cvc", "cateter_venoso_periferico", "clorose", "instabilidade", "oliguria", 
    "hipotensao", "anuria", "bacteremia", "bacteriuria", "disuria", "leucocituria", "nitrito", "svd", "tsa", "choque",
    "staphylococcus", "e_coli", "colecao", "tremor", "calafrio", "pos_operatorio", "dor_suprapubica", "foco_urinario", 
    "colite_pseudomembranosa", "yersinia", "vomito", "shigella", "salmonela", "nausea", "giardia", "dor_cabeca", 
    "dor_abdominal", "diarreia", "campylobacter", "urgencia_urinaria", "urgencia_miccional", "sondagem_alivio", 
    "sondagem_vesical", "urocultura", "piuria", "albumina", "press_parc_co2", "bicarbonato", "calcio", "creatinina", 
    "glicose", "hemoglobina", "plaquetas", "potassio", "sodio", "bilirrubina", "cardiomegalia", "lesao_pulmonar", 
    "pneumonia", "atelectasia", "pneumotorax", "fratura", "freq_respiratoria", "freq_cardiaca", "pressao_sanguinea", 
    "saturacao_sangue", "hemocultura", "propionibacterium", "cryptococcus", "pneumocystis", "histoplasma", "paracoccidioides", 
    "bacteroides", "candida", "clostridium", "fusobacterium", "peptostreptococcus", "sibilancia", "hipotermia", "apneia", 
    "bradicardia", "streptococcus_viridans", "consciencia", "hcm", "hgm", "corynebacterium", "bacillus", "aerococcus", 
    "coccidioides", "veillonella", "covid", "peep", "fio2", "spo2", "pcr_covid", "temperatura", "ph_sangue", "avc", "sne", 
    "desnutricao", "sedacao", "vsg", "fosfatase_alcalina", "ldh", "cetamina", "propofol", "clorpromazina", "fentanil", 
    "pancuronio", "noradrenalina", "diazepan", "lorazepan", "flumazenil", "clonidina", "npt", "cateter_monolumen", 
    "cateter_duplolumen", "cateter_triplolumen", "portocath", "cateter_hickmann", "shilley", "obesidade", "diabetes", 
    "neutropenia", "tabagismo",
]

def get_hospitals_allowed_process_string_condition() -> str:
    """ Esta funçào retorna uma string representando a condição de in para ids de company/hospital que devem ser processados
        Ex de retorno: ('1', '6')
    """

    HOSPITALS_ALLOWED_PROCESS = [1, 6, 7, 8, 12]
    ids = "("
    for id in HOSPITALS_ALLOWED_PROCESS:
        ids += f"'{id}', "

    ids = ids.strip(", ")
    ids += ")"

    return ids

def get_must_update_all_patients() -> Literal['1', '0']:
    """ Esta funçào retorna uma string representando a condição de in para ids de company/hospital que devem ser processados
        Ex de retorno: ('1', '6')
    """
    df = dataRequest.get_data("""SELECT COUNT(*) AS qtd FROM pipeline_execution_log WHERE execution_date > NOW() - INTERVAL '7 days';""", chunck= None)
    MUST_UPDATE_ALL_PATIENTS = (datetime.now().weekday == 6 or (len(df) > 0 and df.iloc[0]['qtd'] == 0))
    if MUST_UPDATE_ALL_PATIENTS:
        return '1'
    else:
        return '0'

# Esta função abaixo permite receber um dataframe e receber suas colunas ou sua unica coluna como referencia e transformar os valores para casabaixa.
# Esta função possivelmente esteja pecando por falta de verificador para evitar erros como entrada de numeros, tenho que veridficar se isso realmente iria gerar um error.
def to_lower_case(df:pd.DataFrame, column:str = "", arrayColumns:list =[]) -> pd.DataFrame:
    if column != "":
        arrayColumns.append(column)
    for column in arrayColumns:
        df[column] = df[column].str.lower()
    return df


# Esta função abaixo permite receber um dataframe e receber suas colunas ou sua unica coluna como referencia e transformar os valores para casaAlta.
# Esta função possivelmente esteja pecando por falta de verificador para evitar erros como entrada de numeros, tenho que veridficar se isso realmente iria gerar um error.
def to_upper_case(df:pd.DataFrame, column:str = "", arrayColumns:list =[]) -> pd.DataFrame:
    if column != "":
        arrayColumns.append(column)
    for column in arrayColumns:
        df[column] = df[column].str.upper()
    return df


# Esra função renomeia as colunas de um dataframe a partir de um dicionario de entrada
# Ela espera receber um dataframe e um dicionario com os nomes antigos e os novos nomes que devem virar, nome antigo chave e novo nome valor
def rename_columns(df:pd.DataFrame, DictColumns: dict[str, str]) -> pd.DataFrame:
    df.rename(columns = DictColumns, inplace = True)
    return df


# # # Rever a função
# # Esta função recebe como parametro um dataframe e um 3 arrays:
# # arrayDestinos: será uma lista de strings representando os nomes de colunas destin da concatenação.
# # arrayDeReferencias: será uma lista de listas  de strings representando os nomes das colunas a serem concatenadas.
# # arraySeparadores: será uma lista  de strings representando os separadores a serem utilizados em cada concatenação
# # OBS: todos os arrays devem ter o mesmo comprimento(length)
# #OBS: caso voce queira concatener uma coluna na outra e nao criar uma coluna nova, no array de arrays, informe somente o nome da segunda coluna.
# def concatenate_columns(df:pd.DataFrame, arrayDestinos:list, arrayDeReferencias:list, arraySeparadores:list, asTypeSTR: bool = True) -> pd.DataFrame:
#     controlePosicao = 0
#     if len(arrayDeReferencias) == len(arrayDestinos) and len(arrayDestinos) == len(arraySeparadores):
#         for destino in arrayDestinos:
#             df[destino] = ""
#             for referencia in arrayDeReferencias[controlePosicao]:
#                 if asTypeSTR:
#                     # df[destino] += arraySeparadores[controlePosicao].astype(str) + df[referencia].astype(str)
#                     df[destino] += str(arraySeparadores[controlePosicao]) + df[referencia].to_string()
#                 else:
#                     df[destino] += str(arraySeparadores[controlePosicao]) + df[referencia]
#             df[destino] = df[destino].str.strip(arraySeparadores[controlePosicao])
#             controlePosicao += 1
#     else:
#         raise IndexError
#     return df

# Nova versão da Concatenate_columns
def concatenate_columns(df:pd.DataFrame, arrayDestinos:list, arrayDeReferencias:list, arraySeparadores:list, asTypeSTR: bool = True) -> pd.DataFrame:
    controlePosicao = 0
    if len(arrayDeReferencias) == len(arrayDestinos) and len(arrayDestinos) == len(arraySeparadores):
        for destino in arrayDestinos:
            # if destino not in df.columns:
            #     df[destino] = df[arrayDeReferencias[controlePosicao]]
            #     for referencia in range(1, len(arrayDeReferencias[controlePosicao])):
            #         df[destino] += str(arraySeparadores[controlePosicao]) + df[referencia].astype(str)
            # else:
            #     df[destino] = df[destino] + str(arraySeparadores[controlePosicao]) + df[arrayDeReferencias[controlePosicao]]
            #     for referencia in range(1, len(arrayDeReferencias[controlePosicao])):
            #         df[destino] += str(arraySeparadores[controlePosicao]) + df[referencia].astype(str)    
            if destino not in df.columns:
                df[destino] = ""
                for referencia in (arrayDeReferencias[controlePosicao]):
                    df[destino] += str(arraySeparadores[controlePosicao]) + df[referencia].astype(str)
                    df[destino] = df[destino].str.strip("None")
            else:
                df[destino + "_aux"] = ""
                for referencia in (arrayDeReferencias[controlePosicao]):
                    df[destino + "_aux"] += str(arraySeparadores[controlePosicao]) + df[referencia].astype(str)
                    df[destino+"_aux"] = df[destino+"_aux"].str.strip("None")
                df = df.drop(columns=destino)
                df = df.rename(columns={destino + "_aux": destino})
            df[destino] = df[destino].str.strip(arraySeparadores[controlePosicao])
            controlePosicao += 1
    else:
        raise IndexError
    return df

# Esta função irá separar uma string de uma coluna em varias subtrings divididas no separador informado e salva nas novas colunas
# arrayDestinos: espera um array de arrays com os nomes destinos de novas colunas apos o split da string de coluna de referencia
# arrayReferencia: espera o nome de uma coluna que sua string será splitada gerando as novas colunas
# arraySeparadores: espera receber um array com os separadores para operar separadores
def split_columns_into_many(df:pd.DataFrame, arrayDestinos:list, arrayDeReferencia:list, arraySeparadores:list) -> pd.DataFrame:
    controlePosicao = 0
    if len(arrayDeReferencia) == len(arrayDestinos) and len(arrayDestinos) == len(arraySeparadores):
        for destino in arrayDestinos:
            df[destino] = df[arrayDeReferencia[controlePosicao]].astype(str).str.split(arraySeparadores[controlePosicao])
            controlePosicao += 1
    return df

# Esta função irá separar uma string de uma coluna em varias subtrings divididas no separador informado e salva nas novas colunas _0, _1, _2, ...
# maxColumnsToSplit: espera um array de arrays com os nomes destinos de novas colunas apos o split da string de coluna de referencia
# arrayReferencia: espera o nome de uma coluna que sua string será splitada gerando as novas colunas
# arraySeparadores: espera receber um array com os separadores para operar separadores
# __new__
def split_columns_count(df:pd.DataFrame, arrayDeReferencia:list, arraySeparadores:list, maxColumnsToSplit:int = 1) -> pd.DataFrame:
    controlePosicao = 0
    for referencia in arrayDeReferencia:
        if maxColumnsToSplit > 0:
            splited_column = df[referencia].astype(str).str.split(arraySeparadores[controlePosicao], n= 2)
            for i in range(maxColumnsToSplit):
                column_name = referencia+"_"+str(i)
                df[column_name] = ""
                for j in range(len(splited_column)):
                    if len(splited_column.iloc[j]) > i:
                        df[column_name].loc[j] = splited_column.loc[j][i]
        controlePosicao += 1
    return df

def split_columns_count_vectorized(df: pd.DataFrame, arrayDeReferencia: list, arraySeparadores: list, maxColumnsToSplit: int = 1) -> pd.DataFrame:
    for i, referencia in enumerate(arrayDeReferencia):
        if maxColumnsToSplit > 0:
            # Split the column into multiple columns at once
            splited_columns = df[referencia].astype(str).str.split(arraySeparadores[i], n=maxColumnsToSplit, expand=True)
            
            # Add the new columns to the dataframe
            for j in range(maxColumnsToSplit):
                column_name = f"{referencia}_{j}"
                if j < splited_columns.shape[1]:
                    df[column_name] = splited_columns[j]
                else:
                    df[column_name] = ""

    return df

# Esta função parseia as datas das colunas para formato de UTC, horario universal
# Ela espera receber um dataframe e um array de colunas que ela deverá operar em cima, ou uma coluna unica que ela deverá operar
# errors: {‘ignore’, ‘raise’, ‘coerce’}
# format: str, ex: "%d/%m/%Y"
# infer_datetime_format: bool, If True and no format is given, attempt to infer the format of the datetime
def parse_date(df:pd.DataFrame, column:str = "", arrayColumns: list = [], sufixo:str = "_parsed", 
               format:str = None, errors:str = "coerce",
               dayfirst:bool = False, yearfirst:bool = False) -> pd.DataFrame:
    if column != "":
        arrayColumns.append(column)
    for col in arrayColumns:
        if sufixo in col:
            columDestino = col
        else:
            columDestino = col + sufixo
        if dayfirst:
            df[columDestino] = pd.to_datetime(df[col], utc= False, format= format, errors= errors, dayfirst= True)
        elif yearfirst:
            df[columDestino] = pd.to_datetime(df[col], utc= False, format= format, errors= errors, yearfirst= True)
        else:
            df[columDestino] = pd.to_datetime(df[col], utc= False, format= format, errors= errors, yearfirst= yearfirst, dayfirst= dayfirst)
        if errors == "coerce":
            df = df[df[columDestino].notna()]
    return df


# Esta função opera em normalize os dados de uma coluna.
# Normalize: converts to lowercase, removes accents, performs Unicode normalization (Café -> cafe)
#   and keeps only letters, numbers and dots. This last parameter could be personalized if necessary.
# Ela espera como parametro um dataframe, uma lista de colunas para normalize ou uma unica coluna e
# normalForm: Valid values for form are "NFC", "NFKC", "NFD", and "NFKD".
"""
    The Unicode standard defines various normalization forms of a Unicode string, based on the 
      definition of canonical equivalence and compatibility equivalence. In Unicode, several 
      characters can be expressed in various way. For example, the character U+00C7 (LATIN 
      CAPITAL LETTER C WITH CEDILLA) can also be expressed as the sequence U+0043 (LATIN 
      CAPITAL LETTER C) U+0327 (COMBINING CEDILLA).
    For each character, there are two normal forms: normal form C and normal form D. Normal 
      form D (NFD) is also known as canonical decomposition, and translates each character 
      into its decomposed form. Normal form C (NFC) first applies a canonical decomposition, 
      then composes pre-combined characters again.
    In addition to these two forms, there are two additional normal forms based on compatibility 
      equivalence. In Unicode, certain characters are supported which normally would be unified 
      with other characters. For example, U+2160 (ROMAN NUMERAL ONE) is really the same thing as 
      U+0049 (LATIN CAPITAL LETTER I). However, it is supported in Unicode for compatibility with 
      existing character sets (e.g. gb2312).
    The normal form KD (NFKD) will apply the compatibility decomposition, i.e. replace all 
      compatibility characters with their equivalents. The normal form KC (NFKC) first applies 
      the compatibility decomposition, followed by the canonical composition.
    Even if two unicode strings are normalized and look the same to a human reader, if one has 
      combining characters and the other doesn't, they may not compare equal.
"""
def normalize(df:pd.DataFrame, column:str = "", arrayColumns:list = [], normalForm:str= "NFKD") -> pd.DataFrame:
    # import unicodedata
    if column != "":
        arrayColumns.append(column)
    for column in arrayColumns:
        df[column]= (df[column]
                        .str.lower()
                        .str.normalize(normalForm)
                        .str.encode("ascii", errors="ignore")
                        .str.decode("utf-8")
                    )
    
    return df


# Esta função remove "sujeira" das strings como espaço em branco \t, \n...
# Ela espera como parametro um dataframe, uma lista de colunas ou uma unica coluna a ser ajustada
def trim(df:pd.DataFrame, column:str = "", arrayColumns:list = []):
    if column != "":
        arrayColumns.append(column)
    for column in arrayColumns:
        df[column] = df[column].str.strip()
    return df


# Esta função remove caracteres indevidos dentro das strings
# Ela espera como parametro um dataframe, um array de tuplas contendo caracter que deseja remover e os caracteres que deseja serem colocados no lugar
# alem disso é necessário informar ou o nome da unica coluna a ser operada, ou um array de colunas a serem operadas.
def replace_values_list(df: pd.DataFrame, arrayDeTuplas: list[tuple[str, str]], column:str = "", arrayColumns: list[str] = [], regex:bool = False, exect: bool = False) -> pd.DataFrame:
    if column != "" and column not in arrayColumns and column is not None:
        arrayColumns.append(column) 
    
    for col in arrayColumns:
        if col not in df.columns:
            continue

        series = df[col].astype(str)

        for pattern, repl in arrayDeTuplas:
            if exect:
                series = series.replace(
                    "^" + re.escape(pattern) + "$",
                    repl,
                    regex=True
                )
            else:
                series = series.str.replace(pattern, repl, regex=regex)

        df[col] = series

    return df


def replace_values_list_vectorized(df: pd.DataFrame, arrayDeTuplas: list, column:str = "", arrayColumns:list = [], regex:bool = False, exect: bool = False) -> pd.DataFrame:
    if column != "" and column not in arrayColumns and column is not None:
        arrayColumns.append(column)
    for tupla in arrayDeTuplas:
        if exect:
            df[arrayColumns] = df[arrayColumns].astype(str).replace('^' + re.escape(tupla[0]) + '$', tupla[1], regex=True)
        else :
            df[arrayColumns] = df[arrayColumns].astype(str).replace(tupla[0],tupla[1], regex= regex)
    return df

# Esta função opera o de para das linhas onde transforma o estado da linha, peculiar para sua forma padronizada do sistema
# Ela espera como parametro o dataframe, um nome da coluna onde deverá ser operado essa leitura ou um array das colunas a serem operadas e tambem o dicionario com os dados de referencia.
def de_para_rows(df: pd.DataFrame, dicionarioParametros:dict, column:str = "", arraycolumns:list = []):
    def retorna_esperado(x):
        return dicionarioParametros.get(x)
    if column != "":
        arraycolumns.append(column)
    for column in arraycolumns:
        df[column].apply(retorna_esperado)
    return df


# Esta função remove as colunas desejadas
# Ela espera como parametro um dataframe, uma lista de colunas para remover ou uma unica coluna
# drop_column()
def remove_columns(df: pd.DataFrame, column: str = "", arrayColumns: list[str] = []) -> pd.DataFrame:
    if column != "":
        arrayColumns.append(column)
    columns_to_be_removed: list[str] = []
    for col in arrayColumns:
        if col in df.columns:
            columns_to_be_removed += [col]
    df.drop(columns= columns_to_be_removed, inplace= True)
    return df


# Esta funçao retorna o dataframe somente com a colunas desejadas
# Ela espera como parametro um dataframe, uma lista de colunas para manter ou uma unica colunas
def keep_columns(df: pd.DataFrame, arrayColumns: list = [], column: str = "") -> pd.DataFrame:
    if column != "":
        arrayColumns.append(column)
    return df[arrayColumns]

# Esta função remove as linhas que nao estão com a data acima de uma data de interesse
# Ela espera como parametro um dataframe, uma lista de colunas para manter ou uma unica colunas
# remove_rows_between_date()
def keep_rows_after_date(df: pd.DataFrame, column: str = "", arrayColumns: list = [], ano: int = 2020, mes: int = 1, dia: int = 1) -> pd.DataFrame:
    if column != "":
        arrayColumns.append(column)
    for column in arrayColumns:
        try:
            target_date = pd.Timestamp(year= ano, month= mes, day= dia)#datetime(ano, mes, dia), tz='UTC')
            df = df[df[column] > target_date]
        except:
            try:
                data = datetime.date(datetime(ano, mes, dia))
                df = df[df[column] > data]
            except:
                data = pd.Timestamp(datetime(ano, mes, dia), tz='UTC')
                df = df[df[column] > data]

    return df


def keep_rows_before_date(df: pd.DataFrame, column: str = "", arrayColumns: list = [], ano: int = 2020, mes: int = 1, dia: int = 1) -> pd.DataFrame:
    if column != "":
        arrayColumns.append(column)
    for column in arrayColumns:
        try:
            target_date = pd.Timestamp(year= ano, month= mes, day= dia)#datetime(ano, mes, dia), tz='UTC')
            df = df[df[column] < target_date]
        except:
            try:
                data = datetime.date(datetime(ano, mes, dia))
                df = df[df[column] > data]
            except:
                data = pd.Timestamp(datetime(ano, mes, dia), tz='UTC')
                df = df[df[column] < data]
    return df


# Esta função divide a string da direita para a esquerda a partir de certo separador
# Ela espera como um parametro um dataframe, uma coluna e um separador de desejo
def tokenize_column(df: pd.DataFrame, column:str) -> pd.DataFrame:
    df["tok"] = df[column].str.rsplit()
    return df


# Esta funcão conta o numero de palavras em uma certa string
# Ela espera como parametro, um datafram e uma coluna
def count_words(df:pd.DataFrame, column:str = "") -> pd.DataFrame:
    df["count_words"] = df[column].str.len()
    return df


# Esta função transforma o valor para Int das colunas informadas
# Esta funçãqo recebe um dataframe, e um array de colunas ou uma unica coluna que debe transfotmar a string para int
def to_int(df: pd.DataFrame, arrayColumns:list = [], column:str = "", errors:str = 'ignore'):
    if column != "":
        arrayColumns.append(column)
    for column in arrayColumns:
        if column in df.columns:
            df[column] = pd.to_numeric(df[column], errors='coerce')#, dtype_backend='numpy_nullable')
            # df[column] = df[column].round()
            # df[column] = pd.to_numeric(df[column], errors='coerce', downcast='integer', dtype_backend='numpy_nullable')
            df[column] = df[column].round(0)
            # df[column] = np.round(df[column])
            # df[column] = df[column].fillna(-1)
            df[column] = df[column].astype(pd.Int64Dtype(), errors=errors)
            # df[column] = df[column].astype('Int64', errors=errors)
            # df[column] = df[column].astype("int64", casting="safe")
            # df[column] = pd.to_numeric(df[column], errors='coerce', dtype_backend='numpy_nullable', downcast='integer')
    return df

# Esta função transforma o valor para Float das colunas informadas
# Esta funçãqo recebe um dataframe, e um array de colunas ou uma unica coluna que debe transfotmar a string para int
def to_float(df: pd.DataFrame, arrayColumns:list = [], column:str = "", errors:str = 'ignore'):
    if column != "":
        arrayColumns.append(column)
    for column in arrayColumns:
        if column in df.columns:
            df[column] = pd.to_numeric(df[column], errors='coerce', dtype_backend='numpy_nullable')
            df[column] = df[column].astype('float64', errors=errors)
    return df


#Esta função normaliza caso tenha tido registro de bacteria
# Esta função espera receber como entrada um array com os nomes das colunas de referencia e um array com os nomes das colunas de destino, ou nomes unicos de colunas, sem ser arrays
def bacteriologico_negativo(df: pd.DataFrame, arrayColumns:list = [], column:str = "", arrayColumnDestiny:list = [], columnDestiny:str = "") -> pd.DataFrame:
    if column != "":
        arrayColumns.append(column)
    if columnDestiny != "":
        arrayColumnDestiny.append(columnDestiny)
    for i in range(len(arrayColumns)): # não vai funcionar pois esta string é diferente para cada cliente
        df[arrayColumnDestiny[i]] = df.apply(lambda df:1 if (df[arrayColumns[i]] == "Não houve crescimento bacteriano") else 0, axis=1)
    return df


# Esta função preenche linhas vazias com os dados intencionados
# Ela espera receber como parametro, um dataframe, um arrayde colunas ou uma coluna unica, e um arrayde referencias para substituir ou uma unica informacao para substituir
# fill_empty_cells() 
def fillnan(df: pd.DataFrame, arrayColumns: list = [], arraySubstitui:list = [], column:str = "", substitui:str = "") -> pd.DataFrame:
    if column != "":
        arrayColumns.append(column)
    arraySubstitui += substitui
    for i in range(len(arrayColumns)):
        df[arrayColumns[i]] = df[arrayColumns[i]].fillna(arraySubstitui[i])
    return df


# Esta função olha todas as colunas do dataframe, verifica se a coluna possui o prefixo de interesse, e substitui os campos nan pelo dado de replaceNan informado na coluna
# Ela espera como parametro, somente um dataframe;
def fillnan_columns_with_prefix(df: pd.DataFrame, prefixo:str, replaceNan) -> pd.DataFrame:
    for column in df.columns:
        if prefixo in column:
            df[column].fillna(replaceNan, inplace = True)
    return df


# Esta função remove linhas vazias prensentes nas colunas de interesse
# Ela espera como parametro um dataframe, uma lista de colunas para remover os NaNs ou uma unica colunas
# remove_rows_with_na() mesma operação
# remove_empty_rows() mesma operação
def remove_nan(df: pd.DataFrame, column:str = "", arrayColumns: list = []) -> pd.DataFrame:
    if column != "":
        arrayColumns.append(column)
    # for col in arrayColumns:
    #     df[col] = df[col].astype(str).str.replace("", np.nan)#, inplace= True)
    df.dropna(subset=arrayColumns, inplace= True)
    return df


# Esta Funcão calcula o tempo de cirurgia, resultado apresentado em minutos
# Ela espera receber como parametro um dataframe e duas strings referentes as colunas de inicio e de fim do procedimento respectivamente e tambem pode ser informado o nome da coluna destino onde deve ser salvo este dado
def difference_time_between_columns(df:pd.DataFrame, colunaInicio:str, colunaFim:str, colunaDestino:str = "tempo_de_cirurgia") -> pd.DataFrame:
    df[colunaDestino] = pd.to_datetime(df[colunaFim], utc = False) - pd.to_datetime(df[colunaInicio], utc = False)
    df[colunaDestino] = df[colunaDestino].fillna("0")
    df[colunaDestino] = df[colunaDestino] / np.timedelta64(1, "m")
    df[colunaDestino] = df[colunaDestino].astype(int)
    return df


# Esta função calcula o tempo de com precisão entre a data de nascimento e a data atual
# Ela espera receber como parametro um dataframe, e duas strings referentes a coluna de nascimento
def difference_time_relativedelta_nascimento(df:pd.DataFrame, dataNascimento:str, colunaDestino:str= "Idade Hoje"):
    from dateutil.relativedelta import relativedelta
    try:
        df[dataNascimento] = pd.to_datetime(df[dataNascimento], unit="ms", utc=False).dt.tz_convert(None)
    except:
        df[dataNascimento] = pd.to_datetime(df[dataNascimento], unit="ms", utc=False)#.dt.tz_convert(None)
    df[colunaDestino] = df[dataNascimento].apply(lambda nascimento: relativedelta(datetime.today(), nascimento).years)
    return df


# Esta função calcula e armazena em uma nova coluna o tempo em dias entre duas datas informadas em colunas
# Ela espera como paramentro um dataframe, e uma lista de colunas destino e uma lista de lista de colunas de referencia para calculo
def difference_time_between_columns_days(df: pd.DataFrame, arrayColunasDestino:list= [], arrayColunasReferencia: list = []) -> pd.DataFrame:
    referencia = 0
    for destino in arrayColunasDestino:
        df[destino] = pd.to_datetime(df[arrayColunasReferencia[referencia][1]], utc= False) - pd.to_datetime(df[arrayColunasReferencia[referencia][0]], utc= False)
        df[destino] = df[destino].apply(lambda x: (x.days))
        referencia +=1
    return df


#Esta função retorna o dataframe com novas 3 colunas separando os dados das datas
# Ela espera por parametro um dataframe, uma lista de colunas ou uma unica coluna.
def extract_time(df: pd.DataFrame, arrayColumns:list = [], column:str = "") -> pd.DataFrame:
    if column != "":
        arrayColumns.append(column)
    for column in arrayColumns:
        nameYear = column + "_year"
        nameMonth = column + "_month"
        nameDays = column + "_day"
        df[nameYear] = pd.DatetimeIndex(df[column]).year
        df[nameMonth] = pd.DatetimeIndex(df[column]).month
        df[nameDays] = pd.DatetimeIndex(df[column]).day
        df[nameYear] = df[nameYear].astype(str)
        df[nameMonth] = df[nameMonth].astype(str)
        df[nameDays] = df[nameDays].astype(str)
    return df


# Esta função retorna uma nova coluna com a data formatada da forma desejada, ela tem um formato padrao mas caso desejado pode ser modificado
# Ela espera como parametro um dataframe, e uma coluna de referencia para a data
def format_date(df: pd.DataFrame, column: str, dateFormat: str = "%yyyy%MM%dd") -> pd.DataFrame:
    colunaDestino = column + "_formatted"
    df[colunaDestino] = pd.to_datetime(df[column], format= dateFormat, utc= False, yearfirst=True)
    return df


# # Esta função cria colunas dummy de colunas desejadas
# # Ela espera por parametro um dataframe, uma unica coluna, e uma lista de possiveis resultados esprados, coisas que desejam procurar.
# def create_dummy(df: pd.DataFrame, column:str = "", arrayDeDesejos:list = []) -> pd.DataFrame:
#     for desejo in arrayDeDesejos:
#         nomeDummy = column+"_"+desejo
#         df[nomeDummy] = np.nan
#     for j in range(len(df)):
#         for i in range(len(arrayDeDesejos)):
#             if df[column].loc[j] == None:
#                 df[column].loc[j] = ""
#             nomeDummy = column+"_"+arrayDeDesejos[i]
#             df[nomeDummy].loc[j] = 1 if df[column].loc[j] in arrayDeDesejos[i] else 0
#     # for i in range(len(arrayDeDesejos)):
#     #     nomeDummy = column+"_"+arrayDeDesejos[i]
#     #     df[nomeDummy] = np.nan
#     #     for j in range(len(df)):
#     #         df[nomeDummy].loc[j] = 1 if df[column].loc[j] in arrayDeDesejos[i] else 0
#     return df

def create_dummy_vectorized(df: pd.DataFrame, column: str = "", arrayDeDesejos: list = []) -> pd.DataFrame:
    # Ensure the column is filled with empty strings instead of None
    df[column] = df[column].fillna("")

    # Create dummy columns with 0
    for desejo in arrayDeDesejos:
        nomeDummy = f"{column}_{desejo}"
        df[nomeDummy] = 0

    # Use vectorized operations to set the dummy columns
    for desejo in arrayDeDesejos:
        nomeDummy = f"{column}_{desejo}"
        df[nomeDummy] = df[column].apply(lambda x: 1 if desejo in x else 0)

    return df

# # Esta função transforma múltiplas categorias de linhas de uma coluna em colunas com valores de uma outra coluna
# # Ela espera por parametro um dataframe, 
# #  uma unica coluna de referência com as categorias, uma única coluna com os valores que preencherão as células, 
# #   e uma lista das colunas esperadas
# def pivot_column(df: pd.DataFrame, columnLabels:str = "", columnValues:str = "", arrayDeDesejos:list = []) -> pd.DataFrame:
#     for desejo in arrayDeDesejos:
#         # nomePivot = column+"_"+desejo
#         nomePivot = desejo
#         df[nomePivot] = np.nan
#     for i in range(len(df)):
#         # for j in range(len(arrayDeDesejos)):
#         for desejo in arrayDeDesejos:
#             nomePivot = desejo
#             # nomePivot = arrayDeDesejos[j]
#             # if arrayDeDesejos[j] == df[columnLabels].loc[i]:
#             if df[columnLabels].loc[i] == desejo:
#                 df[nomePivot].loc[i] = df[columnValues].loc[i]
#             else:
#                 df[nomePivot].loc[i] = np.nan
#     # for j in range(len(arrayDeDesejos)):
#     #     # nomePivot = columnLabels+"_"+arrayDeDesejos[j]
#     #     nomePivot = arrayDeDesejos[j]
#     #     df[nomePivot] = np.nan
#     #     for i in range(len(df)):
#     #         if arrayDeDesejos[j] == df[columnLabels].loc[i]:
#     #             df[nomePivot].loc[i] = df[columnValues].loc[i]
#     #         else:
#     #             df[nomePivot].loc[i] = np.nan
#     return df

def pivot_column_vectorized(df: pd.DataFrame, columnLabels: str = "", columnValues: str = "", arrayDeDesejos: list = []) -> pd.DataFrame:
    # Create columns with NaN
    df[arrayDeDesejos] = pd.NA

    # Use vectorized operations to fill the columns
    for desejo in arrayDeDesejos:
        mask = df[columnLabels] == desejo
        df.loc[mask, desejo] = df.loc[mask, columnValues]

    return df


# Esta função adiciona um caracter ou uma substring no final dos dados de uma coluna.
# Ela espera por parametro um dataframe, uma coluna e um caracter
def adiciona_caracter_fim_coluna(df: pd.DataFrame, column: str, caracter: str) -> pd.DataFrame:
    df[column] += caracter
    return df


# Esta Função arredonda o numero de ponto flutuante e transforma ele em um numero inteiro
# Ela espera como parametro um dataframe e uma coluna ou lista de colunas na qual ela deve operara
def round_numbers(df: pd.DataFrame, column: str = "", arrayColumns:list = [], casasDecimais: int = 2) -> pd.DataFrame:
    if column != "":
        arrayColumns.append(column)
    for column in arrayColumns:
        df[column] = df[column].astype(float)
        df[column] = df[column].round(casasDecimais)
    return df


# Formata a string para se transformar em um numero com ponto flutuante
# Ela espera receber um dataframe, e uma coluna a ser operada ou uma lista de colunas a serem processadas
def decimal_to_float(df: pd.DataFrame, column: str = "", arrayColumns:list = []) -> pd.DataFrame:
    if column != "":
        arrayColumns.append(column)
    for column in arrayColumns:
        df[column] = df[column].astype(str)
        df[column] = df[column].str.replace(",", ".")
        df[column] = df[column].str.replace("None", "0")
        df[column].fillna("0", inplace=True)
        df[column] = df[column].astype(float)
    return df


# Formata o dado para ser interpretado como uma string
# Ela espera receber um dataframe, e uma coluna a ser operada ou uma lista de colunas a serem processadas
def to_str_format(df: pd.DataFrame, column:str = "", arrayColumns:list = []) -> pd.DataFrame:
    if column != "":
        arrayColumns.append(column)
    for column in arrayColumns:
        df[column] = df[column].astype(str)
    return df


# A função verifica as colunas de temperatura maxima e temperatura minima, e exclui as linhas com dados acima do normal ou abaixo do normal
# Ela espera receber um dataframe, e uma coluna de temperatura maxima e uma coluna de temperatura minima
def remove_anormal_temp(df: pd.DataFrame, maxTempColumn:str  = "TEMP_max", minTempColumn:str = "TEMP_min") -> pd.DataFrame:
    df[maxTempColumn] = df[maxTempColumn].apply(lambda x: x if(x < 45) else None)
    df[minTempColumn] = df[minTempColumn].apply(lambda x: x if(x > 24) else None)
    return df


# Esta função recebe um dataframe e computa ele olhando para as colunas de maxtemp e mintemp e cria uma coluna onde indica caso o paciente tenha tido febre.
# Ela espera receber um dataframe, e uma coluna de temperatura maxima e uma coluna de temperatura minima
def febre_computed(df: pd.DataFrame, maxTempColumn:str = "TEMP_max", minTempColumn: str = "TEMP_min") -> pd.DataFrame:
    df["FEBRE COMPUTED"] = 0
    for i in range(len(df)):
        df["FEBRE COMPUTED"].loc[i] = 1 if(df[maxTempColumn].loc[i] >= 38.0) else 0
    return df


# Essa função faz a operacao de encode e decode em uma coluna ou varias colunas desejadas
# Eela espera receber um dataframe, um array de colunas ou uma unica coluna
def url_encode_decode(df:pd.DataFrame, arrayColumns:list = [], column:str = "") -> pd.DataFrame:
    import urllib.parse 
    if column != "":
        arrayColumns.append(column)
    for column in arrayColumns:
        df[column] = df[column].apply(lambda x: urllib.parse.quote(x))
        df[column] = df[column].apply(lambda x: urllib.parse.unquote(x))
    return df


# Ela espera receber um dataframe, um array de colunas ou uma unica coluna
def xml_escape(df:pd.DataFrame, arrayColumns:list = [], column:str = "") -> pd.DataFrame:
    from xml.sax.saxutils import escape
    if column != "":
        arrayColumns.append(column)
    for column in arrayColumns:
        df[column] = df[column].apply(lambda x: escape(x))
    return df


# Ela espera receber um dataframe, um array de colunas ou uma unica coluna
def xml_unescape(df:pd.DataFrame, arrayColumns:list = [], column:str = "") -> pd.DataFrame:
    from xml.sax.saxutils import unescape
    if column != "":
        arrayColumns.append(column)
    for column in arrayColumns:
        df[column] = df[column].apply(lambda x: unescape(x))
    return df


#Essa funcão recebe uma coluna de horario e a incrementa em numero de horas desejadas
# Ela espera como parametro, um dataframe, uma coluna ou um array de nomes de colunas e o numero de horas a serem incrementados em todas as colunas
def incrise_by_n_hours(df:pd.DataFrame, column:str = "", arrayColumns:list = [], hours: int = 0) -> pd.DataFrame:
    if column != "":
        arrayColumns.append(column)
    for column in arrayColumns:
        df[column] = pd.to_datetime(df[column])
        increse = pd.Timedelta(hours= hours)
        df[column] += increse
    return df


# Essa funcao espera receber os nomes da colunas que devem ser criadas uma nova como _copy
def copy_columns(df: pd.DataFrame, column: str = "", arrayColumns: list = []) -> pd.DataFrame:
    if column != "":
        arrayColumns.append(column)
    for column in arrayColumns:
        destino = column + "_copy"
        df[destino] = df[column]
    return df

# Essa funçao recebe um array com varios nomes de colunas e concatena informacao deles dentro de uma unica coluna
def fold_multiple_columns_into_one(df: pd.DataFrame, columnDestiny: str = "", columnsToFold: list = [], separator: str = "", evidence_column_name: str= "") -> pd.DataFrame:
    if columnDestiny not in df.columns:
        df[columnDestiny] = None
    for column in columnsToFold:
        df[columnDestiny] += separator + df[column]
    df = trim(df= df, column= columnDestiny)
    df[evidence_column_name] = None
    for index, row in df.iterrows():
        for col in columnsToFold:
            if pd.notna(row[col]):
                df.at[index, evidence_column_name] = col
                break
    # df.drop(columns=columnsToFold, inplace=True)
    return df



# Essa funçao recebe um array com varios nomes de colunas e concatena informacao deles dentro de uma unica coluna
def fold_multiple_columns_into_one_v2(df: pd.DataFrame, columnFoldName: str = "", columnFoldValue: str= "", columnsToFold: list = []) -> pd.DataFrame:
    df[columnFoldName] = ''
    df[columnFoldValue] = ''
    # for index, row in df.iterrows():
    for i in range(len(df)):
        for col in columnsToFold:
            # if pd.notna(row[col]):
            #     row[columnFoldName] = str(col)
            #     row[columnFoldValue] = str(row[col])
            if df[col].loc[i]:
                df[columnFoldName].loc[i] = col
                df[columnFoldValue].loc[i] = df[col].loc[i]
    return df


def fold_multiple_columns_into_one_v3(df: pd.DataFrame, columnFoldName: str = "", columnValueName: str= "", arrayColumnIds: list = [], arrayColumnValues: list = [], col_level=None) -> pd.DataFrame:
    df = df.melt(id_vars=[arrayColumnIds], value_vars=[arrayColumnValues], var_name= columnFoldName, value_name= columnValueName, col_level= col_level)
    # df = rename_columns({"variable": columnFoldName, "value": columnValueName})
    return df


# Essa funçao recebe um array com varios nomes de colunas e concatena informacao deles dentro de uma unica coluna
def fold_multiple_columns_into_one_v4(df: pd.DataFrame, columnFoldName: str = "", columnValueName: str= "", arrayColumnIds: list = [], arrayColumnValues: list = []) -> pd.DataFrame:
    df[columnFoldName] = ''
    df[columnValueName] = ''

    df_fold = pd.DataFrame(columns = df.columns)

    for i in range(len(df)):
        for col in arrayColumnValues:
            if df[col].loc[i]:
                new_row = pd.DataFrame([[df[id].loc[i] for id in arrayColumnIds] + [col] + [df[col].loc[i]]], columns=arrayColumnIds + [columnFoldName] + [columnValueName])
                df_fold = pd.concat([df_fold, new_row], ignore_index=True)
    return df_fold



# https://gist.github.com/TariqAHassan/fc77c00efef4897241f49e61ddbede9e
def combine_lists(frames):
    from itertools import chain

    # N = total # of rows to collate
    # def fast_flatten(input_list):
    #     a=list(chain.from_iterable(input_list))
    #     a += [False] * (N - len(a)) # collating logical arrays - missing values are replaced with False
    #     return list(a)

    def fast_flatten(input_list):
        return list(chain.from_iterable(input_list))
    
    # COLUMN_NAMES = [frames[i].columns for i in range(len(frames))]
    # COL_NAMES=list(set(list(chain(*COLUMN_NAMES))))
    COL_NAMES = frames[0].columns
    df_dict = dict.fromkeys(COL_NAMES, [])
    for col in COL_NAMES:
        # extracted = (frame[col] for frame in frames if col in frame.columns.tolist())
        extracted = (frame[col] for frame in frames)
        df_dict[col] = fast_flatten(extracted)
    Df_new = pd.DataFrame.from_dict(df_dict)[COL_NAMES]
    return Df_new 



# Essa funçao recebe um array com varios nomes de colunas e concatena informacao deles dentro de uma unica coluna
def fold_multiple_columns_into_one_v5(df: pd.DataFrame, columnFoldName: str = "", columnValueName: str= "", arrayColumnIds: list = [], arrayColumnValues: list = []) -> pd.DataFrame:
    df[columnFoldName] = ''
    df[columnValueName] = ''

    # create a copy of a dataframe that is empty, but has same types from the other df
    # df_fold = df.copy(deep=False)
    df_fold = pd.DataFrame(columns = df[arrayColumnIds + [columnFoldName] + [columnValueName]].columns).astype(df[arrayColumnIds + [columnFoldName] + [columnValueName]].dtypes.to_dict())
    df_fold[columnFoldName] = df_fold[columnFoldName].astype('object')
    df_fold[columnValueName] = df_fold[columnValueName].astype('object')

    for i in range(len(df)):
        for col in arrayColumnValues:
            if df[col].loc[i]:
                # new_row = pd.DataFrame([[df[id].loc[i] for id in arrayColumnIds] + [col] + [df[col].loc[i]]], 
                new_row = pd.DataFrame([[df[id].loc[i] for id in arrayColumnIds] + [col] + [df[col].loc[i]]], 
                                       columns=arrayColumnIds + [columnFoldName] + [columnValueName]) #.astype(df.dtypes.to_dict())
                new_row = new_row.astype(df[arrayColumnIds].dtypes.to_dict())
                new_row[columnFoldName] = new_row[columnFoldName].astype('object')
                new_row[columnValueName] = new_row[columnValueName].astype('object')
                df_fold = combine_lists([df_fold, new_row])
    
    return df_fold


def fold_multiple_columns_into_one_v6(df: pd.DataFrame, columnFoldName: str = "", columnValueName: str= "", arrayColumnIds: list = [], arrayColumnValues: list = []) -> pd.DataFrame:

    # Create a list to store data for the new DataFrame
    new_data = []

    for i in range(len(df)):
        for col in arrayColumnValues:
            if df.at[i, col]:
                # Convert integer values to strings
                new_row_data = ([df.at[i, id] for id in arrayColumnIds]) + [col, df.at[i, col]]
                new_row_data = [str(val) if isinstance(val, int) else val for val in new_row_data]
                new_data.append(new_row_data)

    # Create the new DataFrame using the list of data
    df_fold = pd.DataFrame(new_data, columns=arrayColumnIds + [columnFoldName] + [columnValueName])

    return df_fold


def remove_rows_containing(df: pd.DataFrame, column_name: str, terms: list = None, exact_match: bool = False, regex: re = None) -> pd.DataFrame:

    if terms is None and regex is None:
        return df

    if regex is not None:
        mask = ~df[column_name].str.contains(regex, case=False)
    elif exact_match:
        mask = ~df[column_name].isin([terms])
    else:
        mask = ~df[column_name].str.contains('|'.join(map(re.escape, terms)), case=False)

    df_filtered = df[mask]
    return df_filtered


# Esta função recebe uma STRING e retorna uma STRING sem acentos
def remove_accents(input_str):
    # Normalize the input string using NFD decomposition
    nfkd_form = unicodedata.normalize('NFD', input_str)
    # Filter out the non-spacing marks
    return ''.join(c for c in nfkd_form if unicodedata.category(c) != 'Mn')

def search_pattern(text, pattern_pos, pattern_neg):
    sent_pos = []
    sent_neg = []

    pattern_neg = re.compile(pattern_neg)
    pattern_pos = re.compile(pattern_pos)

    # para melhorar a performance, toda a lista de sentenças é tratada como um único #texto. Na regex foram adicionados delimitadores de sentença assim, a busca será
    # feita a partir de cada sentença, porém, sem iterações
    search_pos = re.findall(pattern_pos, text)

    if search_pos:
        if isinstance(search_pos[0], tuple):
            # re.findall cria uma lista com todos os grupos procurados, sendo
            # necessário extrair apenas os grupos encontrados da lista
            sent_pos = [list(filter(None, i))[0] for i in search_pos]
            # sent_pos = [i[0] for i in sent_pos]
        else:
            sent_pos = search_pos
        
        search_neg = re.findall(pattern_neg, str(sent_pos))

        # caso existam padrões negativos é verificado se existem também padrões
        # negativos na sentença
        if search_neg:
            # re.findall cria uma lista com todos os grupos procurados, sendo
            # necessário extrair apenas os grupos encontrados da lista
            sent_neg = [list(filter(None, i))[0] for i in search_neg]
            # sent_neg = [i[0] for i in sent_neg]

    # são excluídas as sentenças positivas que possuem uma negação anterior
    sent_pos = [x for x in sent_pos if x not in sent_neg]

    # é feito o calculo da proporcao de sent. positivas encontradas vs
    # sent. negativas encontradas
    len_pos = len(sent_pos)
    len_neg = len(sent_neg)
    if len_pos > 0:
        if len_neg > 0:
            proporcao = str(round(len_pos / (len_pos + len_neg), 2))
        else:
            proporcao = '1'
    else:
        proporcao = '0'

    return proporcao, sent_pos, sent_neg, len_pos

def operando(row: pd.Series, criterios: list):
    janela_evolucoes = row["new_sentence"]
    for cri in criterios:
        pattern_pos, pattern_neg = regexPattern.regex_search(cri)

        proporcao, sent_pos, sent_neg, sent_pos_count = search_pattern(
            janela_evolucoes, pattern_pos, pattern_neg
        )
        row[cri] = proporcao
        row[f"{cri}_sent_pos"] = sent_pos
        row[f"{cri}_sent_neg"] = sent_neg
        row[f"{cri}_sent_pos_count"] = sent_pos_count

    return row

def creat_row(df: pd.DataFrame, criterios: list) -> pd.DataFrame:
    colunas_string = [f"{cri}"  for cri in criterios] + [f"{cri}_sent_pos"  for cri in criterios] + [f"{cri}_sent_neg"  for cri in criterios]
    colunas_numero = [f"{cri}_sent_pos_count" for cri in criterios]
    df[colunas_string] = ''
    df[colunas_numero] = 0
    return df


def creat_row_assign(df: pd.DataFrame, criterios: list, mustCapturePos: bool = True, mustCaptureNeg: bool = True, mustCount: bool = True) -> pd.DataFrame:
    if not mustCapturePos and not mustCaptureNeg and not mustCount:
        return df

    updates = {}

    if mustCapturePos:
        updates |= {
            f"{cri}_sent_pos": '' for cri in criterios
        }

    if mustCaptureNeg:
        updates |= {
            f"{cri}_sent_neg": '' for cri in criterios
        }
    
    if mustCount:
        updates |= {
            f"{cri}_sent_pos_count": 0 for cri in criterios
        } | {
            f"{cri}": '' for cri in criterios
        }

    return df.assign(**updates)

def creat_row_criterios_with_suffix_assign(df: pd.DataFrame, criterios: list[str], suffix: list[str], mustCapturePos: bool = True, mustCaptureNeg: bool = True, mustCount: bool = True) -> pd.DataFrame:
    if not mustCapturePos and not mustCaptureNeg and not mustCount:
        return df

    updates = {}

    if mustCapturePos:
        updates |= {
            f"{cri}{s}_sent_pos": '' for cri in criterios for s in suffix
        }

    if mustCaptureNeg:
        updates |= {
            f"{cri}{s}_sent_neg": '' for cri in criterios for s in suffix
        }
    
    if mustCount:
        updates |= {
            f"{cri}{s}_sent_pos_count": 0 for cri in criterios for s in suffix
        } | {
            f"{cri}{s}": None for cri in criterios for s in suffix
        }

    return df.assign(**updates)

import time 

def operando_vetorizado_re(df: pd.DataFrame, criterios: list):
    for cri in criterios:
        pattern_pos, pattern_neg = regexPattern.regex_search(cri)
        
        pattern_pos_re = re.compile(pattern_pos)
        pattern_neg_re = re.compile(pattern_neg)
        
        # Extrai todas as sentenças positivas
        all_pos = df["new_sentence"].str.findall(pattern_pos_re)
        
        all_pos_filtered = all_pos.apply(
            lambda lst: [list(filter(None, x))[0] if isinstance(x, tuple) else x for x in lst]
        )
        
        # Extrai as negativas dentro das positivas
        all_neg = all_pos_filtered.astype(str).str.findall(pattern_neg_re)
        
        all_neg_filtered = all_neg.apply(
            lambda lst: [(list(filter(None, x))[0] if isinstance(x, tuple) else x) for x in lst]
        )
        
        # Remove negativas de dentro das positivas
        final_pos = [
            [x for x in pos if x not in neg]
            for pos, neg in zip(all_pos_filtered, all_neg_filtered)
        ]
        
        count_pos = [len(x) for x in final_pos]
        
        count_neg = [len(x) for x in all_neg_filtered]
        
        proporcao = [
            str(round(p / (p + n), 2)) if p > 0 and n > 0 else ('1' if p > 0 else '0')
            for p, n in zip(count_pos, count_neg)
        ]
        
        # Atribui colunas ao DataFrame
        df[cri] = proporcao
        df[f"{cri}_sent_pos"] = final_pos
        df[f"{cri}_sent_neg"] = all_neg_filtered
        df[f"{cri}_sent_pos_count"] = count_pos
        
    return df

# =========================
# Nova funç˜ão operando, com o auxilio do chat ele propôs que fosse adicionado sanitização nos regex
# que temos para processamento, para n modificar todos foi criada as funções a seguir
# isso permitiu retirar o tratamento de filtro dos Nones ganhando tempo em nao executar esse filtro
# =========================
_BACKREF_NUM_RE = re.compile(r'(?<!\\)\\[1-9]\d*')  # \1, \2, ... não-escapados
_BACKREF_NAMED_RE = re.compile(r'\(\?P=')          # (?P=name)

def _has_backrefs(pattern: str) -> bool:
    """Detecta backreferences numéricas ou nomeadas."""
    return bool(_BACKREF_NUM_RE.search(pattern) or _BACKREF_NAMED_RE.search(pattern))

def strip_captures(pattern: str) -> str:
    """
    Converte capturas em não-capturantes, preservando lookarounds/flags e grupos já não-capturantes.
    NÃO use se houver backrefs numéricos/nomeados no padrão.
    """
    out = []
    i = 0
    L = len(pattern)
    while i < L:
        c = pattern[i]
        if c == '\\' and i + 1 < L:
            out.append(pattern[i:i+2])
            i += 2
            continue
        if c == '(':
            if i + 1 < L and pattern[i+1] == '?':
                if pattern.startswith('(?P<', i):
                    k = pattern.find('>', i + 4)
                    if k != -1:
                        out.append('(?:')
                        i = k + 1
                        continue
                    out.append('('); i += 1; continue
                else:
                    out.append('('); i += 1; continue
            else:
                out.append('(?:'); i += 1; continue
        out.append(c); i += 1
    return ''.join(out)

def _compile_sanitized(pattern: str) -> Tuple[re.Pattern, bool]:
    """
    Compila o padrão:
      - Se não houver backrefs, remove capturas -> findall retorna str (mode=True)
      - Se houver backrefs, compila cru -> pode retornar tuplas (mode=False)
    """
    can_strip = not _has_backrefs(pattern)
    patt = strip_captures(pattern) if can_strip else pattern
    return re.compile(patt), can_strip

def _first_non_none_from_tuple(t: Tuple[Any, ...]) -> Any:
    """Para fallback (quando não dá para sanitizar): primeiro grupo não vazio."""
    for g in t:
        if g:
            return g
    return None

def _to_curly_braced_str(lst: List[Any]) -> str:
    """
    Serializa mantendo ordem e possíveis duplicatas:
    ["a","a","b"] -> "{'a','a','b'}"
    (usa repr() para preservar aspas internas como no print anterior)
    """
    return '{' + ','.join(repr(x) for x in lst) + '}'

def split_sentences(text):
    if not isinstance(text, str):
        return []

    sentences = re.split(r"(?<=[\.!?])\s+", text.strip())

    cleaned = []
    for s in sentences:
        s = s.strip()

        # remove lixo estrutural
        if len(s) <= 1:
            continue
        if s == ".":
            continue

        cleaned.append(s)

    return cleaned

def operando_vetorizado_re_sanatized(df: pd.DataFrame, criterios: List[str], SAIDA_SENTENCAS_COM_CHAVES: bool = True, mustCapturePos: bool = True, mustCaptureNeg: bool = True, mustCount: bool = True) -> pd.DataFrame:
    if not mustCapturePos and not mustCaptureNeg and not mustCount:
        return df
    
    if "new_sentence" not in df.columns:
        raise KeyError("A coluna 'new_sentence' não foi encontrada no DataFrame.")

    for cri in criterios:
        # 1) Buscar padrões (pos/neg)
        pattern_pos_raw, pattern_neg_raw = regexPattern.regex_search(cri)
        
        # 2) Compilar com/s/ sanitização
        pattern_pos_re, pos_sanitized = _compile_sanitized(pattern_pos_raw)
        pattern_neg_re, neg_sanitized = _compile_sanitized(pattern_neg_raw)
        
        # 3) POSITIVOS
        all_pos = df["new_sentence"].str.findall(pattern_pos_re)
        
        # 4) Normalização positivos
        if pos_sanitized:
            all_pos_filtered = all_pos.tolist()
        else:
            apf = []
            apf_append = apf.append
            for lst in all_pos:
                if not lst:
                    apf_append([]); continue
                cur = []
                cur_append = cur.append
                for item in lst:
                    if isinstance(item, tuple):
                        cur_append(_first_non_none_from_tuple(item))
                    else:
                        cur_append(item)
                apf_append(cur)
            all_pos_filtered = apf

        # 5) NEGATIVOS dentro de cada positiva
        all_neg_filtered = []
        anf_append = all_neg_filtered.append
        for pos_list in all_pos_filtered:
            if not pos_list:
                anf_append([]); continue
            negs = []
            negs_append = negs.append
            for p in pos_list:
                s = p if isinstance(p, str) else ""
                found = pattern_neg_re.findall(s)
                if neg_sanitized:
                    negs.extend(found)
                else:
                    for m in found:
                        if isinstance(m, tuple):
                            negs_append(_first_non_none_from_tuple(m))
                        else:
                            negs_append(m)
            anf_append(negs)

        # 6) Remover negativas de dentro das positivas
        final_pos = []
        fp_append = final_pos.append
        for pos_list, neg_list in zip(all_pos_filtered, all_neg_filtered):
            if not pos_list:
                fp_append([])
            else:
                neg_set = set(neg_list)
                fp_append([x for x in pos_list if x not in neg_set])
        
        if mustCount:
            # 7) Contagens
            count_pos = [len(x) for x in final_pos]
            count_neg = [len(x) for x in all_neg_filtered]

            # 8) Proporção
            proporcao = []
            prop_append = proporcao.append
            for p, n in zip(count_pos, count_neg):
                if p > 0 and n > 0:
                    prop_append(str(round(p / (p + n), 2)))
                else:
                    prop_append('1' if p > 0 else '0')

        # 10) Atribuição
        if mustCount:
            df[cri] = proporcao
            df[f"{cri}_sent_pos_count"] = count_pos

        if mustCapturePos:
            df[f"{cri}_sent_pos"] = final_pos if not SAIDA_SENTENCAS_COM_CHAVES else [_to_curly_braced_str(lst) for lst in final_pos]

        if mustCaptureNeg:
            df[f"{cri}_sent_neg"] = all_neg_filtered if not SAIDA_SENTENCAS_COM_CHAVES else [_to_curly_braced_str(lst) for lst in all_neg_filtered]

    return df

def operando_vetorizado_re_sanatized_with_suffix(df: pd.DataFrame, criterios: List[str], suffix: List[str], SAIDA_SENTENCAS_COM_CHAVES: bool = True, mustCapturePos: bool = True, mustCaptureNeg: bool = True, mustCount: bool = True) -> pd.DataFrame:
    if not mustCapturePos and not mustCaptureNeg and not mustCount:
        return df    

    for suffi in suffix:
        texto_column = f"texto{suffi}"
        if texto_column not in df.columns:
            raise KeyError(f"A coluna '{texto_column}' não foi encontrada no DataFrame.")
        
        for cri in criterios:
            # 1) Buscar padrões (pos/neg)
            pattern_pos_raw, pattern_neg_raw = regexPattern.regex_search(cri)
            
            # 2) Compilar com/s/ sanitização
            pattern_pos_re, pos_sanitized = _compile_sanitized(pattern_pos_raw)
            pattern_neg_re, neg_sanitized = _compile_sanitized(pattern_neg_raw)
            
            # 3) POSITIVOS
            all_pos = df[texto_column].str.findall(pattern_pos_re)
            
            # 4) Normalização positivos
            if pos_sanitized:
                all_pos_filtered = all_pos.tolist()
            else:
                apf = []
                apf_append = apf.append
                for lst in all_pos:
                    if not lst:
                        apf_append([]); continue
                    cur = []
                    cur_append = cur.append
                    for item in lst:
                        if isinstance(item, tuple):
                            cur_append(_first_non_none_from_tuple(item))
                        else:
                            cur_append(item)
                    apf_append(cur)
                all_pos_filtered = apf

            # 5) NEGATIVOS dentro de cada positiva
            all_neg_filtered = []
            anf_append = all_neg_filtered.append
            for pos_list in all_pos_filtered:
                if not pos_list:
                    anf_append([]); continue
                negs = []
                negs_append = negs.append
                for p in pos_list:
                    s = p if isinstance(p, str) else ""
                    found = pattern_neg_re.findall(s)
                    if neg_sanitized:
                        negs.extend(found)
                    else:
                        for m in found:
                            if isinstance(m, tuple):
                                negs_append(_first_non_none_from_tuple(m))
                            else:
                                negs_append(m)
                anf_append(negs)

            # 6) Remover negativas de dentro das positivas
            final_pos = []
            fp_append = final_pos.append
            for pos_list, neg_list in zip(all_pos_filtered, all_neg_filtered):
                if not pos_list:
                    fp_append([])
                else:
                    neg_set = set(neg_list)
                    fp_append([x for x in pos_list if x not in neg_set])
            
            if mustCount:
                # 7) Contagens
                count_pos = [len(x) for x in final_pos]
                count_neg = [len(x) for x in all_neg_filtered]

                # 8) Proporção
                proporcao = []
                prop_append = proporcao.append
                for p, n in zip(count_pos, count_neg):
                    total = p+n
                    if total > 0:
                        prop_append(round(p / total, 2))
                    else:
                        prop_append(None)

            # 9) Atribuição
            if mustCount:
                df[f"{cri}{suffi}"] = proporcao
                df[f"{cri}{suffi}_sent_pos_count"] = count_pos

            if mustCapturePos:
                df[f"{cri}{suffi}_sent_pos"] = final_pos if not SAIDA_SENTENCAS_COM_CHAVES else [_to_curly_braced_str(lst) for lst in final_pos]

            if mustCaptureNeg:
                df[f"{cri}{suffi}_sent_neg"] = all_neg_filtered if not SAIDA_SENTENCAS_COM_CHAVES else [_to_curly_braced_str(lst) for lst in all_neg_filtered]

    return df

def getELKIndexValue(key: str) -> str:
    query = f"select value from elk_indexes where key = '{key}'"
    df = dataRequest.get_data(queryText=query, chunck=None)
    if df is None or len(df) == 0:
        return None
    return df.iloc[0]['value']

def sanitize_document(doc: dict[Any, Any]) -> dict[str, Any]:
    """Garante que todos os valores são serializáveis pelo Elasticsearch."""
    sanitized = {}
    for key, value in doc.items():
        # ✅ Fix 2a: trata NaN e infinitos
        if isinstance(value, float) and (np.isnan(value) or np.isinf(value)):
            sanitized[key] = None
        # ✅ Fix 2b: converte Timestamps para ISO 8601
        elif isinstance(value, (pd.Timestamp, datetime)):
            sanitized[key] = value.isoformat() if not pd.isnull(value) else None
        # ✅ Fix 2c: converte numpy integers/floats para tipos nativos Python
        elif isinstance(value, (np.integer,)):
            sanitized[key] = int(value)
        elif isinstance(value, (np.floating,)):
            sanitized[key] = float(value) if not np.isnan(value) else None
        # ✅ Fix 2d: converte numpy booleans
        elif isinstance(value, np.bool_):
            sanitized[key] = bool(value)
        else:
            sanitized[key] = value
    return sanitized

def generate_actions(chunk, index_name):
    # Preenche valores nulos por tipo de coluna
    for col in chunk.columns:
        if pd.api.types.is_datetime64_any_dtype(chunk[col]):
            pass  # datas NaT são tratadas no sanitize_document
        elif chunk[col].dtype == 'object':
            chunk[col] = chunk[col].where(pd.notnull(chunk[col]), None)
        elif chunk[col].dtype in ['float64', 'float32']:
            chunk[col] = chunk[col].where(pd.notnull(chunk[col]), None)

    actions = [
        {
            "_index": index_name,
            "_source": sanitize_document(row.to_dict())
        }
        for _, row in chunk.iterrows()
    ]
    return actions

def wait_for_index_health(client, index_name: str, status: str = "yellow", timeout: str = "30s"):
    """Aguarda o shard primário do index ficar ativo antes de iniciar as escritas em bulk."""
    try:
        client.cluster.health(index=index_name, wait_for_status=status, timeout=timeout)
    except Exception as e:
        print(f"⚠️ Timeout aguardando index '{index_name}' ficar '{status}': {e}")

def _resumo_falha_bulk(info: dict) -> str:
    """Motivo de uma falha do parallel_bulk sem o conteúdo do documento -- o 'info' original
    traz o documento inteiro (texto clínico, prontuário), que não deve ir para o log."""
    detalhe = next(iter(info.values()), {}) if isinstance(info, dict) else {}
    status = detalhe.get("status")
    exc = detalhe.get("exception")
    if exc is not None:
        # a requisição do lote inteiro foi recusada antes de chegar ao índice (rede, proxy, WAF...)
        # e todos os documentos do lote recebem o mesmo erro; o header Server diz quem recusou
        headers = getattr(getattr(exc, "meta", None), "headers", None) or {}
        servidor = headers.get("Server") or headers.get("server")
        return f"status={status} lote recusado: {type(exc).__name__}" + (f" (Server: {servidor})" if servidor else "")
    erro = detalhe.get("error")
    if isinstance(erro, dict):
        erro = f"{erro.get('type')}: {str(erro.get('reason'))[:200]}"
    return f"status={status} {erro}"

def _ref_documento_bulk(action: dict) -> str:
    source = action.get("_source") or {}
    return ",".join(f"{k}={source[k]}" for k in ("id", "paciente_id", "id_enterprise") if source.get(k) is not None) or "sem id"

def _agrupar_falhas_bulk(failed: list) -> dict:
    """{motivo: [identificação de cada documento]} -- para logar uma linha por motivo, não por documento."""
    falhas_por_motivo: dict = {}
    for action, info in failed:
        falhas_por_motivo.setdefault(_resumo_falha_bulk(info), []).append(_ref_documento_bulk(action))
    return falhas_por_motivo

def _enviar_bulk(client, actions: list, thread_count: int) -> list:
    """Envia via parallel_bulk e devolve [(action, info)] só dos documentos que falharam."""
    results = parallel_bulk(
        client,
        actions,
        thread_count=thread_count,
        raise_on_error=False,
        raise_on_exception=False
    )
    return [(action, info) for action, (success, info) in zip(actions, results) if not success]

def _lote_recusado_403(info: dict) -> bool:
    detalhe = next(iter(info.values()), {}) if isinstance(info, dict) else {}
    return detalhe.get("exception") is not None and detalhe.get("status") == 403

def _isolar_recusados_403(client, failed: list, context: str, max_reenvios: int = 64) -> list:
    """Um 403 na requisição (ex.: WAF da AWS barrando o conteúdo de algum documento) derruba o lote
    inteiro, ~500 documentos, por causa de um só. Divide os recusados ao meio e reenvia até isolar
    os que causam a recusa, para o resto ser indexado. Reenviar não duplica nada: um lote recusado
    nunca chegou ao índice. max_reenvios limita o custo caso o 403 seja geral (bloqueio de IP,
    credencial) e não de conteúdo. Devolve as falhas que sobraram."""
    recusados = [(a, i) for a, i in failed if _lote_recusado_403(i)]
    if not recusados:
        return failed

    sobras = [(a, i) for a, i in failed if not _lote_recusado_403(i)]
    sobras_iniciais = len(sobras)
    fila = [recusados]
    reenvios = sozinhos = 0
    while fila:
        grupo = fila.pop()
        if len(grupo) == 1 or reenvios >= max_reenvios:
            sozinhos += len(grupo) == 1
            sobras.extend(grupo)
            continue
        meio = len(grupo) // 2
        for metade in (grupo[:meio], grupo[meio:]):
            reenvios += 1
            falhas = _enviar_bulk(client, [a for a, _ in metade], thread_count=1)
            sobras.extend((a, i) for a, i in falhas if not _lote_recusado_403(i))
            ainda_recusados = [(a, i) for a, i in falhas if _lote_recusado_403(i)]
            if ainda_recusados:
                fila.append(ainda_recusados)

    indexados = len(recusados) - (len(sobras) - sobras_iniciais)
    if indexados == 0 and reenvios >= max_reenvios:
        print(f"🔎 {context}: {len(recusados)} docs recusados com 403 e nenhuma parte passou em {reenvios} reenvios -- parece bloqueio geral (IP, credencial), não um documento específico")
    else:
        print(f"🔎 {context}: {len(recusados)} docs em lotes recusados com 403 -> {indexados} indexados após dividir o lote, {sozinhos} recusados mesmo sozinhos ({reenvios} reenvios)")
    return sobras

def bulk_upload_with_retry(client, actions: list, context: str = "", max_retries: int = 2, thread_count: int = 1) -> Tuple[int, int]:
    """Executa parallel_bulk retentando os documentos que falharem, em vez de descartá-los silenciosamente.

    Se ainda sobrar lote recusado com 403 depois das retentativas, divide o lote para indexar os
    documentos inocentes e isolar os que causam a recusa (ver _isolar_recusados_403).

    Os logs de falha trazem só o motivo e a identificação (id, paciente_id, id_enterprise) dos
    documentos, nunca o conteúdo.

    Retorna (total_sucesso, total_falha_definitiva).
    """
    total = len(actions)
    pending = actions
    for attempt in range(max_retries + 1):
        failed = _enviar_bulk(client, pending, thread_count)
        if not failed:
            return total, 0

        if attempt < max_retries:
            motivos = "; ".join(f"{motivo} ({len(refs)} docs)" for motivo, refs in _agrupar_falhas_bulk(failed).items())
            print(f"⚠️ {len(failed)} documentos falharam em {context}, retentativa {attempt + 1}/{max_retries}... motivos: {motivos}")
            time.sleep(5 * (attempt + 1))
            pending = [action for action, _ in failed]

    failed = _isolar_recusados_403(client, failed, context)
    if failed:
        print(f"🔴🔴🔴 {len(failed)} documentos falharam definitivamente em {context} 🔴🔴🔴")
        for motivo, refs in _agrupar_falhas_bulk(failed).items():
            print(f"🔴 {motivo} -> {len(refs)} docs: {' | '.join(refs)}")
    return total - len(failed), len(failed)

