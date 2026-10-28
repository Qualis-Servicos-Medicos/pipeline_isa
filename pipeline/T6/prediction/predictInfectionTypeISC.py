from typing import Any
from ImpararePackage import dataRequest
import pandas as pd
import joblib
from multiprocessing import Pool, cpu_count

def force_single_thread_model(model: Any) -> Any:
    if hasattr(model, "get_params") and hasattr(model, "set_params"):
        params = model.get_params(deep=False)
        if "n_jobs" in params:
            model.set_params(n_jobs=1)
    return model

_model_forest = None

def _init_worker(model_path: str):
    global _model_forest
    _model_forest = force_single_thread_model(joblib.load(model_path))

def worker (c: pd.DataFrame):
    df_basic_info = c[["prontuario", "dia", "id_enterprise"]].copy()

    colunas_manter = _model_forest.feature_names_in_

    proba = _model_forest.predict_proba(c[colunas_manter])

    df_basic_info['proba_1'] = proba[:, 1].round(4) # Probabilidade de ser IRAS no paciente e no dia
    df_basic_info['prediction'] = (proba[:, 1] >= 0.5).astype(int)

    dataRequest.set_data_on_sql(df= df_basic_info, nomeTabelaDestino= "imparare2_new_isa_set_scored_casos_isc_or_others", if_exists= "append")

def main():
    replace = True
    if replace:
        create_query = """
            DROP TABLE IF EXISTS imparare2_new_isa_set_scored_casos_isc_or_others;
            CREATE UNLOGGED TABLE imparare2_new_isa_set_scored_casos_isc_or_others (
                prontuario INTEGER,
                dia DATE,
                id_enterprise SMALLINT,
                proba_1 FLOAT,
                prediction INTEGER
            );
        """
        dataRequest.execute(create_query)
    
    query = """
        select 
            distinct on (idlf.prontuario, idlf.dia, idlf.id_enterprise)
            idlf.*
        from imparare2_dataset_label_full idlf 
        inner join imparare2_new_isa_set_scored_casos_infeccao inf
            on idlf.prontuario = inf.prontuario 
                and idlf.dia = inf.dia 
                and idlf.id_enterprise = inf.id_enterprise
        where inf.proba_1 > 0.4
    """
    
    path = "/workspaces/pipeline_isa/ScriptsLibrary/pipeline/T6"
    model_path = f"{path}/models/modelo1_caso_isc_or_others.joblib"

    df_iterator = dataRequest.get_data(queryText= query, chunck= 2000)

    with Pool(processes= cpu_count(), initializer= _init_worker, initargs= (model_path,)) as pool:
        for _ in pool.imap_unordered(worker, df_iterator):
            pass

if __name__ == "__main__":
    main()