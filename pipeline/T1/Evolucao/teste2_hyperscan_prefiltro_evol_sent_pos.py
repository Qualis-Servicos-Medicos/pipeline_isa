"""
Teste 2: pré-filtro com Hyperscan para o casamento de critérios de
worker_compute_evol_sent_pos_joined_prepared_3.

Só lê do banco, não grava nada. Para cada chunk da amostra roda as duas versões:
  - atual: o findall de cada critério em todas as linhas (como o worker faz hoje);
  - hyperscan: uma varredura por linha com todos os padrões positivos de uma vez, em modo
    prefilter (devolve um superconjunto dos matches, aproximando os lookarounds), e o mesmo
    findall do worker só nos pares (linha, critério) que o Hyperscan sinalizou.
Compara termos_achados e frases linha a linha e mostra o tempo de cada versão.

Requer: pip install hyperscan
Uso:    python teste2_hyperscan_prefiltro_evol_sent_pos.py [n_chunks]   (padrão: 5 chunks de 2000)
"""
import sys
import time

import hyperscan
import pandas as pd

from ImpararePackage import dataRequest
from ImpararePackage import maestro
from worker_compute_evol_sent_pos_joined_prepared_3 import _criterios_compilados, _matches_por_criterio

CHUNK = 2000

# PREFILTER: aceita lookahead/lookbehind trocando-os por construções mais largas (nunca perde match)
# SINGLEMATCH: cada critério é reportado no máximo uma vez por linha -- só interessa se bateu
_HS_FLAGS = hyperscan.HS_FLAG_PREFILTER | hyperscan.HS_FLAG_SINGLEMATCH


def _preparar_new_sentence(c: pd.DataFrame) -> pd.Series:
    """Mesmo pré-processamento de new_sentence do início de worker.main."""
    s = c["new_sentence"].str.encode("ascii", "ignore").str.decode("utf-8")
    return s.apply(lambda x: maestro.split_sentences(str(x) if not isinstance(x, str) else x)).astype(str)


def _acumular(termos, frases, linhas, final_pos, rotulo):
    for i, hits in zip(linhas, final_pos):
        if hits:
            termos[i].append(rotulo)
            frases[i].extend(h.strip("'") for h in hits)


def _casar_atual(serie: pd.Series, criterios) -> tuple[list, list, int]:
    n = len(serie)
    termos = [[] for _ in range(n)]
    frases = [[] for _ in range(n)]
    for rotulo, pattern_pos_re, pos_sanitized, pattern_neg_re, neg_sanitized in criterios:
        final_pos = _matches_por_criterio(serie, pattern_pos_re, pos_sanitized, pattern_neg_re, neg_sanitized)
        _acumular(termos, frases, range(n), final_pos, rotulo)
    return termos, frases, n * len(criterios)


def _compilar_prefiltro(criterios) -> tuple[hyperscan.Database, list[int]]:
    """Compila todos os padrões positivos num único banco Hyperscan (id = índice do critério).
    Critério que o Hyperscan não aceita nem em modo prefilter fica fora do banco e passa pelo
    findall em todas as linhas, exatamente como hoje."""
    ids, sempre_re = [], []
    for k, (rotulo, pattern_pos_re, *_) in enumerate(criterios):
        try:
            hyperscan.Database().compile(expressions=[pattern_pos_re.pattern.encode()], ids=[k], elements=1, flags=[_HS_FLAGS])
            ids.append(k)
        except hyperscan.error as e:
            print(f"  [hyperscan] '{rotulo}' fica fora do pré-filtro: {e}")
            sempre_re.append(k)

    db = hyperscan.Database()
    db.compile(
        expressions=[criterios[k][1].pattern.encode() for k in ids],
        ids=ids,
        elements=len(ids),
        flags=[_HS_FLAGS] * len(ids),
    )
    return db, sempre_re


def _on_match(id_criterio, inicio, fim, flags, achados):
    achados.append(id_criterio)


def _casar_hyperscan(serie: pd.Series, criterios, db, sempre_re) -> tuple[list, list, int]:
    n = len(serie)
    todos = range(len(criterios))

    # 1) uma varredura por linha -> em quais linhas cada critério pode ter batido
    linhas_por_criterio = [[] for _ in criterios]
    for k in sempre_re:
        linhas_por_criterio[k] = list(range(n))
    for i, texto in enumerate(serie.tolist()):
        if not texto.isascii():
            # salvaguarda: o Hyperscan varre bytes e o \w do re é unicode -- fora de ASCII não
            # há garantia de superconjunto, então a linha passa por todos os critérios
            for k in todos:
                if k not in sempre_re:
                    linhas_por_criterio[k].append(i)
            continue
        achados = []
        db.scan(texto.encode(), match_event_handler=_on_match, context=achados)
        for k in achados:
            linhas_por_criterio[k].append(i)

    # 2) o findall do worker só nas linhas sinalizadas; a decisão final continua sendo do re
    termos = [[] for _ in range(n)]
    frases = [[] for _ in range(n)]
    pares = 0
    for k, (rotulo, pattern_pos_re, pos_sanitized, pattern_neg_re, neg_sanitized) in enumerate(criterios):
        linhas = linhas_por_criterio[k]
        if not linhas:
            continue
        pares += len(linhas)
        final_pos = _matches_por_criterio(serie.iloc[linhas], pattern_pos_re, pos_sanitized, pattern_neg_re, neg_sanitized)
        _acumular(termos, frases, linhas, final_pos, rotulo)
    return termos, frases, pares


def main(n_chunks: int) -> None:
    criterios = _criterios_compilados()

    t = time.perf_counter()
    db, sempre_re = _compilar_prefiltro(criterios)
    print(f"critérios: {len(criterios)} | fora do pré-filtro: {len(sempre_re)} | compilação hyperscan: {time.perf_counter() - t:.2f}s")

    # amostra sem ORDER BY para não ordenar a tabela inteira só para o teste
    query = f"""
        SELECT registro, new_sentence
        FROM imparare2_evolucao_anon_data_trunc
        LIMIT {n_chunks * CHUNK}
    """
    tempo_atual = tempo_hs = 0.0
    pares_atual = pares_hs = 0
    linhas_total = divergentes = 0

    for n, c in enumerate(dataRequest.get_data(queryText=query, chunck=CHUNK), start=1):
        serie = _preparar_new_sentence(c)

        t = time.perf_counter()
        termos_a, frases_a, p_a = _casar_atual(serie, criterios)
        tempo_atual += time.perf_counter() - t

        t = time.perf_counter()
        termos_h, frases_h, p_h = _casar_hyperscan(serie, criterios, db, sempre_re)
        tempo_hs += time.perf_counter() - t

        pares_atual += p_a
        pares_hs += p_h
        linhas_total += len(serie)

        registros = c["registro"].tolist()
        for i in range(len(serie)):
            if termos_a[i] != termos_h[i] or frases_a[i] != frases_h[i]:
                divergentes += 1
                if divergentes <= 10:
                    so_atual = sorted(set(termos_a[i]) - set(termos_h[i]))
                    so_hs = sorted(set(termos_h[i]) - set(termos_a[i]))
                    print(f"  DIVERGÊNCIA registro={registros[i]} só no atual={so_atual} só no hyperscan={so_hs}")

        print(f"chunk {n}: atual {tempo_atual:.1f}s | hyperscan {tempo_hs:.1f}s (acumulado)")

    print()
    print(f"linhas comparadas:    {linhas_total}")
    print(f"linhas divergentes:   {divergentes}")
    print(f"pares (linha, critério) avaliados pelo re: atual {pares_atual} | hyperscan {pares_hs} ({pares_hs / max(pares_atual, 1):.1%})")
    print(f"tempo de casamento:   atual {tempo_atual:.1f}s | hyperscan {tempo_hs:.1f}s | ganho {tempo_atual / max(tempo_hs, 1e-9):.1f}x")


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 5)
