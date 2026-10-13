from ImpararePackage import dataRequest
from ImpararePackage import maestro

def main():
    query = """
        SELECT
            id,
            unidades,
            id_hospital,
            id_enterprise
        FROM isa_unidades;
    """
    df = dataRequest.get_data(queryText= query, isLocal= False)
    
    client = dataRequest.ELASTICSEARCH_CONNECTION
    print(client.cluster.health())
    print(client.ping())

    index_name = maestro.getELKIndexValue("unidades")

    client.options(ignore_status=[400, 404]).indices.delete(index=index_name)
    
    if not client.indices.exists(index=index_name):
        print("Criando index", index_name)
        client.indices.create(
            index=index_name,
            settings={"index": {"max_result_window": 100000}}
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