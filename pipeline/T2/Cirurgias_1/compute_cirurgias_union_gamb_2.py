import pandas as pd
from ImpararePackage import dataRequest
from ImpararePackage import maestro
from multiprocessing import Pool, cpu_count, freeze_support

def main():
    dataRequest.execute("""
        SET synchronous_commit = off;
        
        DROP TABLE IF EXISTS imparare2_cirurgias_union_gamb;
        
        CREATE UNLOGGED TABLE imparare2_cirurgias_union_gamb AS
            select
				proc.patient_id::int as patient_id, 
				proc.id_atendimento::int as id_atendimento, 
				min(proc.dthr_procedimento) as dthr_procedimento,
				max(proc.dthr_fim_procedimento) as dthr_fim_procedimento,
				string_agg(proc.nome_medico, ', ') as nome_medico,
				COALESCE(ROUND((EXTRACT(EPOCH FROM (MAX(proc.dthr_fim_procedimento) - min(proc.dthr_procedimento))) / 60.0)::numeric, 2), 0)::int as tempo_de_cirurgia,
				coalesce(note.texto_cirurgia, 'Descrição não informada') as texto_cirurgia,
				string_agg(proc.nome_procedimento, ', ') as nome_procedimento,
				count(distinct proc.nome_procedimento)::smallint,
                max(proc.surgery_infection_risky)::smallint as surgery_infection_risky,
				proc.id_enterprise::smallint as id_enterprise
			from imparare2_t1_cirurgias_3_3 as proc
			left join imparare2_t1_cirurgias_4_4 as note
			on proc.patient_id = note.patient_id
				and proc.id_atendimento = note.id_atendimento
				and proc.id_enterprise = note.id_enterprise
				and (
					proc.dthr_procedimento between note.dthr_criacao - interval '4 hours' and note.dthr_criacao + interval '4 hours'
					or 
					proc.dthr_fim_procedimento between note.dthr_criacao - interval '4 hours' and note.dthr_criacao + interval '4 hours'
				)
			group by proc.patient_id, proc.id_atendimento, coalesce(note.texto_cirurgia, 'Descrição não informada'), proc.dt_procedimento, proc.id_enterprise;
    """)

if __name__ == "__main__":
    from multiprocessing import freeze_support
    freeze_support()
    main()