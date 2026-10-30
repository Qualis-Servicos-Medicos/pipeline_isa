from ImpararePackage import dataRequest
from ImpararePackage import maestro
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
# import tensorflow as tf
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import accuracy_score
from sklearn.metrics import confusion_matrix
from sklearn.metrics import classification_report
from sklearn.preprocessing import scale
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.calibration import CalibratedClassifierCV
import numpy as np
import joblib
from datetime import timedelta
from sklearn.metrics import precision_recall_curve
import matplotlib.pyplot as plt


def main(testing: bool = True):
    GABARITO = "caso infeccao"
    x = None
    path = "/workspaces/pipeline_isa/ScriptsLibrary/pipeline/T6"
    query = f"""
        SELECT 
            pa."{GABARITO}",
            dtf.*
        FROM imparare2_dataset_label_full  dtf
        inner join new_avaliacao_padrao_ouro pa
            on dtf.prontuario = pa.registro 
                and dtf.dia = pa.dt_infeccao
        where dtf.evo_count_dia > 0
    """
    
    x = dataRequest.get_data(queryText= query, chunck= None)
    if not isinstance(x, pd.DataFrame):
        print("Necessário carregar um pandas dataframe")
        return
    
    x.to_feather(f"{path}/data/dados_treino_modelo_infeccao.feather")
    y = x[GABARITO]
    meta = x[["prontuario", "dia", "id_enterprise"]].copy()
    # x.drop(columns= [GABARITO, "dia", "prontuario"], inplace= True)
    x.drop(columns= [GABARITO, "dia", "prontuario", "idade_anos", "id_enterprise", "cirurgia_risco_infeccao_90_dias", "cirurgia_risco_infeccao_30_dias"]+list(filter(lambda z: "sent_pos_count" in str(z), x.columns.tolist())), inplace= True)
 
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size= 0.2, random_state= 42, stratify= y) # , shuffle= True)
    
    model = RandomForestClassifier(
        random_state= 22, 
        n_estimators= 200, # 200
        criterion= "entropy",
        # max_leaf_nodes= 120,
        # ccp_alpha=0.0002,
        min_samples_leaf= 5, # 8
        max_samples= 0.8,
        n_jobs=-1, 
        max_depth= None,
        max_features= 'sqrt',
        class_weight= {0: 1.0, 1: 20.0} # "balanced"
    )

    model = model.fit(x_train, y_train)

    predictions = model.predict(x_train)
    print("FIM Train")
    print("Train Mimnha Accuracy: ", accuracy_score(y_train, predictions))
    print("TrainConfusion Matrix: \n", confusion_matrix(y_train, predictions, labels= [0,1]))
    print(classification_report(y_train, predictions))

    predictions = model.predict(x_test)
    print("FIM TEST")
    print("TEST Mimnha Accuracy: ", accuracy_score(y_test, predictions))
    print("TESTConfusion Matrix: \n", confusion_matrix(y_test, predictions, labels= [0,1]))
    print(classification_report(y_test, predictions))

    erros = meta.loc[x_test.index].copy()
    erros["y_true"] = y_test.values
    erros["y_pred"] = predictions
    erros["proba_1"] = model.predict_proba(x_test)[:, 1]

    falsos_positivos = erros[(erros["y_true"] == 0) & (erros["y_pred"] == 1)]
    falsos_negativos = erros[(erros["y_true"] == 1) & (erros["y_pred"] == 0)]

    falsos_positivos[["prontuario", "dia", "id_enterprise"]].to_csv(f"{path}/falsos_positivos.csv", sep= ";", index= False)
    falsos_negativos[["prontuario", "dia", "id_enterprise"]].to_csv(f"{path}/falsos_negativos.csv", sep= ";", index= False)
    print(f"Falsos positivos: {len(falsos_positivos)} | Falsos negativos: {len(falsos_negativos)}")

    if True:
        precision, recall, thresholds = precision_recall_curve(y_test, predictions)
        f1_scores = 2 * (precision * recall) / (precision + recall)
    
        plt.figure(figsize=(8, 6))
        plt.plot(thresholds, precision[:-1], label='Precision', color='blue')
        plt.plot(thresholds, recall[:-1], label='Recall', color='green')
        plt.plot(thresholds, f1_scores[:-1], label='F1-Score', color='red')
        plt.xlabel("Threshold")
        plt.ylabel("Score")
        plt.title("Precision, Recall, and F1-Score vs Threshold")
        plt.legend()
        plt.grid()
        plt.show()
    
        best_threshold_index = np.argmax(f1_scores)
        best_threshold = thresholds[best_threshold_index]
        print(f"Best Threshold: {best_threshold}")
    
        y_pred_best_threshold = (predictions >= best_threshold).astype(int)
        print("Confusion Matrix (Best Threshold):\n", confusion_matrix(y_test, y_pred_best_threshold))
        print("Classification Report (Best Threshold):\n", classification_report(y_test, y_pred_best_threshold))
        joblib.dump(model, f"{path}/models/modelo1_caso_infeccao.joblib")
        
        predictions = model.predict_proba(x_test)

        dicionario = {
            "proba_1": predictions[:, 1]
        }

        df = pd.DataFrame(dicionario)
        df["count"] = 1
        df["proba_1"] = df["proba_1"].values.round(2)

        df_result_GROUPED = df.groupby(by="proba_1").sum()
        print(df_result_GROUPED)
        df_result_GROUPED.to_csv(f"{path}/distribution.csv", sep= ";")

        plt.figure(figsize=(20, 10))
        plt.plot(df_result_GROUPED["count"], label= "Acontecimentos")
        plt.title("frequencia de proba")
        plt.ylabel("repeticoes")
        plt.xlabel("proba")
        plt.legend()
        plt.show()

        importance_series = pd.Series(model.feature_importances_, index=x_train.columns).sort_values(ascending=False)
        importance_series.to_csv('importancias_random_forest.csv', index=True)
        top20_features = importance_series.head(20).index.tolist()

        target_col = GABARITO
        plot_base = x_train[top20_features].astype(float).copy()
        plot_base[target_col] = y_train
        plot_base[target_col] = plot_base[target_col].astype(str)
        classes = sorted(plot_base[target_col].dropna().unique())
        colors = ["#1f77b4", "#d62728", "#2ca02c", "#ff7f0e"]

        n_cols = 4
        n_rows = (len(top20_features) + n_cols - 1) // n_cols
        fig, axes = plt.subplots(n_rows, n_cols, figsize=(18, 2.2 * n_rows))
        axes = axes.flatten() if hasattr(axes, "flatten") else [axes]

        for idx, feature in enumerate(top20_features):
            ax = axes[idx]
            feature_df = plot_base[[feature, target_col]].dropna()

            for i, classe in enumerate(classes):
                serie = feature_df.loc[feature_df[target_col] == classe, feature]
                ax.hist(
                    serie,
                    bins=50,
                    alpha=0.35,
                    density=True,
                    label=f"classe = {classe}",
                    color=colors[i % len(colors)],
                    edgecolor="white",
                    linewidth=0.5,
                )

            # ax.set_title()
            ax.set_xlabel(f"{feature} (imp={importance_series.loc[feature]:.4f})")
            ax.set_ylabel("Densidade")
            ax.grid(alpha=0.2)

        # Remove eixos vazios (caso existam)
        for j in range(len(top20_features), len(axes)):
            fig.delaxes(axes[j])

        handles, labels = axes[0].get_legend_handles_labels()
        fig.legend(handles, labels, loc="upper right")
        fig.suptitle(f"Top 20 features por importancia: distribuicao por classe de {GABARITO}", y=1.02)
        plt.tight_layout()
        plt.show()

if __name__ == "__main__":
    main()