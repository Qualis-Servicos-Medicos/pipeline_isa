from ImpararePackage import dataRequest
from ImpararePackage import maestro

def main():
    if maestro.get_must_update_all_patients() != "1":
        print("Atualização de todos os pacientes não está habilitada.")
        return
    
    query_formated = f"""
        SELECT 'mes_inicial' as key
            , date_trunc('month', current_date - interval '1' month)::text as um_mes
            , date_trunc('month', current_date - interval '3' month)::text as tres_meses
            , date_trunc('month', current_date - interval '6' month)::text as seis_meses
            , date_trunc('month', current_date - interval '12' month)::text as doze_meses
            , date_trunc('month', current_date - interval '120' month)::text as tudo
            , h.id_hospital 
            , h.id_enterprise 
        from hospitals h
        UNION
        SELECT 'mes_final'
            , date_trunc('month', current_date)::text
            , date_trunc('month', current_date)::text
            , date_trunc('month', current_date)::text
            , date_trunc('month', current_date)::text
            , date_trunc('month', current_date)::text
            , h.id_hospital 
            , h.id_enterprise 
        from hospitals h
        UNION
        SELECT 
            'medicamentos',
            COUNT(CASE WHEN dthr_prescricao BETWEEN date_trunc('month', current_date - INTERVAL '1 month') AND date_trunc('month', current_date) THEN 1 END)::text,
            COUNT(CASE WHEN dthr_prescricao BETWEEN date_trunc('month', current_date - INTERVAL '3 months') AND date_trunc('month', current_date) THEN 1 END)::text,
            COUNT(CASE WHEN dthr_prescricao BETWEEN date_trunc('month', current_date - INTERVAL '6 months') AND date_trunc('month', current_date) THEN 1 END)::text,
            COUNT(CASE WHEN dthr_prescricao BETWEEN date_trunc('month', current_date - INTERVAL '12 months') AND date_trunc('month', current_date) THEN 1 END)::text,
            COUNT(CASE WHEN dthr_prescricao BETWEEN date_trunc('month', current_date - INTERVAL '120 months') AND date_trunc('month', current_date) THEN 1 END)::text,
            id_hospital,
            id_enterprise
            FROM isa_medicamento
            group by id_enterprise, id_hospital
        UNION
        SELECT 
            'exames' AS label,
            COUNT(*) FILTER (WHERE dthr_entrega BETWEEN date_trunc('month', current_date - interval '1 month') AND date_trunc('month', current_date))::text,
            COUNT(*) FILTER (WHERE dthr_entrega BETWEEN date_trunc('month', current_date - interval '3 month') AND date_trunc('month', current_date))::text,
            COUNT(*) FILTER (WHERE dthr_entrega BETWEEN date_trunc('month', current_date - interval '6 month') AND date_trunc('month', current_date))::text,
            COUNT(*) FILTER (WHERE dthr_entrega BETWEEN date_trunc('month', current_date - interval '12 month') AND date_trunc('month', current_date))::text,
            COUNT(*) FILTER (WHERE dthr_entrega BETWEEN date_trunc('month', current_date - interval '120 month') AND date_trunc('month', current_date))::text,
            id_hospital,
            id_enterprise
        FROM (
            SELECT patient_id, exame, dthr_pedido, dthr_entrega, id_hospital, id_enterprise
            FROM isa_exame
            GROUP BY patient_id, exame, dthr_pedido, dthr_entrega, id_hospital, id_enterprise
        ) AS grouped_exames
        group by id_hospital, id_enterprise
        UNION
        SELECT 
            'evolucoes',
            COUNT(CASE WHEN "dt_encontro" BETWEEN date_trunc('month', current_date - interval '1 month') AND date_trunc('month', current_date) THEN 1 END)::text,
            COUNT(CASE WHEN "dt_encontro" BETWEEN date_trunc('month', current_date - interval '3 months') AND date_trunc('month', current_date) THEN 1 END)::text,
            COUNT(CASE WHEN "dt_encontro" BETWEEN date_trunc('month', current_date - interval '6 months') AND date_trunc('month', current_date) THEN 1 END)::text,
            COUNT(CASE WHEN "dt_encontro" BETWEEN date_trunc('month', current_date - interval '12 months') AND date_trunc('month', current_date) THEN 1 END)::text,
            COUNT(CASE WHEN "dt_encontro" BETWEEN date_trunc('month', current_date - interval '120 months') AND date_trunc('month', current_date) THEN 1 END)::text,
            id_hospital,
            id_enterprise
        FROM isa_encontro
        group by id_hospital, id_enterprise
        UNION
        SELECT 
            'procedimentos',
            COUNT(CASE WHEN "dthr_fim_procedimento" BETWEEN date_trunc('month', current_date - interval '1 month') AND date_trunc('month', current_date) THEN 1 END)::text,
            COUNT(CASE WHEN "dthr_fim_procedimento" BETWEEN date_trunc('month', current_date - interval '3 months') AND date_trunc('month', current_date) THEN 1 END)::text,
            COUNT(CASE WHEN "dthr_fim_procedimento" BETWEEN date_trunc('month', current_date - interval '6 months') AND date_trunc('month', current_date) THEN 1 END)::text,
            COUNT(CASE WHEN "dthr_fim_procedimento" BETWEEN date_trunc('month', current_date - interval '12 months') AND date_trunc('month', current_date) THEN 1 END)::text,
            COUNT(CASE WHEN "dthr_fim_procedimento" BETWEEN date_trunc('month', current_date - interval '120 months') AND date_trunc('month', current_date) THEN 1 END)::text,
            id_hospital,
            id_enterprise
        FROM "isa_procedimento" 
        group by id_hospital, id_enterprise
        UNION
        SELECT 
            'sinais vitais',
            COUNT(CASE WHEN "dthr_coleta" BETWEEN date_trunc('month', current_date - interval '1 month') AND date_trunc('month', current_date) THEN 1 END)::text,
            COUNT(CASE WHEN "dthr_coleta" BETWEEN date_trunc('month', current_date - interval '3 months') AND date_trunc('month', current_date) THEN 1 END)::text,
            COUNT(CASE WHEN "dthr_coleta" BETWEEN date_trunc('month', current_date - interval '6 months') AND date_trunc('month', current_date) THEN 1 END)::text,
            COUNT(CASE WHEN "dthr_coleta" BETWEEN date_trunc('month', current_date - interval '12 months') AND date_trunc('month', current_date) THEN 1 END)::text,
            COUNT(CASE WHEN "dthr_coleta" BETWEEN date_trunc('month', current_date - interval '120 months') AND date_trunc('month', current_date) THEN 1 END)::text,
            id_hospital,
            id_enterprise
        FROM isa_sinal_vital
        group by id_hospital, id_enterprise
        UNION
        SELECT 
            'suspeitas_total',
            COUNT(DISTINCT CASE WHEN dt_infeccao BETWEEN date_trunc('month', current_date - interval '1 month') AND date_trunc('month', current_date) THEN paciente_id END)::text,
            COUNT(DISTINCT CASE WHEN dt_infeccao BETWEEN date_trunc('month', current_date - interval '3 month') AND date_trunc('month', current_date) THEN paciente_id END)::text,
            COUNT(DISTINCT CASE WHEN dt_infeccao BETWEEN date_trunc('month', current_date - interval '6 month') AND date_trunc('month', current_date) THEN paciente_id END)::text,
            COUNT(DISTINCT CASE WHEN dt_infeccao BETWEEN date_trunc('month', current_date - interval '12 month') AND date_trunc('month', current_date) THEN paciente_id END)::text,
            COUNT(DISTINCT CASE WHEN dt_infeccao BETWEEN date_trunc('month', current_date - interval '120 month') AND date_trunc('month', current_date) THEN paciente_id END)::text,
            id_hospital,
            id_enterprise
        FROM "isa_suspeita"
        group by id_hospital, id_enterprise
        UNION
        SELECT 
            'suspeitas_baixa_prob',
            COUNT(DISTINCT CASE WHEN dt_infeccao BETWEEN date_trunc('month', current_date - interval '1 month') AND date_trunc('month', current_date) THEN paciente_id END)::text,
            COUNT(DISTINCT CASE WHEN dt_infeccao BETWEEN date_trunc('month', current_date - interval '3 month') AND date_trunc('month', current_date) THEN paciente_id END)::text,
            COUNT(DISTINCT CASE WHEN dt_infeccao BETWEEN date_trunc('month', current_date - interval '6 month') AND date_trunc('month', current_date) THEN paciente_id END)::text,
            COUNT(DISTINCT CASE WHEN dt_infeccao BETWEEN date_trunc('month', current_date - interval '12 month') AND date_trunc('month', current_date) THEN paciente_id END)::text,
            COUNT(DISTINCT CASE WHEN dt_infeccao BETWEEN date_trunc('month', current_date - interval '120 month') AND date_trunc('month', current_date) THEN paciente_id END)::text,
            id_hospital,
            id_enterprise
        FROM isa_suspeita
        where max_prob < 0.5
        group by id_hospital, id_enterprise
        UNION
        SELECT 
            'suspeitas_media_prob',
            COUNT(DISTINCT CASE WHEN dt_infeccao BETWEEN date_trunc('month', current_date - interval '1 month') AND date_trunc('month', current_date) THEN paciente_id END)::text,
            COUNT(DISTINCT CASE WHEN dt_infeccao BETWEEN date_trunc('month', current_date - interval '3 month') AND date_trunc('month', current_date) THEN paciente_id END)::text,
            COUNT(DISTINCT CASE WHEN dt_infeccao BETWEEN date_trunc('month', current_date - interval '6 month') AND date_trunc('month', current_date) THEN paciente_id END)::text,
            COUNT(DISTINCT CASE WHEN dt_infeccao BETWEEN date_trunc('month', current_date - interval '12 month') AND date_trunc('month', current_date) THEN paciente_id END)::text,
            COUNT(DISTINCT CASE WHEN dt_infeccao BETWEEN date_trunc('month', current_date - interval '120 month') AND date_trunc('month', current_date) THEN paciente_id END)::text,
            id_hospital,
            id_enterprise
        FROM isa_suspeita
        where max_prob >= 0.5 AND max_prob <= 0.75
        group by id_hospital, id_enterprise
        UNION
        SELECT 
            'suspeitas_alta_prob',
            COUNT(DISTINCT CASE WHEN dt_infeccao BETWEEN date_trunc('month', current_date - interval '1 month') AND date_trunc('month', current_date) THEN paciente_id END)::text,
            COUNT(DISTINCT CASE WHEN dt_infeccao BETWEEN date_trunc('month', current_date - interval '3 month') AND date_trunc('month', current_date) THEN paciente_id END)::text,
            COUNT(DISTINCT CASE WHEN dt_infeccao BETWEEN date_trunc('month', current_date - interval '6 month') AND date_trunc('month', current_date) THEN paciente_id END)::text,
            COUNT(DISTINCT CASE WHEN dt_infeccao BETWEEN date_trunc('month', current_date - interval '12 month') AND date_trunc('month', current_date) THEN paciente_id END)::text,
            COUNT(DISTINCT CASE WHEN dt_infeccao BETWEEN date_trunc('month', current_date - interval '120 month') AND date_trunc('month', current_date) THEN paciente_id END)::text,
            id_hospital,
            id_enterprise
        FROM isa_suspeita
        where max_prob > 0.75
        group by id_hospital, id_enterprise
        UNION
        SELECT 
            'taxa_infeccao_total_alta_media_baixa',
            COUNT(CASE WHEN dt_infeccao BETWEEN date_trunc('month', current_date - interval '1 month') AND date_trunc('month', current_date) THEN paciente_id END)::text,
            COUNT(CASE WHEN dt_infeccao BETWEEN date_trunc('month', current_date - interval '3 month') AND date_trunc('month', current_date) THEN paciente_id END)::text,
            COUNT(CASE WHEN dt_infeccao BETWEEN date_trunc('month', current_date - interval '6 month') AND date_trunc('month', current_date) THEN paciente_id END)::text,
            COUNT(CASE WHEN dt_infeccao BETWEEN date_trunc('month', current_date - interval '12 month') AND date_trunc('month', current_date) THEN paciente_id END)::text,
            COUNT(CASE WHEN dt_infeccao BETWEEN date_trunc('month', current_date - interval '120 month') AND date_trunc('month', current_date) THEN paciente_id END)::text,
            id_hospital,
            id_enterprise
        FROM isa_suspeita
        group by id_hospital, id_enterprise
        UNION
        SELECT 
            'infeccao_confirmada_alta_prob_total',
            COUNT(CASE WHEN dt_infeccao BETWEEN date_trunc('month', current_date - interval '1 month') AND date_trunc('month', current_date) THEN paciente_id END)::text,
            COUNT(CASE WHEN dt_infeccao BETWEEN date_trunc('month', current_date - interval '3 month') AND date_trunc('month', current_date) THEN paciente_id END)::text,
            COUNT(CASE WHEN dt_infeccao BETWEEN date_trunc('month', current_date - interval '6 month') AND date_trunc('month', current_date) THEN paciente_id END)::text,
            COUNT(CASE WHEN dt_infeccao BETWEEN date_trunc('month', current_date - interval '12 month') AND date_trunc('month', current_date) THEN paciente_id END)::text,
            COUNT(CASE WHEN dt_infeccao BETWEEN date_trunc('month', current_date - interval '120 month') AND date_trunc('month', current_date) THEN paciente_id END)::text,
            id_hospital,
            id_enterprise
        FROM isa_suspeita
        where max_prob > 0.75
        group by id_hospital, id_enterprise
        UNION 
        SELECT 
            'infeccao_confirmada_media_prob_total',
            COUNT(CASE WHEN dt_infeccao BETWEEN date_trunc('month', current_date - interval '1 month') AND date_trunc('month', current_date) THEN paciente_id END)::text,
            COUNT(CASE WHEN dt_infeccao BETWEEN date_trunc('month', current_date - interval '3 month') AND date_trunc('month', current_date) THEN paciente_id END)::text,
            COUNT(CASE WHEN dt_infeccao BETWEEN date_trunc('month', current_date - interval '6 month') AND date_trunc('month', current_date) THEN paciente_id END)::text,
            COUNT(CASE WHEN dt_infeccao BETWEEN date_trunc('month', current_date - interval '12 month') AND date_trunc('month', current_date) THEN paciente_id END)::text,
            COUNT(CASE WHEN dt_infeccao BETWEEN date_trunc('month', current_date - interval '120 month') AND date_trunc('month', current_date) THEN paciente_id END)::text,
            id_hospital,
            id_enterprise
        FROM isa_suspeita
        where max_prob >= 0.5 AND max_prob <= 0.75
        group by id_hospital, id_enterprise
        UNION
        SELECT 
            'infeccao_confirmada_baixa_prob_total',
            COUNT(CASE WHEN dt_infeccao BETWEEN date_trunc('month', current_date - interval '1 month') AND date_trunc('month', current_date) THEN paciente_id END)::text,
            COUNT(CASE WHEN dt_infeccao BETWEEN date_trunc('month', current_date - interval '3 month') AND date_trunc('month', current_date) THEN paciente_id END)::text,
            COUNT(CASE WHEN dt_infeccao BETWEEN date_trunc('month', current_date - interval '6 month') AND date_trunc('month', current_date) THEN paciente_id END)::text,
            COUNT(CASE WHEN dt_infeccao BETWEEN date_trunc('month', current_date - interval '12 month') AND date_trunc('month', current_date) THEN paciente_id END)::text,
            COUNT(CASE WHEN dt_infeccao BETWEEN date_trunc('month', current_date - interval '120 month') AND date_trunc('month', current_date) THEN paciente_id END)::text,
            id_hospital,
            id_enterprise
        FROM "isa_suspeita" 
        where max_prob < 0.5
        group by id_hospital, id_enterprise
        UNION
        SELECT
            'pacientes_masculino',
            COUNT(CASE WHEN (i.dthr_atendimento BETWEEN date_trunc('month', current_date - interval '1 month') AND date_trunc('month', current_date) OR i.dthr_alta BETWEEN date_trunc('month', current_date - interval '1 month') AND date_trunc('month', current_date) OR (i.dthr_atendimento <= date_trunc('month', current_date - interval '1 month') AND i.dthr_alta >= date_trunc('month', current_date))) THEN 1 END)::text,
            COUNT(CASE WHEN (i.dthr_atendimento BETWEEN date_trunc('month', current_date - interval '3 month') AND date_trunc('month', current_date) OR i.dthr_alta BETWEEN date_trunc('month', current_date - interval '3 month') AND date_trunc('month', current_date) OR (i.dthr_atendimento <= date_trunc('month', current_date - interval '3 month') AND i.dthr_alta >= date_trunc('month', current_date))) THEN 1 END)::text,
            COUNT(CASE WHEN (i.dthr_atendimento BETWEEN date_trunc('month', current_date - interval '6 month') AND date_trunc('month', current_date) OR i.dthr_alta BETWEEN date_trunc('month', current_date - interval '6 month') AND date_trunc('month', current_date) OR (i.dthr_atendimento <= date_trunc('month', current_date - interval '6 month') AND i.dthr_alta >= date_trunc('month', current_date))) THEN 1 END)::text,
            COUNT(CASE WHEN (i.dthr_atendimento BETWEEN date_trunc('month', current_date - interval '12 month') AND date_trunc('month', current_date) OR i.dthr_alta BETWEEN date_trunc('month', current_date - interval '12 month') AND date_trunc('month', current_date) OR (i.dthr_atendimento <= date_trunc('month', current_date - interval '12 month') AND i.dthr_alta >= date_trunc('month', current_date))) THEN 1 END)::text,
            COUNT(CASE WHEN (i.dthr_atendimento BETWEEN date_trunc('month', current_date - interval '120 month') AND date_trunc('month', current_date) OR i.dthr_alta BETWEEN date_trunc('month', current_date - interval '120 month') AND date_trunc('month', current_date) OR (i.dthr_atendimento <= date_trunc('month', current_date - interval '120 month') AND i.dthr_alta >= date_trunc('month', current_date))) THEN 1 END)::text,
            i.id_hospital,
            i.id_enterprise
        FROM isa_internacoes i
        JOIN isa_pacientes p 
            ON i.paciente_id = p.id
                and i.id_enterprise = p.id_enterprise
        where p.sexo = 'M'
        group by i.id_hospital, i.id_enterprise
        UNION
        SELECT
            'pacientes_feminino',
            COUNT(CASE WHEN (i.dthr_atendimento BETWEEN date_trunc('month', current_date - interval '1 month') AND date_trunc('month', current_date) OR i.dthr_alta BETWEEN date_trunc('month', current_date - interval '1 month') AND date_trunc('month', current_date) OR (i.dthr_atendimento <= date_trunc('month', current_date - interval '1 month') AND i.dthr_alta >= date_trunc('month', current_date))) THEN 1 END)::text,
            COUNT(CASE WHEN (i.dthr_atendimento BETWEEN date_trunc('month', current_date - interval '3 month') AND date_trunc('month', current_date) OR i.dthr_alta BETWEEN date_trunc('month', current_date - interval '3 month') AND date_trunc('month', current_date) OR (i.dthr_atendimento <= date_trunc('month', current_date - interval '3 month') AND i.dthr_alta >= date_trunc('month', current_date))) THEN 1 END)::text,
            COUNT(CASE WHEN (i.dthr_atendimento BETWEEN date_trunc('month', current_date - interval '6 month') AND date_trunc('month', current_date) OR i.dthr_alta BETWEEN date_trunc('month', current_date - interval '6 month') AND date_trunc('month', current_date) OR (i.dthr_atendimento <= date_trunc('month', current_date - interval '6 month') AND i.dthr_alta >= date_trunc('month', current_date))) THEN 1 END)::text,
            COUNT(CASE WHEN (i.dthr_atendimento BETWEEN date_trunc('month', current_date - interval '12 month') AND date_trunc('month', current_date) OR i.dthr_alta BETWEEN date_trunc('month', current_date - interval '12 month') AND date_trunc('month', current_date) OR (i.dthr_atendimento <= date_trunc('month', current_date - interval '12 month') AND i.dthr_alta >= date_trunc('month', current_date))) THEN 1 END)::text,
            COUNT(CASE WHEN (i.dthr_atendimento BETWEEN date_trunc('month', current_date - interval '120 month') AND date_trunc('month', current_date) OR i.dthr_alta BETWEEN date_trunc('month', current_date - interval '120 month') AND date_trunc('month', current_date) OR (i.dthr_atendimento <= date_trunc('month', current_date - interval '120 month') AND i.dthr_alta >= date_trunc('month', current_date))) THEN 1 END)::text,
            i.id_hospital,
            i.id_enterprise
        FROM isa_internacoes i
        JOIN isa_pacientes p 
            ON i.paciente_id = p.id
                and i.id_enterprise = p.id_enterprise
        where p.sexo = 'F'
        group by i.id_hospital, i.id_enterprise
        UNION
        SELECT
            'pacientes_masculino_faixa_etaria_ate_10',
            COUNT(CASE WHEN (i.dthr_atendimento BETWEEN date_trunc('month', current_date - interval '1 month') AND date_trunc('month', current_date) OR i.dthr_alta BETWEEN date_trunc('month', current_date - interval '1 month') AND date_trunc('month', current_date) OR (i.dthr_atendimento <= date_trunc('month', current_date - interval '1 month') AND i.dthr_alta >= date_trunc('month', current_date))) THEN 1 END)::text,
            COUNT(CASE WHEN (i.dthr_atendimento BETWEEN date_trunc('month', current_date - interval '3 month') AND date_trunc('month', current_date) OR i.dthr_alta BETWEEN date_trunc('month', current_date - interval '3 month') AND date_trunc('month', current_date) OR (i.dthr_atendimento <= date_trunc('month', current_date - interval '3 month') AND i.dthr_alta >= date_trunc('month', current_date))) THEN 1 END)::text,
            COUNT(CASE WHEN (i.dthr_atendimento BETWEEN date_trunc('month', current_date - interval '6 month') AND date_trunc('month', current_date) OR i.dthr_alta BETWEEN date_trunc('month', current_date - interval '6 month') AND date_trunc('month', current_date) OR (i.dthr_atendimento <= date_trunc('month', current_date - interval '6 month') AND i.dthr_alta >= date_trunc('month', current_date))) THEN 1 END)::text,
            COUNT(CASE WHEN (i.dthr_atendimento BETWEEN date_trunc('month', current_date - interval '12 month') AND date_trunc('month', current_date) OR i.dthr_alta BETWEEN date_trunc('month', current_date - interval '12 month') AND date_trunc('month', current_date) OR (i.dthr_atendimento <= date_trunc('month', current_date - interval '12 month') AND i.dthr_alta >= date_trunc('month', current_date))) THEN 1 END)::text,
            COUNT(CASE WHEN (i.dthr_atendimento BETWEEN date_trunc('month', current_date - interval '120 month') AND date_trunc('month', current_date) OR i.dthr_alta BETWEEN date_trunc('month', current_date - interval '120 month') AND date_trunc('month', current_date) OR (i.dthr_atendimento <= date_trunc('month', current_date - interval '120 month') AND i.dthr_alta >= date_trunc('month', current_date))) THEN 1 END)::text,
            i.id_hospital,
            i.id_enterprise
        FROM isa_internacoes i
        JOIN isa_pacientes p 
            ON i.paciente_id = p.id
                and i.id_enterprise = p.id_enterprise
        where p.sexo = 'M' AND p.idade_hoje <= 10
        group by i.id_hospital, i.id_enterprise
        UNION
        SELECT
            'pacientes_feminino_faixa_etaria_ate_10',
            COUNT(CASE WHEN (i.dthr_atendimento BETWEEN date_trunc('month', current_date - interval '1 month') AND date_trunc('month', current_date) OR i.dthr_alta BETWEEN date_trunc('month', current_date - interval '1 month') AND date_trunc('month', current_date) OR (i.dthr_atendimento <= date_trunc('month', current_date - interval '1 month') AND i.dthr_alta >= date_trunc('month', current_date))) THEN 1 END)::text,
            COUNT(CASE WHEN (i.dthr_atendimento BETWEEN date_trunc('month', current_date - interval '3 month') AND date_trunc('month', current_date) OR i.dthr_alta BETWEEN date_trunc('month', current_date - interval '3 month') AND date_trunc('month', current_date) OR (i.dthr_atendimento <= date_trunc('month', current_date - interval '3 month') AND i.dthr_alta >= date_trunc('month', current_date))) THEN 1 END)::text,
            COUNT(CASE WHEN (i.dthr_atendimento BETWEEN date_trunc('month', current_date - interval '6 month') AND date_trunc('month', current_date) OR i.dthr_alta BETWEEN date_trunc('month', current_date - interval '6 month') AND date_trunc('month', current_date) OR (i.dthr_atendimento <= date_trunc('month', current_date - interval '6 month') AND i.dthr_alta >= date_trunc('month', current_date))) THEN 1 END)::text,
            COUNT(CASE WHEN (i.dthr_atendimento BETWEEN date_trunc('month', current_date - interval '12 month') AND date_trunc('month', current_date) OR i.dthr_alta BETWEEN date_trunc('month', current_date - interval '12 month') AND date_trunc('month', current_date) OR (i.dthr_atendimento <= date_trunc('month', current_date - interval '12 month') AND i.dthr_alta >= date_trunc('month', current_date))) THEN 1 END)::text,
            COUNT(CASE WHEN (i.dthr_atendimento BETWEEN date_trunc('month', current_date - interval '120 month') AND date_trunc('month', current_date) OR i.dthr_alta BETWEEN date_trunc('month', current_date - interval '120 month') AND date_trunc('month', current_date) OR (i.dthr_atendimento <= date_trunc('month', current_date - interval '120 month') AND i.dthr_alta >= date_trunc('month', current_date))) THEN 1 END)::text,
            i.id_hospital,
            i.id_enterprise
        FROM isa_internacoes i
        JOIN isa_pacientes p 
            ON i.paciente_id = p.id
                and i.id_enterprise = p.id_enterprise
        where p.sexo = 'F' AND p.idade_hoje <= 10
        group by i.id_hospital, i.id_enterprise
        UNION
        SELECT
            'pacientes_masculino_faixa_etaria_ate_11_20',
            COUNT(CASE WHEN (i.dthr_atendimento BETWEEN date_trunc('month', current_date - interval '1 month') AND date_trunc('month', current_date) OR i.dthr_alta BETWEEN date_trunc('month', current_date - interval '1 month') AND date_trunc('month', current_date) OR (i.dthr_atendimento <= date_trunc('month', current_date - interval '1 month') AND i.dthr_alta >= date_trunc('month', current_date))) THEN 1 END)::text,
            COUNT(CASE WHEN (i.dthr_atendimento BETWEEN date_trunc('month', current_date - interval '3 month') AND date_trunc('month', current_date) OR i.dthr_alta BETWEEN date_trunc('month', current_date - interval '3 month') AND date_trunc('month', current_date) OR (i.dthr_atendimento <= date_trunc('month', current_date - interval '3 month') AND i.dthr_alta >= date_trunc('month', current_date))) THEN 1 END)::text,
            COUNT(CASE WHEN (i.dthr_atendimento BETWEEN date_trunc('month', current_date - interval '6 month') AND date_trunc('month', current_date) OR i.dthr_alta BETWEEN date_trunc('month', current_date - interval '6 month') AND date_trunc('month', current_date) OR (i.dthr_atendimento <= date_trunc('month', current_date - interval '6 month') AND i.dthr_alta >= date_trunc('month', current_date))) THEN 1 END)::text,
            COUNT(CASE WHEN (i.dthr_atendimento BETWEEN date_trunc('month', current_date - interval '12 month') AND date_trunc('month', current_date) OR i.dthr_alta BETWEEN date_trunc('month', current_date - interval '12 month') AND date_trunc('month', current_date) OR (i.dthr_atendimento <= date_trunc('month', current_date - interval '12 month') AND i.dthr_alta >= date_trunc('month', current_date))) THEN 1 END)::text,
            COUNT(CASE WHEN (i.dthr_atendimento BETWEEN date_trunc('month', current_date - interval '120 month') AND date_trunc('month', current_date) OR i.dthr_alta BETWEEN date_trunc('month', current_date - interval '120 month') AND date_trunc('month', current_date) OR (i.dthr_atendimento <= date_trunc('month', current_date - interval '120 month') AND i.dthr_alta >= date_trunc('month', current_date))) THEN 1 END)::text,
            i.id_hospital,
            i.id_enterprise
        FROM isa_internacoes i
        JOIN isa_pacientes p 
            ON i.paciente_id = p.id
                and i.id_enterprise = p.id_enterprise
        where p.sexo = 'M' and p.idade_hoje <= 20 and p.idade_hoje >= 11
        group by i.id_hospital, i.id_enterprise
        UNION
        SELECT
            'pacientes_feminino_faixa_etaria_ate_11_20',
            COUNT(CASE WHEN (i.dthr_atendimento BETWEEN date_trunc('month', current_date - interval '1 month') AND date_trunc('month', current_date) OR i.dthr_alta BETWEEN date_trunc('month', current_date - interval '1 month') AND date_trunc('month', current_date) OR (i.dthr_atendimento <= date_trunc('month', current_date - interval '1 month') AND i.dthr_alta >= date_trunc('month', current_date))) THEN 1 END)::text,
            COUNT(CASE WHEN (i.dthr_atendimento BETWEEN date_trunc('month', current_date - interval '3 month') AND date_trunc('month', current_date) OR i.dthr_alta BETWEEN date_trunc('month', current_date - interval '3 month') AND date_trunc('month', current_date) OR (i.dthr_atendimento <= date_trunc('month', current_date - interval '3 month') AND i.dthr_alta >= date_trunc('month', current_date))) THEN 1 END)::text,
            COUNT(CASE WHEN (i.dthr_atendimento BETWEEN date_trunc('month', current_date - interval '6 month') AND date_trunc('month', current_date) OR i.dthr_alta BETWEEN date_trunc('month', current_date - interval '6 month') AND date_trunc('month', current_date) OR (i.dthr_atendimento <= date_trunc('month', current_date - interval '6 month') AND i.dthr_alta >= date_trunc('month', current_date))) THEN 1 END)::text,
            COUNT(CASE WHEN (i.dthr_atendimento BETWEEN date_trunc('month', current_date - interval '12 month') AND date_trunc('month', current_date) OR i.dthr_alta BETWEEN date_trunc('month', current_date - interval '12 month') AND date_trunc('month', current_date) OR (i.dthr_atendimento <= date_trunc('month', current_date - interval '12 month') AND i.dthr_alta >= date_trunc('month', current_date))) THEN 1 END)::text,
            COUNT(CASE WHEN (i.dthr_atendimento BETWEEN date_trunc('month', current_date - interval '120 month') AND date_trunc('month', current_date) OR i.dthr_alta BETWEEN date_trunc('month', current_date - interval '120 month') AND date_trunc('month', current_date) OR (i.dthr_atendimento <= date_trunc('month', current_date - interval '120 month') AND i.dthr_alta >= date_trunc('month', current_date))) THEN 1 END)::text,
            i.id_hospital,
            i.id_enterprise
        FROM isa_internacoes i
        JOIN isa_pacientes p 
            ON i.paciente_id = p.id
                and i.id_enterprise = p.id_enterprise
        where p.sexo = 'F' and p.idade_hoje <= 20 and p.idade_hoje >= 11
        group by i.id_hospital, i.id_enterprise
        UNION
        SELECT
            'pacientes_masculino_faixa_etaria_ate_21_30',
            COUNT(CASE WHEN (i.dthr_atendimento BETWEEN date_trunc('month', current_date - interval '1 month') AND date_trunc('month', current_date) OR i.dthr_alta BETWEEN date_trunc('month', current_date - interval '1 month') AND date_trunc('month', current_date) OR (i.dthr_atendimento <= date_trunc('month', current_date - interval '1 month') AND i.dthr_alta >= date_trunc('month', current_date))) THEN 1 END)::text,
            COUNT(CASE WHEN (i.dthr_atendimento BETWEEN date_trunc('month', current_date - interval '3 month') AND date_trunc('month', current_date) OR i.dthr_alta BETWEEN date_trunc('month', current_date - interval '3 month') AND date_trunc('month', current_date) OR (i.dthr_atendimento <= date_trunc('month', current_date - interval '3 month') AND i.dthr_alta >= date_trunc('month', current_date))) THEN 1 END)::text,
            COUNT(CASE WHEN (i.dthr_atendimento BETWEEN date_trunc('month', current_date - interval '6 month') AND date_trunc('month', current_date) OR i.dthr_alta BETWEEN date_trunc('month', current_date - interval '6 month') AND date_trunc('month', current_date) OR (i.dthr_atendimento <= date_trunc('month', current_date - interval '6 month') AND i.dthr_alta >= date_trunc('month', current_date))) THEN 1 END)::text,
            COUNT(CASE WHEN (i.dthr_atendimento BETWEEN date_trunc('month', current_date - interval '12 month') AND date_trunc('month', current_date) OR i.dthr_alta BETWEEN date_trunc('month', current_date - interval '12 month') AND date_trunc('month', current_date) OR (i.dthr_atendimento <= date_trunc('month', current_date - interval '12 month') AND i.dthr_alta >= date_trunc('month', current_date))) THEN 1 END)::text,
            COUNT(CASE WHEN (i.dthr_atendimento BETWEEN date_trunc('month', current_date - interval '120 month') AND date_trunc('month', current_date) OR i.dthr_alta BETWEEN date_trunc('month', current_date - interval '120 month') AND date_trunc('month', current_date) OR (i.dthr_atendimento <= date_trunc('month', current_date - interval '120 month') AND i.dthr_alta >= date_trunc('month', current_date))) THEN 1 END)::text,
            i.id_hospital,
            i.id_enterprise
        FROM isa_internacoes i
        JOIN isa_pacientes p 
            ON i.paciente_id = p.id
                and i.id_enterprise = p.id_enterprise
        where p.sexo = 'M' and p.idade_hoje <= 30 and p.idade_hoje >= 21
        group by i.id_hospital, i.id_enterprise
        UNION
        SELECT
            'pacientes_feminino_faixa_etaria_ate_21_30',
            COUNT(CASE WHEN (i.dthr_atendimento BETWEEN date_trunc('month', current_date - interval '1 month') AND date_trunc('month', current_date) OR i.dthr_alta BETWEEN date_trunc('month', current_date - interval '1 month') AND date_trunc('month', current_date) OR (i.dthr_atendimento <= date_trunc('month', current_date - interval '1 month') AND i.dthr_alta >= date_trunc('month', current_date))) THEN 1 END)::text,
            COUNT(CASE WHEN (i.dthr_atendimento BETWEEN date_trunc('month', current_date - interval '3 month') AND date_trunc('month', current_date) OR i.dthr_alta BETWEEN date_trunc('month', current_date - interval '3 month') AND date_trunc('month', current_date) OR (i.dthr_atendimento <= date_trunc('month', current_date - interval '3 month') AND i.dthr_alta >= date_trunc('month', current_date))) THEN 1 END)::text,
            COUNT(CASE WHEN (i.dthr_atendimento BETWEEN date_trunc('month', current_date - interval '6 month') AND date_trunc('month', current_date) OR i.dthr_alta BETWEEN date_trunc('month', current_date - interval '6 month') AND date_trunc('month', current_date) OR (i.dthr_atendimento <= date_trunc('month', current_date - interval '6 month') AND i.dthr_alta >= date_trunc('month', current_date))) THEN 1 END)::text,
            COUNT(CASE WHEN (i.dthr_atendimento BETWEEN date_trunc('month', current_date - interval '12 month') AND date_trunc('month', current_date) OR i.dthr_alta BETWEEN date_trunc('month', current_date - interval '12 month') AND date_trunc('month', current_date) OR (i.dthr_atendimento <= date_trunc('month', current_date - interval '12 month') AND i.dthr_alta >= date_trunc('month', current_date))) THEN 1 END)::text,
            COUNT(CASE WHEN (i.dthr_atendimento BETWEEN date_trunc('month', current_date - interval '120 month') AND date_trunc('month', current_date) OR i.dthr_alta BETWEEN date_trunc('month', current_date - interval '120 month') AND date_trunc('month', current_date) OR (i.dthr_atendimento <= date_trunc('month', current_date - interval '120 month') AND i.dthr_alta >= date_trunc('month', current_date))) THEN 1 END)::text,
            i.id_hospital,
            i.id_enterprise
        FROM isa_internacoes i
        JOIN isa_pacientes p 
            ON i.paciente_id = p.id
                and i.id_enterprise = p.id_enterprise
        where p.sexo = 'F' and p.idade_hoje <= 30 and p.idade_hoje >= 21
        group by i.id_hospital, i.id_enterprise
        UNION
        SELECT
            'pacientes_masculino_faixa_etaria_ate_31_40',
            COUNT(CASE WHEN (i.dthr_atendimento BETWEEN date_trunc('month', current_date - interval '1 month') AND date_trunc('month', current_date) OR i.dthr_alta BETWEEN date_trunc('month', current_date - interval '1 month') AND date_trunc('month', current_date) OR (i.dthr_atendimento <= date_trunc('month', current_date - interval '1 month') AND i.dthr_alta >= date_trunc('month', current_date))) THEN 1 END)::text,
            COUNT(CASE WHEN (i.dthr_atendimento BETWEEN date_trunc('month', current_date - interval '3 month') AND date_trunc('month', current_date) OR i.dthr_alta BETWEEN date_trunc('month', current_date - interval '3 month') AND date_trunc('month', current_date) OR (i.dthr_atendimento <= date_trunc('month', current_date - interval '3 month') AND i.dthr_alta >= date_trunc('month', current_date))) THEN 1 END)::text,
            COUNT(CASE WHEN (i.dthr_atendimento BETWEEN date_trunc('month', current_date - interval '6 month') AND date_trunc('month', current_date) OR i.dthr_alta BETWEEN date_trunc('month', current_date - interval '6 month') AND date_trunc('month', current_date) OR (i.dthr_atendimento <= date_trunc('month', current_date - interval '6 month') AND i.dthr_alta >= date_trunc('month', current_date))) THEN 1 END)::text,
            COUNT(CASE WHEN (i.dthr_atendimento BETWEEN date_trunc('month', current_date - interval '12 month') AND date_trunc('month', current_date) OR i.dthr_alta BETWEEN date_trunc('month', current_date - interval '12 month') AND date_trunc('month', current_date) OR (i.dthr_atendimento <= date_trunc('month', current_date - interval '12 month') AND i.dthr_alta >= date_trunc('month', current_date))) THEN 1 END)::text,
            COUNT(CASE WHEN (i.dthr_atendimento BETWEEN date_trunc('month', current_date - interval '120 month') AND date_trunc('month', current_date) OR i.dthr_alta BETWEEN date_trunc('month', current_date - interval '120 month') AND date_trunc('month', current_date) OR (i.dthr_atendimento <= date_trunc('month', current_date - interval '120 month') AND i.dthr_alta >= date_trunc('month', current_date))) THEN 1 END)::text,
            i.id_hospital,
            i.id_enterprise
        FROM isa_internacoes i
        JOIN isa_pacientes p 
            ON i.paciente_id = p.id
                and i.id_enterprise = p.id_enterprise
        where p.sexo = 'M' and p.idade_hoje <= 40 and p.idade_hoje >= 31
        group by i.id_hospital, i.id_enterprise
        UNION
        SELECT
            'pacientes_feminino_faixa_etaria_ate_31_40',
            COUNT(CASE WHEN (i.dthr_atendimento BETWEEN date_trunc('month', current_date - interval '1 month') AND date_trunc('month', current_date) OR i.dthr_alta BETWEEN date_trunc('month', current_date - interval '1 month') AND date_trunc('month', current_date) OR (i.dthr_atendimento <= date_trunc('month', current_date - interval '1 month') AND i.dthr_alta >= date_trunc('month', current_date))) THEN 1 END)::text,
            COUNT(CASE WHEN (i.dthr_atendimento BETWEEN date_trunc('month', current_date - interval '3 month') AND date_trunc('month', current_date) OR i.dthr_alta BETWEEN date_trunc('month', current_date - interval '3 month') AND date_trunc('month', current_date) OR (i.dthr_atendimento <= date_trunc('month', current_date - interval '3 month') AND i.dthr_alta >= date_trunc('month', current_date))) THEN 1 END)::text,
            COUNT(CASE WHEN (i.dthr_atendimento BETWEEN date_trunc('month', current_date - interval '6 month') AND date_trunc('month', current_date) OR i.dthr_alta BETWEEN date_trunc('month', current_date - interval '6 month') AND date_trunc('month', current_date) OR (i.dthr_atendimento <= date_trunc('month', current_date - interval '6 month') AND i.dthr_alta >= date_trunc('month', current_date))) THEN 1 END)::text,
            COUNT(CASE WHEN (i.dthr_atendimento BETWEEN date_trunc('month', current_date - interval '12 month') AND date_trunc('month', current_date) OR i.dthr_alta BETWEEN date_trunc('month', current_date - interval '12 month') AND date_trunc('month', current_date) OR (i.dthr_atendimento <= date_trunc('month', current_date - interval '12 month') AND i.dthr_alta >= date_trunc('month', current_date))) THEN 1 END)::text,
            COUNT(CASE WHEN (i.dthr_atendimento BETWEEN date_trunc('month', current_date - interval '120 month') AND date_trunc('month', current_date) OR i.dthr_alta BETWEEN date_trunc('month', current_date - interval '120 month') AND date_trunc('month', current_date) OR (i.dthr_atendimento <= date_trunc('month', current_date - interval '120 month') AND i.dthr_alta >= date_trunc('month', current_date))) THEN 1 END)::text,
            i.id_hospital,
            i.id_enterprise
        FROM isa_internacoes i
        JOIN isa_pacientes p 
            ON i.paciente_id = p.id
                and i.id_enterprise = p.id_enterprise
        where p.sexo = 'F' and p.idade_hoje <= 40 and p.idade_hoje >= 31
        group by i.id_hospital, i.id_enterprise
        UNION
        SELECT
            'pacientes_masculino_faixa_etaria_ate_41_50',
            COUNT(CASE WHEN (i.dthr_atendimento BETWEEN date_trunc('month', current_date - interval '1 month') AND date_trunc('month', current_date) OR i.dthr_alta BETWEEN date_trunc('month', current_date - interval '1 month') AND date_trunc('month', current_date) OR (i.dthr_atendimento <= date_trunc('month', current_date - interval '1 month') AND i.dthr_alta >= date_trunc('month', current_date))) THEN 1 END)::text,
            COUNT(CASE WHEN (i.dthr_atendimento BETWEEN date_trunc('month', current_date - interval '3 month') AND date_trunc('month', current_date) OR i.dthr_alta BETWEEN date_trunc('month', current_date - interval '3 month') AND date_trunc('month', current_date) OR (i.dthr_atendimento <= date_trunc('month', current_date - interval '3 month') AND i.dthr_alta >= date_trunc('month', current_date))) THEN 1 END)::text,
            COUNT(CASE WHEN (i.dthr_atendimento BETWEEN date_trunc('month', current_date - interval '6 month') AND date_trunc('month', current_date) OR i.dthr_alta BETWEEN date_trunc('month', current_date - interval '6 month') AND date_trunc('month', current_date) OR (i.dthr_atendimento <= date_trunc('month', current_date - interval '6 month') AND i.dthr_alta >= date_trunc('month', current_date))) THEN 1 END)::text,
            COUNT(CASE WHEN (i.dthr_atendimento BETWEEN date_trunc('month', current_date - interval '12 month') AND date_trunc('month', current_date) OR i.dthr_alta BETWEEN date_trunc('month', current_date - interval '12 month') AND date_trunc('month', current_date) OR (i.dthr_atendimento <= date_trunc('month', current_date - interval '12 month') AND i.dthr_alta >= date_trunc('month', current_date))) THEN 1 END)::text,
            COUNT(CASE WHEN (i.dthr_atendimento BETWEEN date_trunc('month', current_date - interval '120 month') AND date_trunc('month', current_date) OR i.dthr_alta BETWEEN date_trunc('month', current_date - interval '120 month') AND date_trunc('month', current_date) OR (i.dthr_atendimento <= date_trunc('month', current_date - interval '120 month') AND i.dthr_alta >= date_trunc('month', current_date))) THEN 1 END)::text,
            i.id_hospital,
            i.id_enterprise
        FROM isa_internacoes i
        JOIN isa_pacientes p 
            ON i.paciente_id = p.id
                and i.id_enterprise = p.id_enterprise
        where p.sexo = 'M' and p.idade_hoje <= 50 and p.idade_hoje >= 41
        group by i.id_hospital, i.id_enterprise
        UNION
        SELECT
            'pacientes_feminino_faixa_etaria_ate_41_50',
            COUNT(CASE WHEN (i.dthr_atendimento BETWEEN date_trunc('month', current_date - interval '1 month') AND date_trunc('month', current_date) OR i.dthr_alta BETWEEN date_trunc('month', current_date - interval '1 month') AND date_trunc('month', current_date) OR (i.dthr_atendimento <= date_trunc('month', current_date - interval '1 month') AND i.dthr_alta >= date_trunc('month', current_date))) THEN 1 END)::text,
            COUNT(CASE WHEN (i.dthr_atendimento BETWEEN date_trunc('month', current_date - interval '3 month') AND date_trunc('month', current_date) OR i.dthr_alta BETWEEN date_trunc('month', current_date - interval '3 month') AND date_trunc('month', current_date) OR (i.dthr_atendimento <= date_trunc('month', current_date - interval '3 month') AND i.dthr_alta >= date_trunc('month', current_date))) THEN 1 END)::text,
            COUNT(CASE WHEN (i.dthr_atendimento BETWEEN date_trunc('month', current_date - interval '6 month') AND date_trunc('month', current_date) OR i.dthr_alta BETWEEN date_trunc('month', current_date - interval '6 month') AND date_trunc('month', current_date) OR (i.dthr_atendimento <= date_trunc('month', current_date - interval '6 month') AND i.dthr_alta >= date_trunc('month', current_date))) THEN 1 END)::text,
            COUNT(CASE WHEN (i.dthr_atendimento BETWEEN date_trunc('month', current_date - interval '12 month') AND date_trunc('month', current_date) OR i.dthr_alta BETWEEN date_trunc('month', current_date - interval '12 month') AND date_trunc('month', current_date) OR (i.dthr_atendimento <= date_trunc('month', current_date - interval '12 month') AND i.dthr_alta >= date_trunc('month', current_date))) THEN 1 END)::text,
            COUNT(CASE WHEN (i.dthr_atendimento BETWEEN date_trunc('month', current_date - interval '120 month') AND date_trunc('month', current_date) OR i.dthr_alta BETWEEN date_trunc('month', current_date - interval '120 month') AND date_trunc('month', current_date) OR (i.dthr_atendimento <= date_trunc('month', current_date - interval '120 month') AND i.dthr_alta >= date_trunc('month', current_date))) THEN 1 END)::text,
            i.id_hospital,
            i.id_enterprise
        FROM isa_internacoes i
        JOIN isa_pacientes p 
            ON i.paciente_id = p.id
                and i.id_enterprise = p.id_enterprise
        where p.sexo = 'F' and p.idade_hoje <= 50 and p.idade_hoje >= 41
        group by i.id_hospital, i.id_enterprise
        UNION
        SELECT
            'pacientes_masculino_faixa_etaria_ate_51_60',
            COUNT(CASE WHEN (i.dthr_atendimento BETWEEN date_trunc('month', current_date - interval '1 month') AND date_trunc('month', current_date) OR i.dthr_alta BETWEEN date_trunc('month', current_date - interval '1 month') AND date_trunc('month', current_date) OR (i.dthr_atendimento <= date_trunc('month', current_date - interval '1 month') AND i.dthr_alta >= date_trunc('month', current_date))) THEN 1 END)::text,
            COUNT(CASE WHEN (i.dthr_atendimento BETWEEN date_trunc('month', current_date - interval '3 month') AND date_trunc('month', current_date) OR i.dthr_alta BETWEEN date_trunc('month', current_date - interval '3 month') AND date_trunc('month', current_date) OR (i.dthr_atendimento <= date_trunc('month', current_date - interval '3 month') AND i.dthr_alta >= date_trunc('month', current_date))) THEN 1 END)::text,
            COUNT(CASE WHEN (i.dthr_atendimento BETWEEN date_trunc('month', current_date - interval '6 month') AND date_trunc('month', current_date) OR i.dthr_alta BETWEEN date_trunc('month', current_date - interval '6 month') AND date_trunc('month', current_date) OR (i.dthr_atendimento <= date_trunc('month', current_date - interval '6 month') AND i.dthr_alta >= date_trunc('month', current_date))) THEN 1 END)::text,
            COUNT(CASE WHEN (i.dthr_atendimento BETWEEN date_trunc('month', current_date - interval '12 month') AND date_trunc('month', current_date) OR i.dthr_alta BETWEEN date_trunc('month', current_date - interval '12 month') AND date_trunc('month', current_date) OR (i.dthr_atendimento <= date_trunc('month', current_date - interval '12 month') AND i.dthr_alta >= date_trunc('month', current_date))) THEN 1 END)::text,
            COUNT(CASE WHEN (i.dthr_atendimento BETWEEN date_trunc('month', current_date - interval '120 month') AND date_trunc('month', current_date) OR i.dthr_alta BETWEEN date_trunc('month', current_date - interval '120 month') AND date_trunc('month', current_date) OR (i.dthr_atendimento <= date_trunc('month', current_date - interval '120 month') AND i.dthr_alta >= date_trunc('month', current_date))) THEN 1 END)::text,
            i.id_hospital,
            i.id_enterprise
        FROM isa_internacoes i
        JOIN isa_pacientes p 
            ON i.paciente_id = p.id
                and i.id_enterprise = p.id_enterprise
        where p.sexo = 'M' and p.idade_hoje <= 60 and p.idade_hoje >= 51
        group by i.id_hospital, i.id_enterprise
        UNION
        SELECT
            'pacientes_feminino_faixa_etaria_ate_51_60',
            COUNT(CASE WHEN (i.dthr_atendimento BETWEEN date_trunc('month', current_date - interval '1 month') AND date_trunc('month', current_date) OR i.dthr_alta BETWEEN date_trunc('month', current_date - interval '1 month') AND date_trunc('month', current_date) OR (i.dthr_atendimento <= date_trunc('month', current_date - interval '1 month') AND i.dthr_alta >= date_trunc('month', current_date))) THEN 1 END)::text,
            COUNT(CASE WHEN (i.dthr_atendimento BETWEEN date_trunc('month', current_date - interval '3 month') AND date_trunc('month', current_date) OR i.dthr_alta BETWEEN date_trunc('month', current_date - interval '3 month') AND date_trunc('month', current_date) OR (i.dthr_atendimento <= date_trunc('month', current_date - interval '3 month') AND i.dthr_alta >= date_trunc('month', current_date))) THEN 1 END)::text,
            COUNT(CASE WHEN (i.dthr_atendimento BETWEEN date_trunc('month', current_date - interval '6 month') AND date_trunc('month', current_date) OR i.dthr_alta BETWEEN date_trunc('month', current_date - interval '6 month') AND date_trunc('month', current_date) OR (i.dthr_atendimento <= date_trunc('month', current_date - interval '6 month') AND i.dthr_alta >= date_trunc('month', current_date))) THEN 1 END)::text,
            COUNT(CASE WHEN (i.dthr_atendimento BETWEEN date_trunc('month', current_date - interval '12 month') AND date_trunc('month', current_date) OR i.dthr_alta BETWEEN date_trunc('month', current_date - interval '12 month') AND date_trunc('month', current_date) OR (i.dthr_atendimento <= date_trunc('month', current_date - interval '12 month') AND i.dthr_alta >= date_trunc('month', current_date))) THEN 1 END)::text,
            COUNT(CASE WHEN (i.dthr_atendimento BETWEEN date_trunc('month', current_date - interval '120 month') AND date_trunc('month', current_date) OR i.dthr_alta BETWEEN date_trunc('month', current_date - interval '120 month') AND date_trunc('month', current_date) OR (i.dthr_atendimento <= date_trunc('month', current_date - interval '120 month') AND i.dthr_alta >= date_trunc('month', current_date))) THEN 1 END)::text,
            i.id_hospital,
            i.id_enterprise
        FROM isa_internacoes i
        JOIN isa_pacientes p 
            ON i.paciente_id = p.id
                and i.id_enterprise = p.id_enterprise
        where p.sexo = 'F' and p.idade_hoje <= 60 and p.idade_hoje >= 51
        group by i.id_hospital, i.id_enterprise
        UNION
        SELECT
            'pacientes_masculino_faixa_etaria_ate_61_70',
            COUNT(CASE WHEN (i.dthr_atendimento BETWEEN date_trunc('month', current_date - interval '1 month') AND date_trunc('month', current_date) OR i.dthr_alta BETWEEN date_trunc('month', current_date - interval '1 month') AND date_trunc('month', current_date) OR (i.dthr_atendimento <= date_trunc('month', current_date - interval '1 month') AND i.dthr_alta >= date_trunc('month', current_date))) THEN 1 END)::text,
            COUNT(CASE WHEN (i.dthr_atendimento BETWEEN date_trunc('month', current_date - interval '3 month') AND date_trunc('month', current_date) OR i.dthr_alta BETWEEN date_trunc('month', current_date - interval '3 month') AND date_trunc('month', current_date) OR (i.dthr_atendimento <= date_trunc('month', current_date - interval '3 month') AND i.dthr_alta >= date_trunc('month', current_date))) THEN 1 END)::text,
            COUNT(CASE WHEN (i.dthr_atendimento BETWEEN date_trunc('month', current_date - interval '6 month') AND date_trunc('month', current_date) OR i.dthr_alta BETWEEN date_trunc('month', current_date - interval '6 month') AND date_trunc('month', current_date) OR (i.dthr_atendimento <= date_trunc('month', current_date - interval '6 month') AND i.dthr_alta >= date_trunc('month', current_date))) THEN 1 END)::text,
            COUNT(CASE WHEN (i.dthr_atendimento BETWEEN date_trunc('month', current_date - interval '12 month') AND date_trunc('month', current_date) OR i.dthr_alta BETWEEN date_trunc('month', current_date - interval '12 month') AND date_trunc('month', current_date) OR (i.dthr_atendimento <= date_trunc('month', current_date - interval '12 month') AND i.dthr_alta >= date_trunc('month', current_date))) THEN 1 END)::text,
            COUNT(CASE WHEN (i.dthr_atendimento BETWEEN date_trunc('month', current_date - interval '120 month') AND date_trunc('month', current_date) OR i.dthr_alta BETWEEN date_trunc('month', current_date - interval '120 month') AND date_trunc('month', current_date) OR (i.dthr_atendimento <= date_trunc('month', current_date - interval '120 month') AND i.dthr_alta >= date_trunc('month', current_date))) THEN 1 END)::text,
            i.id_hospital,
            i.id_enterprise
        FROM isa_internacoes i
        JOIN isa_pacientes p 
            ON i.paciente_id = p.id
                and i.id_enterprise = p.id_enterprise
        where p.sexo = 'M' and p.idade_hoje <= 70 and p.idade_hoje >= 61
        group by i.id_hospital, i.id_enterprise
        UNION
        SELECT
            'pacientes_feminino_faixa_etaria_ate_61_70',
            COUNT(CASE WHEN (i.dthr_atendimento BETWEEN date_trunc('month', current_date - interval '1 month') AND date_trunc('month', current_date) OR i.dthr_alta BETWEEN date_trunc('month', current_date - interval '1 month') AND date_trunc('month', current_date) OR (i.dthr_atendimento <= date_trunc('month', current_date - interval '1 month') AND i.dthr_alta >= date_trunc('month', current_date))) THEN 1 END)::text,
            COUNT(CASE WHEN (i.dthr_atendimento BETWEEN date_trunc('month', current_date - interval '3 month') AND date_trunc('month', current_date) OR i.dthr_alta BETWEEN date_trunc('month', current_date - interval '3 month') AND date_trunc('month', current_date) OR (i.dthr_atendimento <= date_trunc('month', current_date - interval '3 month') AND i.dthr_alta >= date_trunc('month', current_date))) THEN 1 END)::text,
            COUNT(CASE WHEN (i.dthr_atendimento BETWEEN date_trunc('month', current_date - interval '6 month') AND date_trunc('month', current_date) OR i.dthr_alta BETWEEN date_trunc('month', current_date - interval '6 month') AND date_trunc('month', current_date) OR (i.dthr_atendimento <= date_trunc('month', current_date - interval '6 month') AND i.dthr_alta >= date_trunc('month', current_date))) THEN 1 END)::text,
            COUNT(CASE WHEN (i.dthr_atendimento BETWEEN date_trunc('month', current_date - interval '12 month') AND date_trunc('month', current_date) OR i.dthr_alta BETWEEN date_trunc('month', current_date - interval '12 month') AND date_trunc('month', current_date) OR (i.dthr_atendimento <= date_trunc('month', current_date - interval '12 month') AND i.dthr_alta >= date_trunc('month', current_date))) THEN 1 END)::text,
            COUNT(CASE WHEN (i.dthr_atendimento BETWEEN date_trunc('month', current_date - interval '120 month') AND date_trunc('month', current_date) OR i.dthr_alta BETWEEN date_trunc('month', current_date - interval '120 month') AND date_trunc('month', current_date) OR (i.dthr_atendimento <= date_trunc('month', current_date - interval '120 month') AND i.dthr_alta >= date_trunc('month', current_date))) THEN 1 END)::text,
            i.id_hospital,
            i.id_enterprise
        FROM isa_internacoes i
        JOIN isa_pacientes p 
            ON i.paciente_id = p.id
                and i.id_enterprise = p.id_enterprise
        where p.sexo = 'F' and p.idade_hoje <= 70 and p.idade_hoje >= 61
        group by i.id_hospital, i.id_enterprise
        UNION
        SELECT
            'pacientes_masculino_faixa_etaria_ate_71_80',
            COUNT(CASE WHEN (i.dthr_atendimento BETWEEN date_trunc('month', current_date - interval '1 month') AND date_trunc('month', current_date) OR i.dthr_alta BETWEEN date_trunc('month', current_date - interval '1 month') AND date_trunc('month', current_date) OR (i.dthr_atendimento <= date_trunc('month', current_date - interval '1 month') AND i.dthr_alta >= date_trunc('month', current_date))) THEN 1 END)::text,
            COUNT(CASE WHEN (i.dthr_atendimento BETWEEN date_trunc('month', current_date - interval '3 month') AND date_trunc('month', current_date) OR i.dthr_alta BETWEEN date_trunc('month', current_date - interval '3 month') AND date_trunc('month', current_date) OR (i.dthr_atendimento <= date_trunc('month', current_date - interval '3 month') AND i.dthr_alta >= date_trunc('month', current_date))) THEN 1 END)::text,
            COUNT(CASE WHEN (i.dthr_atendimento BETWEEN date_trunc('month', current_date - interval '6 month') AND date_trunc('month', current_date) OR i.dthr_alta BETWEEN date_trunc('month', current_date - interval '6 month') AND date_trunc('month', current_date) OR (i.dthr_atendimento <= date_trunc('month', current_date - interval '6 month') AND i.dthr_alta >= date_trunc('month', current_date))) THEN 1 END)::text,
            COUNT(CASE WHEN (i.dthr_atendimento BETWEEN date_trunc('month', current_date - interval '12 month') AND date_trunc('month', current_date) OR i.dthr_alta BETWEEN date_trunc('month', current_date - interval '12 month') AND date_trunc('month', current_date) OR (i.dthr_atendimento <= date_trunc('month', current_date - interval '12 month') AND i.dthr_alta >= date_trunc('month', current_date))) THEN 1 END)::text,
            COUNT(CASE WHEN (i.dthr_atendimento BETWEEN date_trunc('month', current_date - interval '120 month') AND date_trunc('month', current_date) OR i.dthr_alta BETWEEN date_trunc('month', current_date - interval '120 month') AND date_trunc('month', current_date) OR (i.dthr_atendimento <= date_trunc('month', current_date - interval '120 month') AND i.dthr_alta >= date_trunc('month', current_date))) THEN 1 END)::text,
            i.id_hospital,
            i.id_enterprise
        FROM isa_internacoes i
        JOIN isa_pacientes p 
            ON i.paciente_id = p.id
                and i.id_enterprise = p.id_enterprise
        where p.sexo = 'M' and p.idade_hoje <= 80 and p.idade_hoje >= 71
        group by i.id_hospital, i.id_enterprise
        UNION
        SELECT
            'pacientes_feminino_faixa_etaria_ate_71_80',
            COUNT(CASE WHEN (i.dthr_atendimento BETWEEN date_trunc('month', current_date - interval '1 month') AND date_trunc('month', current_date) OR i.dthr_alta BETWEEN date_trunc('month', current_date - interval '1 month') AND date_trunc('month', current_date) OR (i.dthr_atendimento <= date_trunc('month', current_date - interval '1 month') AND i.dthr_alta >= date_trunc('month', current_date))) THEN 1 END)::text,
            COUNT(CASE WHEN (i.dthr_atendimento BETWEEN date_trunc('month', current_date - interval '3 month') AND date_trunc('month', current_date) OR i.dthr_alta BETWEEN date_trunc('month', current_date - interval '3 month') AND date_trunc('month', current_date) OR (i.dthr_atendimento <= date_trunc('month', current_date - interval '3 month') AND i.dthr_alta >= date_trunc('month', current_date))) THEN 1 END)::text,
            COUNT(CASE WHEN (i.dthr_atendimento BETWEEN date_trunc('month', current_date - interval '6 month') AND date_trunc('month', current_date) OR i.dthr_alta BETWEEN date_trunc('month', current_date - interval '6 month') AND date_trunc('month', current_date) OR (i.dthr_atendimento <= date_trunc('month', current_date - interval '6 month') AND i.dthr_alta >= date_trunc('month', current_date))) THEN 1 END)::text,
            COUNT(CASE WHEN (i.dthr_atendimento BETWEEN date_trunc('month', current_date - interval '12 month') AND date_trunc('month', current_date) OR i.dthr_alta BETWEEN date_trunc('month', current_date - interval '12 month') AND date_trunc('month', current_date) OR (i.dthr_atendimento <= date_trunc('month', current_date - interval '12 month') AND i.dthr_alta >= date_trunc('month', current_date))) THEN 1 END)::text,
            COUNT(CASE WHEN (i.dthr_atendimento BETWEEN date_trunc('month', current_date - interval '120 month') AND date_trunc('month', current_date) OR i.dthr_alta BETWEEN date_trunc('month', current_date - interval '120 month') AND date_trunc('month', current_date) OR (i.dthr_atendimento <= date_trunc('month', current_date - interval '120 month') AND i.dthr_alta >= date_trunc('month', current_date))) THEN 1 END)::text,
            i.id_hospital,
            i.id_enterprise
        FROM isa_internacoes i
        JOIN isa_pacientes p 
            ON i.paciente_id = p.id
                and i.id_enterprise = p.id_enterprise
        where p.sexo = 'F' and p.idade_hoje <= 80 and p.idade_hoje >= 71
        group by i.id_hospital, i.id_enterprise
        UNION
        SELECT
            'pacientes_masculino_faixa_etaria_ate_81_90',
            COUNT(CASE WHEN (i.dthr_atendimento BETWEEN date_trunc('month', current_date - interval '1 month') AND date_trunc('month', current_date) OR i.dthr_alta BETWEEN date_trunc('month', current_date - interval '1 month') AND date_trunc('month', current_date) OR (i.dthr_atendimento <= date_trunc('month', current_date - interval '1 month') AND i.dthr_alta >= date_trunc('month', current_date))) THEN 1 END)::text,
            COUNT(CASE WHEN (i.dthr_atendimento BETWEEN date_trunc('month', current_date - interval '3 month') AND date_trunc('month', current_date) OR i.dthr_alta BETWEEN date_trunc('month', current_date - interval '3 month') AND date_trunc('month', current_date) OR (i.dthr_atendimento <= date_trunc('month', current_date - interval '3 month') AND i.dthr_alta >= date_trunc('month', current_date))) THEN 1 END)::text,
            COUNT(CASE WHEN (i.dthr_atendimento BETWEEN date_trunc('month', current_date - interval '6 month') AND date_trunc('month', current_date) OR i.dthr_alta BETWEEN date_trunc('month', current_date - interval '6 month') AND date_trunc('month', current_date) OR (i.dthr_atendimento <= date_trunc('month', current_date - interval '6 month') AND i.dthr_alta >= date_trunc('month', current_date))) THEN 1 END)::text,
            COUNT(CASE WHEN (i.dthr_atendimento BETWEEN date_trunc('month', current_date - interval '12 month') AND date_trunc('month', current_date) OR i.dthr_alta BETWEEN date_trunc('month', current_date - interval '12 month') AND date_trunc('month', current_date) OR (i.dthr_atendimento <= date_trunc('month', current_date - interval '12 month') AND i.dthr_alta >= date_trunc('month', current_date))) THEN 1 END)::text,
            COUNT(CASE WHEN (i.dthr_atendimento BETWEEN date_trunc('month', current_date - interval '120 month') AND date_trunc('month', current_date) OR i.dthr_alta BETWEEN date_trunc('month', current_date - interval '120 month') AND date_trunc('month', current_date) OR (i.dthr_atendimento <= date_trunc('month', current_date - interval '120 month') AND i.dthr_alta >= date_trunc('month', current_date))) THEN 1 END)::text,
            i.id_hospital,
            i.id_enterprise
        FROM isa_internacoes i
        JOIN isa_pacientes p 
            ON i.paciente_id = p.id
                and i.id_enterprise = p.id_enterprise
        where p.sexo = 'M' and p.idade_hoje <= 90 and p.idade_hoje >= 81
        group by i.id_hospital, i.id_enterprise
        UNION
        SELECT
            'pacientes_feminino_faixa_etaria_ate_81_90',
            COUNT(CASE WHEN (i.dthr_atendimento BETWEEN date_trunc('month', current_date - interval '1 month') AND date_trunc('month', current_date) OR i.dthr_alta BETWEEN date_trunc('month', current_date - interval '1 month') AND date_trunc('month', current_date) OR (i.dthr_atendimento <= date_trunc('month', current_date - interval '1 month') AND i.dthr_alta >= date_trunc('month', current_date))) THEN 1 END)::text,
            COUNT(CASE WHEN (i.dthr_atendimento BETWEEN date_trunc('month', current_date - interval '3 month') AND date_trunc('month', current_date) OR i.dthr_alta BETWEEN date_trunc('month', current_date - interval '3 month') AND date_trunc('month', current_date) OR (i.dthr_atendimento <= date_trunc('month', current_date - interval '3 month') AND i.dthr_alta >= date_trunc('month', current_date))) THEN 1 END)::text,
            COUNT(CASE WHEN (i.dthr_atendimento BETWEEN date_trunc('month', current_date - interval '6 month') AND date_trunc('month', current_date) OR i.dthr_alta BETWEEN date_trunc('month', current_date - interval '6 month') AND date_trunc('month', current_date) OR (i.dthr_atendimento <= date_trunc('month', current_date - interval '6 month') AND i.dthr_alta >= date_trunc('month', current_date))) THEN 1 END)::text,
            COUNT(CASE WHEN (i.dthr_atendimento BETWEEN date_trunc('month', current_date - interval '12 month') AND date_trunc('month', current_date) OR i.dthr_alta BETWEEN date_trunc('month', current_date - interval '12 month') AND date_trunc('month', current_date) OR (i.dthr_atendimento <= date_trunc('month', current_date - interval '12 month') AND i.dthr_alta >= date_trunc('month', current_date))) THEN 1 END)::text,
            COUNT(CASE WHEN (i.dthr_atendimento BETWEEN date_trunc('month', current_date - interval '120 month') AND date_trunc('month', current_date) OR i.dthr_alta BETWEEN date_trunc('month', current_date - interval '120 month') AND date_trunc('month', current_date) OR (i.dthr_atendimento <= date_trunc('month', current_date - interval '120 month') AND i.dthr_alta >= date_trunc('month', current_date))) THEN 1 END)::text,
            i.id_hospital,
            i.id_enterprise
        FROM isa_internacoes i
        JOIN isa_pacientes p 
            ON i.paciente_id = p.id
                and i.id_enterprise = p.id_enterprise
        where p.sexo = 'F' and p.idade_hoje <= 90 and p.idade_hoje >= 81
        group by i.id_hospital, i.id_enterprise
        UNION
        SELECT
            'pacientes_masculino_faixa_etaria_ate_91_100',
            COUNT(CASE WHEN (i.dthr_atendimento BETWEEN date_trunc('month', current_date - interval '1 month') AND date_trunc('month', current_date) OR i.dthr_alta BETWEEN date_trunc('month', current_date - interval '1 month') AND date_trunc('month', current_date) OR (i.dthr_atendimento <= date_trunc('month', current_date - interval '1 month') AND i.dthr_alta >= date_trunc('month', current_date))) THEN 1 END)::text,
            COUNT(CASE WHEN (i.dthr_atendimento BETWEEN date_trunc('month', current_date - interval '3 month') AND date_trunc('month', current_date) OR i.dthr_alta BETWEEN date_trunc('month', current_date - interval '3 month') AND date_trunc('month', current_date) OR (i.dthr_atendimento <= date_trunc('month', current_date - interval '3 month') AND i.dthr_alta >= date_trunc('month', current_date))) THEN 1 END)::text,
            COUNT(CASE WHEN (i.dthr_atendimento BETWEEN date_trunc('month', current_date - interval '6 month') AND date_trunc('month', current_date) OR i.dthr_alta BETWEEN date_trunc('month', current_date - interval '6 month') AND date_trunc('month', current_date) OR (i.dthr_atendimento <= date_trunc('month', current_date - interval '6 month') AND i.dthr_alta >= date_trunc('month', current_date))) THEN 1 END)::text,
            COUNT(CASE WHEN (i.dthr_atendimento BETWEEN date_trunc('month', current_date - interval '12 month') AND date_trunc('month', current_date) OR i.dthr_alta BETWEEN date_trunc('month', current_date - interval '12 month') AND date_trunc('month', current_date) OR (i.dthr_atendimento <= date_trunc('month', current_date - interval '12 month') AND i.dthr_alta >= date_trunc('month', current_date))) THEN 1 END)::text,
            COUNT(CASE WHEN (i.dthr_atendimento BETWEEN date_trunc('month', current_date - interval '120 month') AND date_trunc('month', current_date) OR i.dthr_alta BETWEEN date_trunc('month', current_date - interval '120 month') AND date_trunc('month', current_date) OR (i.dthr_atendimento <= date_trunc('month', current_date - interval '120 month') AND i.dthr_alta >= date_trunc('month', current_date))) THEN 1 END)::text,
            i.id_hospital,
            i.id_enterprise
        FROM isa_internacoes i
        JOIN isa_pacientes p 
            ON i.paciente_id = p.id
                and i.id_enterprise = p.id_enterprise
        where p.sexo = 'M' and p.idade_hoje <= 100 and p.idade_hoje >= 91
        group by i.id_hospital, i.id_enterprise
        UNION
        SELECT
            'pacientes_feminino_faixa_etaria_ate_91_100',
            COUNT(CASE WHEN (i.dthr_atendimento BETWEEN date_trunc('month', current_date - interval '1 month') AND date_trunc('month', current_date) OR i.dthr_alta BETWEEN date_trunc('month', current_date - interval '1 month') AND date_trunc('month', current_date) OR (i.dthr_atendimento <= date_trunc('month', current_date - interval '1 month') AND i.dthr_alta >= date_trunc('month', current_date))) THEN 1 END)::text,
            COUNT(CASE WHEN (i.dthr_atendimento BETWEEN date_trunc('month', current_date - interval '3 month') AND date_trunc('month', current_date) OR i.dthr_alta BETWEEN date_trunc('month', current_date - interval '3 month') AND date_trunc('month', current_date) OR (i.dthr_atendimento <= date_trunc('month', current_date - interval '3 month') AND i.dthr_alta >= date_trunc('month', current_date))) THEN 1 END)::text,
            COUNT(CASE WHEN (i.dthr_atendimento BETWEEN date_trunc('month', current_date - interval '6 month') AND date_trunc('month', current_date) OR i.dthr_alta BETWEEN date_trunc('month', current_date - interval '6 month') AND date_trunc('month', current_date) OR (i.dthr_atendimento <= date_trunc('month', current_date - interval '6 month') AND i.dthr_alta >= date_trunc('month', current_date))) THEN 1 END)::text,
            COUNT(CASE WHEN (i.dthr_atendimento BETWEEN date_trunc('month', current_date - interval '12 month') AND date_trunc('month', current_date) OR i.dthr_alta BETWEEN date_trunc('month', current_date - interval '12 month') AND date_trunc('month', current_date) OR (i.dthr_atendimento <= date_trunc('month', current_date - interval '12 month') AND i.dthr_alta >= date_trunc('month', current_date))) THEN 1 END)::text,
            COUNT(CASE WHEN (i.dthr_atendimento BETWEEN date_trunc('month', current_date - interval '120 month') AND date_trunc('month', current_date) OR i.dthr_alta BETWEEN date_trunc('month', current_date - interval '120 month') AND date_trunc('month', current_date) OR (i.dthr_atendimento <= date_trunc('month', current_date - interval '120 month') AND i.dthr_alta >= date_trunc('month', current_date))) THEN 1 END)::text,
            i.id_hospital,
            i.id_enterprise
        FROM isa_internacoes i
        JOIN isa_pacientes p 
            ON i.paciente_id = p.id
                and i.id_enterprise = p.id_enterprise
        where p.sexo = 'F' and p.idade_hoje <= 100 and p.idade_hoje >= 91
        group by i.id_hospital, i.id_enterprise
        UNION
        SELECT
            'pacientes_masculino_faixa_etaria_ate_100_mais',
            COUNT(CASE WHEN (i.dthr_atendimento BETWEEN date_trunc('month', current_date - interval '1 month') AND date_trunc('month', current_date) OR i.dthr_alta BETWEEN date_trunc('month', current_date - interval '1 month') AND date_trunc('month', current_date) OR (i.dthr_atendimento <= date_trunc('month', current_date - interval '1 month') AND i.dthr_alta >= date_trunc('month', current_date))) THEN 1 END)::text,
            COUNT(CASE WHEN (i.dthr_atendimento BETWEEN date_trunc('month', current_date - interval '3 month') AND date_trunc('month', current_date) OR i.dthr_alta BETWEEN date_trunc('month', current_date - interval '3 month') AND date_trunc('month', current_date) OR (i.dthr_atendimento <= date_trunc('month', current_date - interval '3 month') AND i.dthr_alta >= date_trunc('month', current_date))) THEN 1 END)::text,
            COUNT(CASE WHEN (i.dthr_atendimento BETWEEN date_trunc('month', current_date - interval '6 month') AND date_trunc('month', current_date) OR i.dthr_alta BETWEEN date_trunc('month', current_date - interval '6 month') AND date_trunc('month', current_date) OR (i.dthr_atendimento <= date_trunc('month', current_date - interval '6 month') AND i.dthr_alta >= date_trunc('month', current_date))) THEN 1 END)::text,
            COUNT(CASE WHEN (i.dthr_atendimento BETWEEN date_trunc('month', current_date - interval '12 month') AND date_trunc('month', current_date) OR i.dthr_alta BETWEEN date_trunc('month', current_date - interval '12 month') AND date_trunc('month', current_date) OR (i.dthr_atendimento <= date_trunc('month', current_date - interval '12 month') AND i.dthr_alta >= date_trunc('month', current_date))) THEN 1 END)::text,
            COUNT(CASE WHEN (i.dthr_atendimento BETWEEN date_trunc('month', current_date - interval '120 month') AND date_trunc('month', current_date) OR i.dthr_alta BETWEEN date_trunc('month', current_date - interval '120 month') AND date_trunc('month', current_date) OR (i.dthr_atendimento <= date_trunc('month', current_date - interval '120 month') AND i.dthr_alta >= date_trunc('month', current_date))) THEN 1 END)::text,
            i.id_hospital,
            i.id_enterprise
        FROM isa_internacoes i
        JOIN isa_pacientes p 
            ON i.paciente_id = p.id
                and i.id_enterprise = p.id_enterprise
        where p.sexo = 'M' and p.idade_hoje > 100
        group by i.id_hospital, i.id_enterprise
        UNION
        SELECT
            'pacientes_feminino_faixa_etaria_ate_100_mais',
            COUNT(CASE WHEN (i.dthr_atendimento BETWEEN date_trunc('month', current_date - interval '1 month') AND date_trunc('month', current_date) OR i.dthr_alta BETWEEN date_trunc('month', current_date - interval '1 month') AND date_trunc('month', current_date) OR (i.dthr_atendimento <= date_trunc('month', current_date - interval '1 month') AND i.dthr_alta >= date_trunc('month', current_date))) THEN 1 END)::text,
            COUNT(CASE WHEN (i.dthr_atendimento BETWEEN date_trunc('month', current_date - interval '3 month') AND date_trunc('month', current_date) OR i.dthr_alta BETWEEN date_trunc('month', current_date - interval '3 month') AND date_trunc('month', current_date) OR (i.dthr_atendimento <= date_trunc('month', current_date - interval '3 month') AND i.dthr_alta >= date_trunc('month', current_date))) THEN 1 END)::text,
            COUNT(CASE WHEN (i.dthr_atendimento BETWEEN date_trunc('month', current_date - interval '6 month') AND date_trunc('month', current_date) OR i.dthr_alta BETWEEN date_trunc('month', current_date - interval '6 month') AND date_trunc('month', current_date) OR (i.dthr_atendimento <= date_trunc('month', current_date - interval '6 month') AND i.dthr_alta >= date_trunc('month', current_date))) THEN 1 END)::text,
            COUNT(CASE WHEN (i.dthr_atendimento BETWEEN date_trunc('month', current_date - interval '12 month') AND date_trunc('month', current_date) OR i.dthr_alta BETWEEN date_trunc('month', current_date - interval '12 month') AND date_trunc('month', current_date) OR (i.dthr_atendimento <= date_trunc('month', current_date - interval '12 month') AND i.dthr_alta >= date_trunc('month', current_date))) THEN 1 END)::text,
            COUNT(CASE WHEN (i.dthr_atendimento BETWEEN date_trunc('month', current_date - interval '120 month') AND date_trunc('month', current_date) OR i.dthr_alta BETWEEN date_trunc('month', current_date - interval '120 month') AND date_trunc('month', current_date) OR (i.dthr_atendimento <= date_trunc('month', current_date - interval '120 month') AND i.dthr_alta >= date_trunc('month', current_date))) THEN 1 END)::text,
            i.id_hospital,
            i.id_enterprise
        FROM isa_internacoes i
        JOIN isa_pacientes p 
            ON i.paciente_id = p.id
                and i.id_enterprise = p.id_enterprise
        where p.sexo = 'F' and p.idade_hoje > 100
        group by i.id_hospital, i.id_enterprise
        UNION
        SELECT 
            'pacientes_masculino_faixa_etaria_mediana',
            PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY idade_hoje) FILTER (WHERE dthr_atendimento BETWEEN date_trunc('month', current_date - interval '1 month') AND date_trunc('month', current_date)OR dthr_alta BETWEEN date_trunc('month', current_date - interval '1 month') AND date_trunc('month', current_date)OR (dthr_atendimento <= date_trunc('month', current_date - interval '1 month') AND dthr_alta >= date_trunc('month', current_date)))::text,
            PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY idade_hoje) FILTER (WHERE dthr_atendimento BETWEEN date_trunc('month', current_date - interval '3 month') AND date_trunc('month', current_date)OR dthr_alta BETWEEN date_trunc('month', current_date - interval '3 month') AND date_trunc('month', current_date)OR (dthr_atendimento <= date_trunc('month', current_date - interval '3 month') AND dthr_alta >= date_trunc('month', current_date)))::text,
            PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY idade_hoje) FILTER (WHERE dthr_atendimento BETWEEN date_trunc('month', current_date - interval '6 month') AND date_trunc('month', current_date)OR dthr_alta BETWEEN date_trunc('month', current_date - interval '6 month') AND date_trunc('month', current_date)OR (dthr_atendimento <= date_trunc('month', current_date - interval '6 month') AND dthr_alta >= date_trunc('month', current_date)))::text,
            PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY idade_hoje) FILTER (WHERE dthr_atendimento BETWEEN date_trunc('month', current_date - interval '12 month') AND date_trunc('month', current_date)OR dthr_alta BETWEEN date_trunc('month', current_date - interval '12 month') AND date_trunc('month', current_date)OR (dthr_atendimento <= date_trunc('month', current_date - interval '12 month') AND dthr_alta >= date_trunc('month', current_date)))::text,
            PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY idade_hoje) FILTER (WHERE dthr_atendimento BETWEEN date_trunc('month', current_date - interval '120 month') AND date_trunc('month', current_date)OR dthr_alta BETWEEN date_trunc('month', current_date - interval '120 month') AND date_trunc('month', current_date)OR (dthr_atendimento <= date_trunc('month', current_date - interval '120 month') AND dthr_alta >= date_trunc('month', current_date)))::text,
            i.id_hospital,
            i.id_enterprise
        FROM isa_internacoes i
        JOIN isa_pacientes p 
            ON i.paciente_id = p.id
                and i.id_enterprise = p.id_enterprise
        where p.sexo = 'M'
        group by i.id_hospital, i.id_enterprise
        UNION
        SELECT 
            'pacientes_masculino_faixa_etaria_mediana',
            PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY idade_hoje) FILTER (WHERE dthr_atendimento BETWEEN date_trunc('month', current_date - interval '1 month') AND date_trunc('month', current_date)OR dthr_alta BETWEEN date_trunc('month', current_date - interval '1 month') AND date_trunc('month', current_date)OR (dthr_atendimento <= date_trunc('month', current_date - interval '1 month') AND dthr_alta >= date_trunc('month', current_date)))::text,
            PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY idade_hoje) FILTER (WHERE dthr_atendimento BETWEEN date_trunc('month', current_date - interval '3 month') AND date_trunc('month', current_date)OR dthr_alta BETWEEN date_trunc('month', current_date - interval '3 month') AND date_trunc('month', current_date)OR (dthr_atendimento <= date_trunc('month', current_date - interval '3 month') AND dthr_alta >= date_trunc('month', current_date)))::text,
            PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY idade_hoje) FILTER (WHERE dthr_atendimento BETWEEN date_trunc('month', current_date - interval '6 month') AND date_trunc('month', current_date)OR dthr_alta BETWEEN date_trunc('month', current_date - interval '6 month') AND date_trunc('month', current_date)OR (dthr_atendimento <= date_trunc('month', current_date - interval '6 month') AND dthr_alta >= date_trunc('month', current_date)))::text,
            PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY idade_hoje) FILTER (WHERE dthr_atendimento BETWEEN date_trunc('month', current_date - interval '12 month') AND date_trunc('month', current_date)OR dthr_alta BETWEEN date_trunc('month', current_date - interval '12 month') AND date_trunc('month', current_date)OR (dthr_atendimento <= date_trunc('month', current_date - interval '12 month') AND dthr_alta >= date_trunc('month', current_date)))::text,
            PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY idade_hoje) FILTER (WHERE dthr_atendimento BETWEEN date_trunc('month', current_date - interval '120 month') AND date_trunc('month', current_date)OR dthr_alta BETWEEN date_trunc('month', current_date - interval '120 month') AND date_trunc('month', current_date)OR (dthr_atendimento <= date_trunc('month', current_date - interval '120 month') AND dthr_alta >= date_trunc('month', current_date)))::text,
            i.id_hospital,
            i.id_enterprise
        FROM isa_internacoes i
        JOIN isa_pacientes p 
            ON i.paciente_id = p.id
                and i.id_enterprise = p.id_enterprise
        where p.sexo = 'F'
        group by i.id_hospital, i.id_enterprise
        UNION
        SELECT 
            'pacientes_geral_faixa_etaria_mediana',
            PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY idade_hoje) FILTER (WHERE dthr_atendimento BETWEEN date_trunc('month', current_date - interval '1 month') AND date_trunc('month', current_date)OR dthr_alta BETWEEN date_trunc('month', current_date - interval '1 month') AND date_trunc('month', current_date)OR (dthr_atendimento <= date_trunc('month', current_date - interval '1 month') AND dthr_alta >= date_trunc('month', current_date)))::text,
            PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY idade_hoje) FILTER (WHERE dthr_atendimento BETWEEN date_trunc('month', current_date - interval '3 month') AND date_trunc('month', current_date)OR dthr_alta BETWEEN date_trunc('month', current_date - interval '3 month') AND date_trunc('month', current_date)OR (dthr_atendimento <= date_trunc('month', current_date - interval '3 month') AND dthr_alta >= date_trunc('month', current_date)))::text,
            PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY idade_hoje) FILTER (WHERE dthr_atendimento BETWEEN date_trunc('month', current_date - interval '6 month') AND date_trunc('month', current_date)OR dthr_alta BETWEEN date_trunc('month', current_date - interval '6 month') AND date_trunc('month', current_date)OR (dthr_atendimento <= date_trunc('month', current_date - interval '6 month') AND dthr_alta >= date_trunc('month', current_date)))::text,
            PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY idade_hoje) FILTER (WHERE dthr_atendimento BETWEEN date_trunc('month', current_date - interval '12 month') AND date_trunc('month', current_date)OR dthr_alta BETWEEN date_trunc('month', current_date - interval '12 month') AND date_trunc('month', current_date)OR (dthr_atendimento <= date_trunc('month', current_date - interval '12 month') AND dthr_alta >= date_trunc('month', current_date)))::text,
            PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY idade_hoje) FILTER (WHERE dthr_atendimento BETWEEN date_trunc('month', current_date - interval '120 month') AND date_trunc('month', current_date)OR dthr_alta BETWEEN date_trunc('month', current_date - interval '120 month') AND date_trunc('month', current_date)OR (dthr_atendimento <= date_trunc('month', current_date - interval '120 month') AND dthr_alta >= date_trunc('month', current_date)))::text,
            i.id_hospital,
            i.id_enterprise
        FROM isa_internacoes i
        JOIN isa_pacientes p 
            ON i.paciente_id = p.id
                and i.id_enterprise = p.id_enterprise
        group by i.id_hospital, i.id_enterprise
        UNION
        SELECT 'pacientes_por_local_' || local_encontro
            , COUNT(DISTINCT case when ie.dt_encontro between date_trunc('month', current_date - interval '1' month) and date_trunc('month', current_date) then ie.prontuario end)::text
            , COUNT(DISTINCT case when ie.dt_encontro between date_trunc('month', current_date - interval '3' month) and date_trunc('month', current_date) then ie.prontuario end)::text
            , COUNT(DISTINCT case when ie.dt_encontro between date_trunc('month', current_date - interval '6' month) and date_trunc('month', current_date) then ie.prontuario end)::text
            , COUNT(DISTINCT case when ie.dt_encontro between date_trunc('month', current_date - interval '12' month) and date_trunc('month', current_date) then ie.prontuario end)::text
            , COUNT(DISTINCT case when ie.dt_encontro between date_trunc('month', current_date - interval '120' month) and date_trunc('month', current_date) then ie.prontuario end)::text
            , ie.id_hospital
            , ie.id_enterprise
        from isa_encontro ie  
        inner join isa_pacientes ip 
            on ip.id = ie.prontuario::bigint
                and ip.id_enterprise = ie.id_enterprise
        group by local_encontro, ie.id_hospital, ie.id_enterprise
        UNION
        SELECT 
            'supeitas_por_probabilidade_alta',
            COUNT(DISTINCT is2.paciente_id) FILTER (WHERE is2.dt_infeccao BETWEEN date_trunc('month', current_date - interval '1 month') AND date_trunc('month', current_date))::text,
            COUNT(DISTINCT is2.paciente_id) FILTER (WHERE is2.dt_infeccao BETWEEN date_trunc('month', current_date - interval '3 month') AND date_trunc('month', current_date))::text,
            COUNT(DISTINCT is2.paciente_id) FILTER (WHERE is2.dt_infeccao BETWEEN date_trunc('month', current_date - interval '6 month') AND date_trunc('month', current_date))::text,
            COUNT(DISTINCT is2.paciente_id) FILTER (WHERE is2.dt_infeccao BETWEEN date_trunc('month', current_date - interval '12 month') AND date_trunc('month', current_date))::text,
            COUNT(DISTINCT is2.paciente_id) FILTER (WHERE is2.dt_infeccao BETWEEN date_trunc('month', current_date - interval '120 month') AND date_trunc('month', current_date))::text,
            is2.id_hospital, 
            is2.id_enterprise
        FROM isa_suspeita is2
        JOIN isa_pacientes ip 
            ON is2.paciente_id = ip.id
                and is2.id_enterprise = ip.id_enterprise
        JOIN isa_infeccao ii 
            ON is2.paciente_id = ii.paciente_id 
                and is2.id_enterprise = ii.id_enterprise
                and date_trunc('day', ii.dt_infeccao) = date_trunc('day', is2.dt_infeccao) 
        where is2.max_prob >= 0.75
        group by is2.id_hospital, is2.id_enterprise
        UNION
        SELECT 
            'supeitas_por_probabilidade_media',
            COUNT(DISTINCT is2.paciente_id) FILTER (WHERE is2.dt_infeccao BETWEEN date_trunc('month', current_date - interval '1 month') AND date_trunc('month', current_date))::text,
            COUNT(DISTINCT is2.paciente_id) FILTER (WHERE is2.dt_infeccao BETWEEN date_trunc('month', current_date - interval '3 month') AND date_trunc('month', current_date))::text,
            COUNT(DISTINCT is2.paciente_id) FILTER (WHERE is2.dt_infeccao BETWEEN date_trunc('month', current_date - interval '6 month') AND date_trunc('month', current_date))::text,
            COUNT(DISTINCT is2.paciente_id) FILTER (WHERE is2.dt_infeccao BETWEEN date_trunc('month', current_date - interval '12 month') AND date_trunc('month', current_date))::text,
            COUNT(DISTINCT is2.paciente_id) FILTER (WHERE is2.dt_infeccao BETWEEN date_trunc('month', current_date - interval '120 month') AND date_trunc('month', current_date))::text,
            is2.id_hospital, 
            is2.id_enterprise
        FROM isa_suspeita is2
        JOIN isa_pacientes ip 
            ON is2.paciente_id = ip.id
                and is2.id_enterprise = ip.id_enterprise
        JOIN isa_infeccao ii 
            ON is2.paciente_id = ii.paciente_id 
                and is2.id_enterprise = ii.id_enterprise
                and date_trunc('day', ii.dt_infeccao) = date_trunc('day', is2.dt_infeccao) 
        where is2.max_prob < 0.75 and is2.max_prob >= 0.5
        group by is2.id_hospital, is2.id_enterprise
        UNION
        SELECT 
            'suspeitas_por_tipo_IPCS_alta',
            COUNT(DISTINCT is2.paciente_id) FILTER (WHERE is2.dt_infeccao BETWEEN date_trunc('month', current_date - interval '1 month') AND date_trunc('month', current_date))::text,
            COUNT(DISTINCT is2.paciente_id) FILTER (WHERE is2.dt_infeccao BETWEEN date_trunc('month', current_date - interval '3 month') AND date_trunc('month', current_date))::text,
            COUNT(DISTINCT is2.paciente_id) FILTER (WHERE is2.dt_infeccao BETWEEN date_trunc('month', current_date - interval '6 month') AND date_trunc('month', current_date))::text,
            COUNT(DISTINCT is2.paciente_id) FILTER (WHERE is2.dt_infeccao BETWEEN date_trunc('month', current_date - interval '12 month') AND date_trunc('month', current_date))::text,
            COUNT(DISTINCT is2.paciente_id) FILTER (WHERE is2.dt_infeccao BETWEEN date_trunc('month', current_date - interval '120 month') AND date_trunc('month', current_date))::text,
            is2.id_hospital, 
            is2.id_enterprise
        FROM isa_suspeita is2
        JOIN isa_pacientes ip 
            ON is2.paciente_id = ip.id
                and is2.id_enterprise = ip.id_enterprise
        JOIN isa_infeccao ii 
            ON is2.paciente_id = ii.paciente_id 
                and is2.id_enterprise = ii.id_enterprise
                and date_trunc('day', ii.dt_infeccao) = date_trunc('day', is2.dt_infeccao) 
        where is2.max_prob >= 0.75 AND ii.pred_ipcs = 1
        group by is2.id_hospital, is2.id_enterprise
        UNION
        SELECT 
            'suspeitas_por_tipo_IPCS_media',
            COUNT(DISTINCT is2.paciente_id) FILTER (WHERE is2.dt_infeccao BETWEEN date_trunc('month', current_date - interval '1 month') AND date_trunc('month', current_date))::text,
            COUNT(DISTINCT is2.paciente_id) FILTER (WHERE is2.dt_infeccao BETWEEN date_trunc('month', current_date - interval '3 month') AND date_trunc('month', current_date))::text,
            COUNT(DISTINCT is2.paciente_id) FILTER (WHERE is2.dt_infeccao BETWEEN date_trunc('month', current_date - interval '6 month') AND date_trunc('month', current_date))::text,
            COUNT(DISTINCT is2.paciente_id) FILTER (WHERE is2.dt_infeccao BETWEEN date_trunc('month', current_date - interval '12 month') AND date_trunc('month', current_date))::text,
            COUNT(DISTINCT is2.paciente_id) FILTER (WHERE is2.dt_infeccao BETWEEN date_trunc('month', current_date - interval '120 month') AND date_trunc('month', current_date))::text,
            is2.id_hospital, 
            is2.id_enterprise
        FROM isa_suspeita is2
        JOIN isa_pacientes ip 
            ON is2.paciente_id = ip.id
                and is2.id_enterprise = ip.id_enterprise
        JOIN isa_infeccao ii 
            ON is2.paciente_id = ii.paciente_id 
                and is2.id_enterprise = ii.id_enterprise
                and date_trunc('day', ii.dt_infeccao) = date_trunc('day', is2.dt_infeccao) 
        where is2.max_prob < 0.75 AND is2.max_prob >= 0.5 AND ii.pred_ipcs = 1
        group by is2.id_hospital, is2.id_enterprise
        UNION
        SELECT 
            'suspeitas_por_tipo_ISC_alta',
            COUNT(DISTINCT is2.paciente_id) FILTER (WHERE is2.dt_infeccao BETWEEN date_trunc('month', current_date - interval '1 month') AND date_trunc('month', current_date))::text,
            COUNT(DISTINCT is2.paciente_id) FILTER (WHERE is2.dt_infeccao BETWEEN date_trunc('month', current_date - interval '3 month') AND date_trunc('month', current_date))::text,
            COUNT(DISTINCT is2.paciente_id) FILTER (WHERE is2.dt_infeccao BETWEEN date_trunc('month', current_date - interval '6 month') AND date_trunc('month', current_date))::text,
            COUNT(DISTINCT is2.paciente_id) FILTER (WHERE is2.dt_infeccao BETWEEN date_trunc('month', current_date - interval '12 month') AND date_trunc('month', current_date))::text,
            COUNT(DISTINCT is2.paciente_id) FILTER (WHERE is2.dt_infeccao BETWEEN date_trunc('month', current_date - interval '120 month') AND date_trunc('month', current_date))::text,
            is2.id_hospital, 
            is2.id_enterprise
        FROM isa_suspeita is2
        JOIN isa_pacientes ip 
            ON is2.paciente_id = ip.id
                and is2.id_enterprise = ip.id_enterprise
        JOIN isa_infeccao ii 
            ON is2.paciente_id = ii.paciente_id 
                and is2.id_enterprise = ii.id_enterprise
                and date_trunc('day', ii.dt_infeccao) = date_trunc('day', is2.dt_infeccao) 
        where is2.max_prob >= 0.75 AND ii.pred_isc = 1
        group by is2.id_hospital, is2.id_enterprise
        UNION
        SELECT 
            'suspeitas_por_tipo_ISC_media',
            COUNT(DISTINCT is2.paciente_id) FILTER (WHERE is2.dt_infeccao BETWEEN date_trunc('month', current_date - interval '1 month') AND date_trunc('month', current_date))::text,
            COUNT(DISTINCT is2.paciente_id) FILTER (WHERE is2.dt_infeccao BETWEEN date_trunc('month', current_date - interval '3 month') AND date_trunc('month', current_date))::text,
            COUNT(DISTINCT is2.paciente_id) FILTER (WHERE is2.dt_infeccao BETWEEN date_trunc('month', current_date - interval '6 month') AND date_trunc('month', current_date))::text,
            COUNT(DISTINCT is2.paciente_id) FILTER (WHERE is2.dt_infeccao BETWEEN date_trunc('month', current_date - interval '12 month') AND date_trunc('month', current_date))::text,
            COUNT(DISTINCT is2.paciente_id) FILTER (WHERE is2.dt_infeccao BETWEEN date_trunc('month', current_date - interval '120 month') AND date_trunc('month', current_date))::text,
            is2.id_hospital, 
            is2.id_enterprise
        FROM isa_suspeita is2
        JOIN isa_pacientes ip 
            ON is2.paciente_id = ip.id
                and is2.id_enterprise = ip.id_enterprise
        JOIN isa_infeccao ii 
            ON is2.paciente_id = ii.paciente_id 
                and is2.id_enterprise = ii.id_enterprise
                and date_trunc('day', ii.dt_infeccao) = date_trunc('day', is2.dt_infeccao) 
        where is2.max_prob < 0.75 AND is2.max_prob >= 0.5 AND ii.pred_isc = 1
        group by is2.id_hospital, is2.id_enterprise
        UNION
        SELECT 
            'suspeitas_por_tipo_ITU_alta',
            COUNT(DISTINCT is2.paciente_id) FILTER (WHERE is2.dt_infeccao BETWEEN date_trunc('month', current_date - interval '1 month') AND date_trunc('month', current_date))::text,
            COUNT(DISTINCT is2.paciente_id) FILTER (WHERE is2.dt_infeccao BETWEEN date_trunc('month', current_date - interval '3 month') AND date_trunc('month', current_date))::text,
            COUNT(DISTINCT is2.paciente_id) FILTER (WHERE is2.dt_infeccao BETWEEN date_trunc('month', current_date - interval '6 month') AND date_trunc('month', current_date))::text,
            COUNT(DISTINCT is2.paciente_id) FILTER (WHERE is2.dt_infeccao BETWEEN date_trunc('month', current_date - interval '12 month') AND date_trunc('month', current_date))::text,
            COUNT(DISTINCT is2.paciente_id) FILTER (WHERE is2.dt_infeccao BETWEEN date_trunc('month', current_date - interval '120 month') AND date_trunc('month', current_date))::text,
            is2.id_hospital, 
            is2.id_enterprise
        FROM isa_suspeita is2
        JOIN isa_pacientes ip 
            ON is2.paciente_id = ip.id
                and is2.id_enterprise = ip.id_enterprise
        JOIN isa_infeccao ii 
            ON is2.paciente_id = ii.paciente_id 
                and is2.id_enterprise = ii.id_enterprise
                and date_trunc('day', ii.dt_infeccao) = date_trunc('day', is2.dt_infeccao) 
        where is2.max_prob >= 0.75 AND ii.pred_itu = 1
        group by is2.id_hospital, is2.id_enterprise
        UNION
        SELECT 
            'suspeitas_por_tipo_ITU_media',
            COUNT(DISTINCT is2.paciente_id) FILTER (WHERE is2.dt_infeccao BETWEEN date_trunc('month', current_date - interval '1 month') AND date_trunc('month', current_date))::text,
            COUNT(DISTINCT is2.paciente_id) FILTER (WHERE is2.dt_infeccao BETWEEN date_trunc('month', current_date - interval '3 month') AND date_trunc('month', current_date))::text,
            COUNT(DISTINCT is2.paciente_id) FILTER (WHERE is2.dt_infeccao BETWEEN date_trunc('month', current_date - interval '6 month') AND date_trunc('month', current_date))::text,
            COUNT(DISTINCT is2.paciente_id) FILTER (WHERE is2.dt_infeccao BETWEEN date_trunc('month', current_date - interval '12 month') AND date_trunc('month', current_date))::text,
            COUNT(DISTINCT is2.paciente_id) FILTER (WHERE is2.dt_infeccao BETWEEN date_trunc('month', current_date - interval '120 month') AND date_trunc('month', current_date))::text,
            is2.id_hospital, 
            is2.id_enterprise
        FROM isa_suspeita is2
        JOIN isa_pacientes ip 
            ON is2.paciente_id = ip.id
                and is2.id_enterprise = ip.id_enterprise
        JOIN isa_infeccao ii 
            ON is2.paciente_id = ii.paciente_id 
                and is2.id_enterprise = ii.id_enterprise
                and date_trunc('day', ii.dt_infeccao) = date_trunc('day', is2.dt_infeccao) 
        where is2.max_prob < 0.75 AND is2.max_prob >= 0.5 AND ii.pred_itu = 1
        group by is2.id_hospital, is2.id_enterprise
        UNION
        SELECT 
            'suspeitas_por_tipo_PAV_alta',
            COUNT(DISTINCT is2.paciente_id) FILTER (WHERE is2.dt_infeccao BETWEEN date_trunc('month', current_date - interval '1 month') AND date_trunc('month', current_date))::text,
            COUNT(DISTINCT is2.paciente_id) FILTER (WHERE is2.dt_infeccao BETWEEN date_trunc('month', current_date - interval '3 month') AND date_trunc('month', current_date))::text,
            COUNT(DISTINCT is2.paciente_id) FILTER (WHERE is2.dt_infeccao BETWEEN date_trunc('month', current_date - interval '6 month') AND date_trunc('month', current_date))::text,
            COUNT(DISTINCT is2.paciente_id) FILTER (WHERE is2.dt_infeccao BETWEEN date_trunc('month', current_date - interval '12 month') AND date_trunc('month', current_date))::text,
            COUNT(DISTINCT is2.paciente_id) FILTER (WHERE is2.dt_infeccao BETWEEN date_trunc('month', current_date - interval '120 month') AND date_trunc('month', current_date))::text,
            is2.id_hospital, 
            is2.id_enterprise
        FROM isa_suspeita is2
        JOIN isa_pacientes ip 
            ON is2.paciente_id = ip.id
                and is2.id_enterprise = ip.id_enterprise
        JOIN isa_infeccao ii 
            ON is2.paciente_id = ii.paciente_id 
                and is2.id_enterprise = ii.id_enterprise
                and date_trunc('day', ii.dt_infeccao) = date_trunc('day', is2.dt_infeccao) 
        where is2.max_prob >= 0.75 AND ii.pred_pav = 1
        group by is2.id_hospital, is2.id_enterprise
        UNION
        SELECT 
            'suspeitas_por_tipo_PAV_media',
            COUNT(DISTINCT is2.paciente_id) FILTER (WHERE is2.dt_infeccao BETWEEN date_trunc('month', current_date - interval '1 month') AND date_trunc('month', current_date))::text,
            COUNT(DISTINCT is2.paciente_id) FILTER (WHERE is2.dt_infeccao BETWEEN date_trunc('month', current_date - interval '3 month') AND date_trunc('month', current_date))::text,
            COUNT(DISTINCT is2.paciente_id) FILTER (WHERE is2.dt_infeccao BETWEEN date_trunc('month', current_date - interval '6 month') AND date_trunc('month', current_date))::text,
            COUNT(DISTINCT is2.paciente_id) FILTER (WHERE is2.dt_infeccao BETWEEN date_trunc('month', current_date - interval '12 month') AND date_trunc('month', current_date))::text,
            COUNT(DISTINCT is2.paciente_id) FILTER (WHERE is2.dt_infeccao BETWEEN date_trunc('month', current_date - interval '120 month') AND date_trunc('month', current_date))::text,
            is2.id_hospital, 
            is2.id_enterprise
        FROM isa_suspeita is2
        JOIN isa_pacientes ip 
            ON is2.paciente_id = ip.id
                and is2.id_enterprise = ip.id_enterprise
        JOIN isa_infeccao ii 
            ON is2.paciente_id = ii.paciente_id 
                and is2.id_enterprise = ii.id_enterprise
                and date_trunc('day', ii.dt_infeccao) = date_trunc('day', is2.dt_infeccao) 
        where is2.max_prob < 0.75 AND is2.max_prob >= 0.5 AND ii.pred_pav = 1
        group by is2.id_hospital, is2.id_enterprise
        UNION
        SELECT 
            'suspeitas_por_tipo_PNM_alta',
            COUNT(DISTINCT is2.paciente_id) FILTER (WHERE is2.dt_infeccao BETWEEN date_trunc('month', current_date - interval '1 month') AND date_trunc('month', current_date))::text,
            COUNT(DISTINCT is2.paciente_id) FILTER (WHERE is2.dt_infeccao BETWEEN date_trunc('month', current_date - interval '3 month') AND date_trunc('month', current_date))::text,
            COUNT(DISTINCT is2.paciente_id) FILTER (WHERE is2.dt_infeccao BETWEEN date_trunc('month', current_date - interval '6 month') AND date_trunc('month', current_date))::text,
            COUNT(DISTINCT is2.paciente_id) FILTER (WHERE is2.dt_infeccao BETWEEN date_trunc('month', current_date - interval '12 month') AND date_trunc('month', current_date))::text,
            COUNT(DISTINCT is2.paciente_id) FILTER (WHERE is2.dt_infeccao BETWEEN date_trunc('month', current_date - interval '120 month') AND date_trunc('month', current_date))::text,
            is2.id_hospital, 
            is2.id_enterprise
        FROM isa_suspeita is2
        JOIN isa_pacientes ip 
            ON is2.paciente_id = ip.id
                and is2.id_enterprise = ip.id_enterprise
        JOIN isa_infeccao ii 
            ON is2.paciente_id = ii.paciente_id 
                and is2.id_enterprise = ii.id_enterprise
                and date_trunc('day', ii.dt_infeccao) = date_trunc('day', is2.dt_infeccao) 
        where is2.max_prob >= 0.75 AND ii.pred_pnm = 1
        group by is2.id_hospital, is2.id_enterprise
        UNION
        SELECT 
            'suspeitas_por_tipo_PNM_media',
            COUNT(DISTINCT is2.paciente_id) FILTER (WHERE is2.dt_infeccao BETWEEN date_trunc('month', current_date - interval '1 month') AND date_trunc('month', current_date))::text,
            COUNT(DISTINCT is2.paciente_id) FILTER (WHERE is2.dt_infeccao BETWEEN date_trunc('month', current_date - interval '3 month') AND date_trunc('month', current_date))::text,
            COUNT(DISTINCT is2.paciente_id) FILTER (WHERE is2.dt_infeccao BETWEEN date_trunc('month', current_date - interval '6 month') AND date_trunc('month', current_date))::text,
            COUNT(DISTINCT is2.paciente_id) FILTER (WHERE is2.dt_infeccao BETWEEN date_trunc('month', current_date - interval '12 month') AND date_trunc('month', current_date))::text,
            COUNT(DISTINCT is2.paciente_id) FILTER (WHERE is2.dt_infeccao BETWEEN date_trunc('month', current_date - interval '120 month') AND date_trunc('month', current_date))::text,
            is2.id_hospital, 
            is2.id_enterprise
        FROM isa_suspeita is2
        JOIN isa_pacientes ip 
            ON is2.paciente_id = ip.id
                and is2.id_enterprise = ip.id_enterprise
        JOIN isa_infeccao ii 
            ON is2.paciente_id = ii.paciente_id 
                and is2.id_enterprise = ii.id_enterprise
                and date_trunc('day', ii.dt_infeccao) = date_trunc('day', is2.dt_infeccao) 
        where is2.max_prob < 0.75 AND is2.max_prob >= 0.5 AND ii.pred_pnm = 1
        group by is2.id_hospital, is2.id_enterprise
        UNION
        SELECT 
            'suspeitas_por_tipo_TRAQUEO_alta',
            COUNT(DISTINCT is2.paciente_id) FILTER (WHERE is2.dt_infeccao BETWEEN date_trunc('month', current_date - interval '1 month') AND date_trunc('month', current_date))::text,
            COUNT(DISTINCT is2.paciente_id) FILTER (WHERE is2.dt_infeccao BETWEEN date_trunc('month', current_date - interval '3 month') AND date_trunc('month', current_date))::text,
            COUNT(DISTINCT is2.paciente_id) FILTER (WHERE is2.dt_infeccao BETWEEN date_trunc('month', current_date - interval '6 month') AND date_trunc('month', current_date))::text,
            COUNT(DISTINCT is2.paciente_id) FILTER (WHERE is2.dt_infeccao BETWEEN date_trunc('month', current_date - interval '12 month') AND date_trunc('month', current_date))::text,
            COUNT(DISTINCT is2.paciente_id) FILTER (WHERE is2.dt_infeccao BETWEEN date_trunc('month', current_date - interval '120 month') AND date_trunc('month', current_date))::text,
            is2.id_hospital, 
            is2.id_enterprise
        FROM isa_suspeita is2
        JOIN isa_pacientes ip 
            ON is2.paciente_id = ip.id
                and is2.id_enterprise = ip.id_enterprise
        JOIN isa_infeccao ii 
            ON is2.paciente_id = ii.paciente_id 
                and is2.id_enterprise = ii.id_enterprise
                and date_trunc('day', ii.dt_infeccao) = date_trunc('day', is2.dt_infeccao) 
        where is2.max_prob >= 0.75 AND ii.pred_traqueo = 1
        group by is2.id_hospital, is2.id_enterprise
        UNION
        SELECT 
            'suspeitas_por_tipo_TRAQUEO_media',
            COUNT(DISTINCT is2.paciente_id) FILTER (WHERE is2.dt_infeccao BETWEEN date_trunc('month', current_date - interval '1 month') AND date_trunc('month', current_date))::text,
            COUNT(DISTINCT is2.paciente_id) FILTER (WHERE is2.dt_infeccao BETWEEN date_trunc('month', current_date - interval '3 month') AND date_trunc('month', current_date))::text,
            COUNT(DISTINCT is2.paciente_id) FILTER (WHERE is2.dt_infeccao BETWEEN date_trunc('month', current_date - interval '6 month') AND date_trunc('month', current_date))::text,
            COUNT(DISTINCT is2.paciente_id) FILTER (WHERE is2.dt_infeccao BETWEEN date_trunc('month', current_date - interval '12 month') AND date_trunc('month', current_date))::text,
            COUNT(DISTINCT is2.paciente_id) FILTER (WHERE is2.dt_infeccao BETWEEN date_trunc('month', current_date - interval '120 month') AND date_trunc('month', current_date))::text,
            is2.id_hospital, 
            is2.id_enterprise
        FROM isa_suspeita is2
        JOIN isa_pacientes ip 
            ON is2.paciente_id = ip.id
                and is2.id_enterprise = ip.id_enterprise
        JOIN isa_infeccao ii 
            ON is2.paciente_id = ii.paciente_id 
                and is2.id_enterprise = ii.id_enterprise
                and date_trunc('day', ii.dt_infeccao) = date_trunc('day', is2.dt_infeccao) 
        where is2.max_prob < 0.75 AND is2.max_prob >= 0.5 AND ii.pred_traqueo = 1
        group by is2.id_hospital, is2.id_enterprise
    """
    c = dataRequest.get_data(queryText= query_formated, chunck= None)
    if pos == 0:
        dataRequest.set_data_on_sql(df= c, nomeTabelaDestino= "isa_relatorio", isLocal=  False, if_exists= "replace")
        pos += 1
    else:
        dataRequest.set_data_on_sql(df= c, nomeTabelaDestino= "isa_relatorio", isLocal=  False, if_exists= "append")
    

if __name__ == "__main__":
    main()