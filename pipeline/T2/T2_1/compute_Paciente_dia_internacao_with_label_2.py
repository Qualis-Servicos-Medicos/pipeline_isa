from ImpararePackage import dataRequest

def main():
    dataRequest.execute('DROP TABLE IF EXISTS "imparare2_paciente_dia_internacao_with_label_nova"')
    dataRequest.execute("""
        SET synchronous_commit = off;
        CREATE UNLOGGED TABLE imparare2_paciente_dia_internacao_with_label_nova AS
        with last_and_next_int as (
            select 
                int.id_enterprise, 
                int.cd_atendimento,
                max(int2.cd_atendimento) previous_cd_antedimento,
                min(int3.cd_atendimento) next_cd_atendimento
            from imparare2_internacoes_v2_stacked_by_cd_atendimento int
            left join imparare2_internacoes_v2_stacked_by_cd_atendimento int2
                on int.registro = int2.registro
                    and int.id_enterprise = int2.id_enterprise
                    and int2.cd_atendimento < int.cd_atendimento
            left join imparare2_internacoes_v2_stacked_by_cd_atendimento int3
                on int.registro = int3.registro
                    and int.id_enterprise = int3.id_enterprise
                    and int3.cd_atendimento > int.cd_atendimento
            group by int.registro, int.id_enterprise, int.cd_atendimento
        )
        select distinct 
            int.registro, 
            pac.sexo::text, 
            pac.dt_nascimento_parsed::date,
            EXTRACT(YEAR FROM AGE(date(dd), pac.dt_nascimento_parsed)) AS idade_anos,
            (date(dd) - pac.dt_nascimento_parsed::date) AS idade_dias,
            dd::date as dia,
            int.dthr_atendimento, 
            int.nmconvenio, 
            int.unidade, 
            int.tipo_intern,
            int.dthr_alta, 
            COALESCE(int.alta, 'AINDA INTERNADO') as alta,
            int.los,
            int2.los as los_on_previous_hospitalization,
            int.dthr_atendimento::date - int2.dthr_alta::date as days_since_previous_hospitalizations,
            int3.los as los_on_next_hospitalization,
            int3.dthr_atendimento::date - int.dthr_alta::date as days_to_next_hospitalizations,
            pac.id_enterprise
        from generate_series('2020-01-01' , (date_trunc('day', (NOW() + interval '1 day'))::date), '1 day'::interval) dd, 
            imparare2_pacientes_prepared pac 
        inner join imparare2_internacoes_v2_stacked_by_cd_atendimento int
            on pac.registro = int.registro
                AND pac.id_enterprise = int.id_enterprise
        left join last_and_next_int
            on last_and_next_int.cd_atendimento = int.cd_atendimento
                and last_and_next_int.id_enterprise = int.id_enterprise
        left join imparare2_internacoes_v2_stacked_by_cd_atendimento int2 
            on last_and_next_int.previous_cd_antedimento = int2.cd_atendimento
                and last_and_next_int.id_enterprise = int2.id_enterprise
        left join imparare2_internacoes_v2_stacked_by_cd_atendimento int3
            on last_and_next_int.next_cd_atendimento = int3.cd_atendimento
                and last_and_next_int.id_enterprise = int3.id_enterprise
        where date(dd) BETWEEN date(int.dthr_atendimento) and date(int.dthr_alta)
    """)

if __name__ == "__main__":
    main()