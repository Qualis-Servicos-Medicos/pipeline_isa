from ImpararePackage import dataRequest
from ImpararePackage import maestro
import pandas as pd
from typing import Any

def main():
    query = """
        SELECT DISTINCT ON (isa_suspeita.id)
            isa_suspeita.id,
            isa_suspeita.paciente_id::text,
            nome,
            isa_suspeita.dt_infeccao,
            isa_suspeita.prob_perc,
            isa_suspeita.max_prob,
            (
                CASE
                    WHEN isa_suspeita.max_prob >= 0.5
                    AND isa_suspeita.max_prob < 0.7 THEN 'MEDIA'
                    ELSE (
                        CASE
                            WHEN isa_suspeita.max_prob >= 0.7 THEN 'ALTA'
                            ELSE 'BAIXA'
                        END
                    )
                END
            ) as prob_grupo_isa,
            criterio,
            dt_inicio,
            dt_fim,
            pred_pnm, -- Se 0 não mostra na interface se 1 mostra
            prob_perc_pnm as pnm,
            pred_traqueo,
            prob_perc_traqueo as traqueo,
            pred_pav,
            prob_perc_pav as pav,
            pred_itu,
            prob_perc_itu as itu,
            pred_isc,
            prob_perc_isc as isc,
            pred_ipcs,
            prob_perc_ipcs as ipcs,
            pred_comunitaria,
            prob_perc_comunitaria AS comunitaria,
            pred_iras,
            prob_perc_iras AS iras
        FROM isa_suspeita
        LEFT JOIN isa_pacientes 
            ON isa_suspeita.paciente_id = isa_pacientes.id
        LEFT JOIN isa_infeccao 
            ON isa_suspeita.paciente_id = isa_infeccao.paciente_id
            AND isa_suspeita.dt_infeccao = isa_infeccao.dt_infeccao
        ORDER BY isa_suspeita.id, isa_suspeita.dt_infeccao DESC
    """
    df = dataRequest.get_data(queryText= query)
    
    client = dataRequest.ELASTICSEARCH_CONNECTION
    print(client.cluster.health())
    print(client.ping())

    index_name = "suspeitas"
    
    client.options(ignore_status=[400, 404]).indices.delete(index=index_name)
    
    if not client.indices.exists(index=index_name):
        print("Criando index", index_name)
        client.indices.create(
            index=index_name,
            settings={
                "index": {
                    "max_result_window": 100000,
                    "number_of_shards": 1,
                    "number_of_replicas": 0,
                    "refresh_interval": "30s",
                    "translog": {
                        "durability": "async",
                        "sync_interval": "30s"
                    }
                }
            },
            mappings={
                # front busca "suspeitas" por paciente_id (term); demais campos so sao retornados
                "dynamic": "strict",
                "properties": {
                    "id": {"type": "keyword", "index": False, "doc_values": False},
                    "paciente_id": {"type": "integer"},
                    "nome": {"type": "text", "index": False},
                    "dt_infeccao": {"type": "date", "index": False, "doc_values": False},
                    "prob_perc": {"type": "float", "index": False, "doc_values": False},
                    "max_prob": {"type": "float", "index": False, "doc_values": False},
                    "prob_grupo_isa": {"type": "keyword", "index": False, "doc_values": False},
                    "criterio": {"type": "keyword", "index": False, "doc_values": False},
                    "dt_inicio": {"type": "date", "index": False, "doc_values": False},
                    "dt_fim": {"type": "date", "index": False, "doc_values": False},
                    "pred_pnm": {"type": "integer", "index": False, "doc_values": False},
                    "pnm": {"type": "float", "index": False, "doc_values": False},
                    "pred_traqueo": {"type": "integer", "index": False, "doc_values": False},
                    "traqueo": {"type": "float", "index": False, "doc_values": False},
                    "pred_pav": {"type": "integer", "index": False, "doc_values": False},
                    "pav": {"type": "float", "index": False, "doc_values": False},
                    "pred_itu": {"type": "integer", "index": False, "doc_values": False},
                    "itu": {"type": "float", "index": False, "doc_values": False},
                    "pred_isc": {"type": "integer", "index": False, "doc_values": False},
                    "isc": {"type": "float", "index": False, "doc_values": False},
                    "pred_ipcs": {"type": "integer", "index": False, "doc_values": False},
                    "ipcs": {"type": "float", "index": False, "doc_values": False},
                    "pred_comunitaria": {"type": "integer", "index": False, "doc_values": False},
                    "comunitaria": {"type": "float", "index": False, "doc_values": False},
                    "pred_iras": {"type": "integer", "index": False, "doc_values": False},
                    "iras": {"type": "float", "index": False, "doc_values": False},
                }
            }
        )
        maestro.wait_for_index_health(client, index_name)

    total_success = 0
    total_failed = 0

    for chunk in df:
        actions = maestro.generate_actions(chunk, index_name)
        success, failed = maestro.bulk_upload_with_retry(client, actions, context=index_name, thread_count=4)
        total_success += success
        total_failed += failed

    print(f"\n✅ {index_name} Indexados com sucesso: {total_success}")
    print(f"❌ {index_name} Falhas: {total_failed}")

if __name__ == "__main__":
    main()