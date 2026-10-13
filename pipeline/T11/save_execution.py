from ImpararePackage import dataRequest

def main():
    dataRequest.execute("INSERT INTO pipeline_execution_log (execution_date) VALUES (CURRENT_DATE);")

if __name__ == "__main__":
    main()