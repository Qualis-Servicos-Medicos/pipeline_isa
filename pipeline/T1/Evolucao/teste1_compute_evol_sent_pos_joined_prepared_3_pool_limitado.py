from ImpararePackage import dataRequest
from multiprocessing import Pool, cpu_count
from worker_compute_evol_sent_pos_joined_prepared_3 import main as worker
import os
import time

# Teste 1: mesma execução de compute_evol_sent_pos_joined_prepared_3.py (mesmo worker, mesma
# tabela de saída), mas sem tomar todos os núcleos do servidor -- o Postgres roda no mesmo host
# e é ele quem recebe os inserts desses workers.
#   ISA_WORKERS -> quantidade de processos (padrão: cpu_count() - 4, mínimo 1)
#   ISA_NICE    -> incremento de nice em cada worker (padrão: 10; 0 desliga). Com nice alto o SO
#                  dá preferência ao Postgres e aos outros jobs, e o script fica com a CPU que sobra.
WORKERS = int(os.environ.get("ISA_WORKERS", max(1, cpu_count() - 4)))
NICE = int(os.environ.get("ISA_NICE", 10))


def _baixar_prioridade():
    if NICE:
        os.nice(NICE)


def main():
    replace = True

    if replace:
        dataRequest.execute("DROP TABLE IF EXISTS imparare2_evol_sent_pos_joined_prepared;")
        create_query = """
            CREATE UNLOGGED TABLE imparare2_evol_sent_pos_joined_prepared (
                registro int8 NULL,
                dthr_evolucao DATE NULL,
                dthr_evolucao_hr timestamp NULL,
                texto_evolucao text NULL,
                termos_achados text NULL,
                perfil_termos text NULL,
                id_enterprise int4 NULL
            );
        """
        dataRequest.execute(create_query)

    append_query = """
        SELECT
            registro,
            perfil,
            dthr_evolucao::date as dthr_evolucao,
            dthr_evolucao as dthr_evolucao_hr,
            sentence_original as texto_evolucao,
            new_sentence,
            id_enterprise
        FROM imparare2_evolucao_anon_data_trunc
        ORDER BY registro, id_enterprise, new_sentence, dthr_evolucao
    """
    df_iterator = dataRequest.get_data(queryText= append_query, chunck= 2000)

    print(f"workers: {WORKERS} de {cpu_count()} núcleos | nice: +{NICE}")
    inicio = time.perf_counter()
    chunks = 0

    with Pool(processes= WORKERS, initializer= _baixar_prioridade) as pool:
        for _ in pool.imap_unordered(worker, df_iterator):
            chunks += 1

    print(f"{chunks} chunks em {time.perf_counter() - inicio:.1f}s")

if __name__ == "__main__":
    main()
