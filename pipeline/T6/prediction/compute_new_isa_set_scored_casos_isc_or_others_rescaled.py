from ImpararePackage import dataRequest

def main():
    query = """
        DROP TABLE IF EXISTS imparare2_new_isa_set_scored_casos_isc_or_others_rescaled;
        SET synchronous_commit = off;
        CREATE UNLOGGED TABLE imparare2_new_isa_set_scored_casos_isc_or_others_rescaled AS
            with max_iras_prob as (
                SELECT 
                    MAX(proba_1)::decimal as max_prob_perc_iras
                FROM imparare2_new_isa_set_scored_casos_isc_or_others
            )
            SELECT 
                prontuario, 
                dia, 
                id_enterprise,
                proba_1, 
                prediction,
                CEILING(proba_1::decimal * 1000.0/(select max_prob_perc_iras from max_iras_prob))/1000.0 AS rescaled_proba_1
            FROM imparare2_new_isa_set_scored_casos_isc_or_others;
    """
    dataRequest.execute(queryText= query)

if __name__ == "__main__":
    main()