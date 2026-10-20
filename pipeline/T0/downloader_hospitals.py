from ImpararePackage import dataRequest

def main():
    """Esse script baixa 10 linhas não tem porque paralelizar"""
    print("Iniciando downloader_hospitals")
    query_dowloader = "select * FROM hospital"

    df = dataRequest.get_data(queryText= query_dowloader, isWellheadEngine=True, chunck= None)
    
    dataRequest.set_data_on_sql(df= df, nomeTabelaDestino= "hospitals", if_exists= "replace")

    dataRequest.execute("CREATE INDEX IF NOT EXISTS hospitals_id_hospital_idx ON hospitals(id_hospital, id_enterprise);")
    
    print(f"Baixado no total: {len(df)} linhas em hospitals - downloader_hospitals")
    
if __name__ == "__main__":
    main()