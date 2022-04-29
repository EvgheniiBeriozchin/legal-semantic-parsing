from SPARQLWrapper import SPARQLWrapper, JSON
import pandas as pd

ADDRESS = "http://www.wikidata.org/entity/{}"


class WikidataQueries:


    def __init__(self) -> None:
        self.sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
        self.sparql.setReturnFormat(JSON)

    def get_courts(self) -> [str]:
        self.sparql.setQuery(
            """
            SELECT ?item ?itemLabel
            WHERE
            {
                ?item wdt:P31 wd:Q41487.
                SERVICE wikibase:label { bd:serviceParam wikibase:language "en" }
            }
            """
        )

        results = self.sparql.query().convert()
        results_df = pd.io.json.json_normalize(results['results']['bindings'])
        
        courts = []
        for row in results_df[['item.value', 'itemLabel.value']].iterrows():
            if ADDRESS.format(row[1][1]) == row[1][0]:
                continue
            courts.append(row[1][1])

        return courts

    
    def get_courts_with_regions(self) -> pd.DataFrame:
        self.sparql.setQuery(
            """
            SELECT ?item ?itemLabel ?country ?countryLabel ?region ?regionLabel
            WHERE
            {
                ?item wdt:P31 wd:Q41487.
                ?item wdt:P131 ?region.
                ?item wdt:P17 ?country.
                SERVICE wikibase:label { bd:serviceParam wikibase:language "en" }
            }
            """
        )
        results = self.sparql.query().convert()

        results_df = pd.io.json.json_normalize(results['results']['bindings'])

        return results_df[['item.value', 'itemLabel.value', 'country.value', 'countryLabel.value', 'region.value', 'regionLabel.value']]