from ImpararePackage import dataRequest

def main():
    dataRequest.execute("""
        DROP TABLE IF EXISTS imparare2_dataset_label;
        
        CREATE UNLOGGED TABLE imparare2_dataset_label AS
            SELECT 
                d.registro, 
                d.dia::Date,
                MAX(d.sexo) sexo,
                MAX(idade_anos)::SMALLINT as idade_anos,
                MAX(idade_dias)::INTEGER as idade_dias,
                MIN(unidade) unidade_internacao,
                MIN(tipo_intern) tipo_internacao,
                MIN(dthr_atendimento)::DATE as dthr_internacao,
                MAX(dthr_alta)::DATE as dthr_alta,
                COALESCE(d.dia::date - min(dthr_atendimento)::date, 0)::SMALLINT as los_dias,
                count(*)::SMALLINT as count,
                id_enterprise::SMALLINT as id_enterprise,
                MAX(los) los,
                MAX(los_on_previous_hospitalization) los_on_previous_hospitalization,
                MAX(days_since_previous_hospitalizations) days_since_previous_hospitalizations,
                max(los_on_next_hospitalization) los_on_next_hospitalization,
                max(days_to_next_hospitalizations) days_to_next_hospitalizations
            FROM imparare2_paciente_dia_internacao_with_label_nova as d
            GROUP BY d.registro, d.dia, id_enterprise;
    """)
    dataRequest.execute("""CREATE INDEX IF NOT EXISTS imparare2_dataset_label_idx_1 ON imparare2_dataset_label(id_enterprise, registro, dia);""")

if __name__ == "__main__":
    main()