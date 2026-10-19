from ImpararePackage import dataRequest
def main():


    dataRequest.execute('CREATE INDEX IF NOT EXISTS suspeita_paciente_idx on "isa_suspeita"(id);', isLocal=  False)
    dataRequest.execute('CREATE INDEX IF NOT EXISTS suspeita_paciente_idx2 on "isa_suspeita"(paciente_id);', isLocal=  False)
    dataRequest.execute('CREATE INDEX IF NOT EXISTS suspeita_paciente_idx3 on "isa_suspeita"(dt_infeccao);', isLocal=  False)
    dataRequest.execute('CREATE INDEX IF NOT EXISTS suspeita_paciente_idx4 on "isa_suspeita"(prob_perc);', isLocal=  False)
    dataRequest.execute('CREATE INDEX IF NOT EXISTS suspeita_paciente_idx5 on "isa_suspeita"(max_prob);', isLocal=  False)

    dataRequest.execute('CREATE INDEX IF NOT EXISTS paciente_idx on "isa_pacientes"(id);', isLocal=  False)
    dataRequest.execute('CREATE INDEX IF NOT EXISTS paciente_idx2 on "isa_pacientes"("nome");', isLocal=  False)

    dataRequest.execute('CREATE INDEX IF NOT EXISTS infeccao_idx on "isa_infeccao"(id);', isLocal=  False)
    dataRequest.execute('CREATE INDEX IF NOT EXISTS infeccao_idx2 on "isa_infeccao"(paciente_id);', isLocal=  False)
    dataRequest.execute('CREATE INDEX IF NOT EXISTS infeccao_idx3 on "isa_infeccao"(dt_infeccao);', isLocal=  False)
    dataRequest.execute('CREATE INDEX IF NOT EXISTS infeccao_idx4 on "isa_infeccao"(prob_perc);', isLocal=  False)

    # dataRequest.execute('CREATE INDEX IF NOT EXISTS avaliacao_idx on "isa_avaliacao"(paciente_id);', isLocal= False)
    # dataRequest.execute('CREATE INDEX IF NOT EXISTS avaliacao_idx2 on "isa_avaliacao"(dt_infeccao);', isLocal= False)

    # dataRequest.execute('CREATE INDEX IF NOT EXISTS suspeita_perc_idx on "isa_suspeita_perc"(paciente_id);', isLocal=  False)
    # dataRequest.execute('CREATE INDEX IF NOT EXISTS suspeita_perc_idx2 on "isa_suspeita_perc"(dt_infeccao);', isLocal=  False)
    # dataRequest.execute(' CREATE INDEX IF NOT EXISTS suspeita_perc_idx3 on "isa_suspeita_perc"(max_prob);', isLocal=  False)

if __name__ == "__main__":
    main()