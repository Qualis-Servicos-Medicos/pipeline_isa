from ImpararePackage import dataRequest

def main():
    dataRequest.execute("""
        SET synchronous_commit = off;

        DROP TABLE IF EXISTS imparare2_dataset_label_intermediario;

        CREATE UNLOGGED TABLE imparare2_dataset_label_intermediario AS
            SELECT DISTINCT ON(df_pct_dia.registro, df_pct_dia.dia)
                df_pct_dia.registro::INT4 AS prontuario,
                df_pct_dia.dia AS dia,
                df_pct_dia.id_enterprise::SMALLINT AS id_enterprise,
                df_pct_dia.idade_anos::SMALLINT AS idade_anos,
                df_pct_dia.idade_dias::INT4 AS idade_dias,
                df_pct_dia.los_dias::SMALLINT,
                df_pct_dia.los::SMALLINT,
                df_pct_dia.los_on_previous_hospitalization::SMALLINT,
                df_pct_dia.days_synce_previous_hospitalizations::SMALLINT,
                df_pct_dia.los_on_next_hospitalization::SMALLINT,
                df_pct_dia.days_to_next_hospitalizations::SMALLINT,
                -- ------------------------------------
                --          Cirurgias
                -- ------------------------------------
                df_cir.tempo_cirurgia_hoje::INT4 AS cirurgia_tempo_total,
                df_cir.count_laudos_cirurgias_hoje::SMALLINT AS cirurgia_procedimentos_total,
                df_cir.cirurgia_dentro_ultimos_30_dias AS cirurgia_em_30_dias,
                df_cir.cirurgia_dentro_ultimos_90_dias AS cirurgia_em_90_dias,
                -- ------------------------------------
                --          Sinais vitais
                -- ------------------------------------
                df_enf_svt."FC_min"::FLOAT4 AS "FC_min",
                df_enf_svt."FC_max"::FLOAT4 AS "FC_max",
                df_enf_svt."FC_ALTERADA"::BOOLEAN AS "FC_ALTERADA",
                df_enf_svt."FC_ALTA"::BOOLEAN AS "FC_ALTA",
                df_enf_svt."FC_BAIXA"::BOOLEAN AS "FC_BAIXA",
                df_enf_svt."FR_min"::FLOAT4 AS "FR_min",
                df_enf_svt."FR_max"::FLOAT4 AS "FR_max",
                df_enf_svt."FR_ALTERADO"::BOOLEAN AS "FR_ALTERADA",
                df_enf_svt."HGT_min"::FLOAT4 AS "HGT_min",
                df_enf_svt."HGT_max"::FLOAT4 AS "HGT_max",
                df_enf_svt."HGT_ALTERADO"::BOOLEAN AS "HGT_ALTERADO",
                df_enf_svt."OXIMETRIA_min"::FLOAT4 AS "OXIMETRIA_min",
                df_enf_svt."OXIMETRIA_max"::FLOAT4 AS "OXIMETRIA_max",
                df_enf_svt."PAD_min"::FLOAT4 AS "PAD_min",
                df_enf_svt."PAD_max"::FLOAT4 AS "PAD_max",
                df_enf_svt."PAS_min"::FLOAT4 AS "PAS_min",
                df_enf_svt."PAS_max"::FLOAT4 AS "PAS_max",
                df_enf_svt."PAS_ALTERADO"::BOOLEAN AS "PAS_ALTERADA",
                df_enf_svt."TEMP_min"::FLOAT4 AS "TEMP_min",
                df_enf_svt."TEMP_max"::FLOAT4 AS "TEMP_max",
                df_enf_svt."TEMP_ALTERADA"::BOOLEAN AS "TEMP_ALTERADA",
                df_enf_svt."O2_min"::FLOAT4 AS "O2_min",
                df_enf_svt."O2_max"::FLOAT4 AS "O2_max",
                df_enf_svt."FIO2_min"::FLOAT4 AS "FIO2_min",
                df_enf_svt."FIO2_max"::FLOAT4 AS "FIO2_max",
                df_enf_svt."PEEP_min"::FLOAT4 AS "PEEP_min",
                df_enf_svt."PEEP_max"::FLOAT4 AS "PEEP_max",
                df_enf_svt."SINAIS_VITAIS_count_total"::SMALLINT AS "SINAIS_VITAIS_registros_total",
                -- ------------------------------------
                --             Evolucoes
                -- ------------------------------------
                df_evo.evo_count_dia::SMALLINT,
                -- ------------------------------------
                --            Antibioticos
                -- ------------------------------------
                -- df_atb."ATB_COMUNITARIO_count"::SMALLINT,
                -- df_atb."ATB_TOPICO_count"::SMALLINT,
                -- df_atb."ATB_INTERMEDIARIO_count"::SMALLINT,
                -- df_atb."ATB_HOSPITALAR_count"::SMALLINT,
                -- df_atb."ATB_MMR_count"::SMALLINT,
                -- df_atb."ATB_ANTIFUNGICO_count"::SMALLINT,
                -- df_atb."ATB_OUTROS_count"::SMALLINT,
                -- df_atb."ATB_PROFILATICO_count"::SMALLINT,
                df_atb.atb_categ::SMALLINT,
                -- df_atb.via_categ::SMALLINT,
                -- df_atb."via_PARENTERAL_count"::SMALLINT,
                -- df_atb."via_ENTERAL_count"::SMALLINT,
                -- df_atb."via_TOPICO_count"::SMALLINT,
                -- df_atb."via_OUTRO_count"::SMALLINT,
                -- df_atb.atb_em_uso_passado::SMALLINT,
                -- df_atb.atb_em_uso_hoje::SMALLINT,
                -- df_atb.atb_em_uso_futuro::SMALLINT,
                -- df_atb.atb_em_uso::SMALLINT,
                -- df_atb.ACICLOVIR_count::SMALLINT, 
                -- df_atb.AMOXICILINA_SULBACTAM_count::SMALLINT, 
                -- df_atb.CEFADROXILA_count::SMALLINT, 
                -- df_atb.CEFALOTINA_count::SMALLINT,
                -- df_atb.CEFOTAXIMA_count::SMALLINT, 
                -- df_atb.CEFTAZIDIMA_count::SMALLINT, 
                -- df_atb.CEFTAZIDIMA_AVIBACTAM_count::SMALLINT,
                -- df_atb.CEFTALOZANA_TAZOBACTAM_count::SMALLINT, 
                -- df_atb.CETOCONAZOL_count::SMALLINT, 
                -- df_atb.CLARITROMICINA_count::SMALLINT,
                -- df_atb.CLORANFENICOL_count::SMALLINT, 
                -- df_atb.DOXICICLINA_count::SMALLINT, 
                -- df_atb.ERTAPENEM_count::SMALLINT, 
                -- df_atb.ERITROMICINA_count::SMALLINT,
                -- df_atb.GANCICLOVIR_count::SMALLINT, 
                -- df_atb.IVERMECTINA_count::SMALLINT,
                -- df_atb.MICAFUNGINA_count::SMALLINT, 
                -- df_atb.MICONAZOL_count::SMALLINT, 
                -- df_atb.MOXIFLOXACINO_count::SMALLINT, 
                -- df_atb.MUPIROCINA_count::SMALLINT, 
                -- df_atb.NEOMICINA_count::SMALLINT,
                -- df_atb.RIFAMPICINA_count::SMALLINT, 
                -- df_atb.SULFADIAZINA_count::SMALLINT,
                -- df_atb.TEICOPLANINA_count::SMALLINT, 
                -- df_atb.VORICONAZOL_count::SMALLINT,
                -- df_atb.CIPROFLOXACINO_count::SMALLINT, 
                -- df_atb.OUTRO_count::SMALLINT,
                -- df_atb.AMICACINA_count::SMALLINT,
                -- df_atb.AMOXICILINA_CLAVULANATO_count::SMALLINT,
                -- df_atb.AMOXICILINA_count::SMALLINT,
                -- df_atb.AMPICILINA_count::SMALLINT,
                -- df_atb.AZITROMICINA_count::SMALLINT,
                -- df_atb.PENICILINAGBENZATINA_count::SMALLINT,
                -- df_atb.PENICILINAGPOTASSICA_count::SMALLINT,
                -- df_atb.CEFALEXINA_count::SMALLINT,
                -- df_atb.CEFAZOLINA_count::SMALLINT,
                -- df_atb.CEFEPIMA_count::SMALLINT,
                -- df_atb.CEFTRIAXONA_count::SMALLINT,
                -- df_atb.CEFUROXIMA_count::SMALLINT,
                -- df_atb.CLINDAMICINA_count::SMALLINT,
                -- df_atb.FLUCONAZOL_count::SMALLINT,
                -- df_atb.GENTAMICINA_count::SMALLINT,
                -- df_atb.LEVOFLOXACINO_count::SMALLINT,
                -- df_atb.LINEZOLIDA_count::SMALLINT,
                -- df_atb.MEROPENEM_count::SMALLINT,
                -- df_atb.METRONIDAZOL_count::SMALLINT,
                -- df_atb.NISTATINA_count::SMALLINT,
                -- df_atb.OXACILINA_count::SMALLINT,
                -- df_atb.PIPERACILINA_TAZOBACTAM_count::SMALLINT,
                -- df_atb.AMPICILINA_SULBACTAM_count::SMALLINT,
                -- df_atb.SULFAMETOXAZOL_TRIMETOPRIM_count::SMALLINT,
                -- df_atb.POLIMIXINAB_count::SMALLINT,
                -- df_atb.TOBRAMICINA_count::SMALLINT,
                -- df_atb.VANCOMICINA_count::SMALLINT,
                -- df_atb.VIA_TOPICO_count::SMALLINT,
                -- df_atb.VIA_SNG_count::SMALLINT,
                -- df_atb.VIA_OUTRO_count::SMALLINT,
                -- df_atb.VIA_EV_count::SMALLINT,
                -- df_atb.VIA_IM_count::SMALLINT,
                -- df_atb.VIA_VO_count::SMALLINT,
                -- ------------------------------------
                --            CULTURAS
                -- ------------------------------------
                -- df_cult.qtd_hemocultura_positiva_futuro::SMALLINT,
                -- df_cult.qtd_hemocultura_positiva_hoje::SMALLINT,
                -- df_cult.qtd_hemocultura_positiva_passado::SMALLINT,
                -- df_cult.qtd_hemocultura_sem_crescimento_futuro::SMALLINT,
                -- df_cult.qtd_hemocultura_sem_crescimento_hoje::SMALLINT,
                -- df_cult.qtd_hemocultura_sem_crescimento_passado::SMALLINT,
                df_cult.qtd_cultura_positiva_futuro::SMALLINT,
                df_cult.qtd_cultura_positiva_hoje::SMALLINT,
                df_cult.qtd_cultura_positiva_passado::SMALLINT,
                df_cult.qtd_cultura_sem_crescimento_futuro::SMALLINT,
                df_cult.qtd_cultura_sem_crescimento_hoje::SMALLINT,
                df_cult.qtd_cultura_sem_crescimento_passado::SMALLINT,
                df_cult.cultura_pos_categ_passado::BOOLEAN,
                df_cult.cultura_pos_categ_hoje::BOOLEAN,
                df_cult.cultura_pos_categ_futuro::BOOLEAN,
                -- df_cult.qtd_urocultura_positiva_futuro::SMALLINT,
                -- df_cult.qtd_urocultura_positiva_hoje::SMALLINT,
                -- df_cult.qtd_urocultura_positiva_passado::SMALLINT,
                -- df_cult.qtd_urocultura_sem_crescimento_futuro::SMALLINT,
                -- df_cult.qtd_urocultura_sem_crescimento_hoje::SMALLINT,
                -- df_cult.qtd_urocultura_sem_crescimento_passado::SMALLINT,
                -- ------------------------------------
                --            HEMOGRAMA
                -- ------------------------------------
                df_sangue.leuco_min::FLOAT4,
                df_sangue.leuco_max::FLOAT4,
                df_sangue.leuco_avg::FLOAT4,
                df_sangue.rdw_min::FLOAT4,
                df_sangue.rdw_max::FLOAT4,
                df_sangue.rdw_avg::FLOAT4,
                df_sangue.neuto_min::FLOAT4,
                df_sangue.neuto_max::FLOAT4,
                df_sangue.neuto_avg::FLOAT4,
                df_sangue.pcr_min::FLOAT4,
                df_sangue.pcr_max::FLOAT4,
                df_sangue.pcr_avg::FLOAT4,
                -- df_sangue.clostridium_pos::INTEGER,
                df_sangue.leuco_alterado_futuro::INTEGER,
                df_sangue.leucocitose_futuro::INTEGER,
                df_sangue.leucopenia_futuro::INTEGER,
                df_sangue.rdw_alterado_futuro::INTEGER,
                df_sangue.neutro_alterado_futuro::INTEGER,
                df_sangue.pcr_alterada_futuro::INTEGER,
                df_sangue.clostridium_positivo_futuro::INTEGER,
                df_sangue.mrsa_positivo_futuro::INTEGER,
                df_sangue.virus_resp_positivo_futuro::INTEGER,
                df_sangue.glicose_liquor_alterada_futuro::INTEGER,
                df_sangue.proteina_liquor_alterada_futuro::INTEGER,
                df_sangue.leuco_alterado_passado::INTEGER,
                df_sangue.leucocitose_passado::INTEGER,
                df_sangue.leucopenia_passado::INTEGER,
                df_sangue.rdw_alterado_passado::INTEGER,
                df_sangue.neutro_alterado_passado::INTEGER,
                df_sangue.pcr_alterada_passado::INTEGER,
                df_sangue.clostridium_positivo_passado::INTEGER,
                df_sangue.mrsa_positivo_passado::INTEGER,
                df_sangue.virus_resp_positivo_passado::INTEGER,
                df_sangue.glicose_liquor_alterada_passado::INTEGER,
                df_sangue.proteina_liquor_alterada_passado::INTEGER,
                df_sangue."LEUCO_ALTERADA"::SMALLINT as "LEUCO_ALTERADO",
                df_sangue."LEUCOCITOSE"::SMALLINT as "LEUCO_ALTO",
                df_sangue."LEUCOPENIA"::SMALLINT as "LEUCO_BAIXO",
                df_sangue."RDW_ALTERADA"::SMALLINT as "RDW_ALTO",
                df_sangue."NEUTROF_ALTERADO"::SMALLINT as "NEUTROFILO_ALTO",
                df_sangue."PCR_ALTERADA"::SMALLINT as "PCR_ALTA",
                df_sangue."CLOSTRIDIUM_POSITIVO"::SMALLINT as "CLOSTRIDIUM_POSITIVO",
                df_sangue."MRSA_POSITIVO"::SMALLINT as "MRSA_POSITIVO",
                df_sangue."VIRUS_RESPIRATORIO_POSITIVO"::SMALLINT as "VIRUS_RESPIRATORIO_POSITIVO",
                df_sangue."LIQUOR_ALTERA_GLICOSE"::SMALLINT as "LIQUOR_ALTERA_GLICOSE",
                df_sangue."LIQUOR_ALTERA_PROTEINA"::SMALLINT as "LIQUOR_ALTERA_PROTEINA",
                -- ------------------------------------
                --          Exames de imagem
                -- ------------------------------------
                COALESCE(df_rx.laudo_exame_count, 0)::SMALLINT AS laudo_exame_count
            FROM imparare2_dataset_label df_pct_dia
            LEFT JOIN imparare2_dataset_sangue_categ_temporal df_sangue
                ON df_pct_dia.registro = df_sangue.registro
                    AND df_pct_dia.dia = df_sangue.data_requisicao_exame
                    AND df_pct_dia.id_enterprise = df_sangue.id_enterprise
            LEFT JOIN imparare2_dataset_cirurgias df_cir
                ON df_pct_dia.registro = df_cir.prontuario
                    AND df_pct_dia.dia = df_cir.dia
                    AND df_pct_dia.id_enterprise = df_cir.id_enterprise
            LEFT JOIN imparare2_dataset_enfermagem_categ df_enf_svt
                ON df_pct_dia.registro = df_enf_svt.registro
                    AND df_pct_dia.dia = df_enf_svt.dia::date
                    AND df_pct_dia.id_enterprise = df_enf_svt.id_enterprise
            LEFT JOIN imparare2_dataset_evolucao df_evo
                ON df_pct_dia.registro = df_evo.prontuario
                    AND df_pct_dia.dia = df_evo.dia
                    AND df_pct_dia.id_enterprise = df_evo.id_enterprise
            LEFT JOIN imparare2_dataset_prescricao_ab df_atb
                ON df_pct_dia.registro = df_atb.prontuario
                    AND df_pct_dia.dia = df_atb.dia
                    AND df_pct_dia.id_enterprise = df_atb.id_enterprise
            LEFT JOIN imparare2_dataset_hemograma df_cult
                ON df_pct_dia.registro = df_cult.prontuario
                    AND df_pct_dia.dia = df_cult.dia
                    AND df_pct_dia.id_enterprise = df_cult.id_enterprise
            LEFT JOIN imparare2_dataset_raiox df_rx
                ON df_pct_dia.registro = df_rx.prontuario
                    AND df_pct_dia.dia = df_rx.dia
                    AND df_pct_dia.id_enterprise = df_rx.id_enterprise;

        CREATE INDEX IF NOT EXISTS idx_dataset_label_intermediario ON imparare2_dataset_label_intermediario (id_enterprise, prontuario, dia);
    """)

if __name__ == "__main__":
    main()