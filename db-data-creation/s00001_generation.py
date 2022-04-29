from wikidata_queries import WikidataQueries
from db import db

import pandas as pd
import json

ADDRESS = "http://www.wikidata.org/entity/{}"
COUNT_PER_SENTENCE_TYPE = 63
SAMPLE_SIZE_PER_SENTENCE_TPYE = 5
sentences = ["The {ct} is located in {co}.", "The {ct} is in {co}.", "The {ct} sits in {co}.", "The location of the {ct} is {co}", "The location of the {ct} is in {co}"]
    


def generate_data(wikidata_info: pd.DataFrame):
    i = 0
    data = []
    for row in wikidata_info.iterrows():
        if i == COUNT_PER_SENTENCE_TYPE * len(sentences):
            break
        if ADDRESS.format(row[1][1]) == row[1][0] or ADDRESS.format(row[1][3]) == row[1][2]:
            continue
        data.append({
            "text" : sentences[i // COUNT_PER_SENTENCE_TYPE].format(ct=row[1][1], co=row[1][3]),
            "logical_form" : "Court(\\a)^CourtName(\\a, {ct})^Country(\\a, {co})".format(ct=row[1][1], co=row[1][3])
        })
        i += 1

    return data


if __name__=="__main__":
    wikidata = WikidataQueries()
    wikidata_info = wikidata.get_courts_with_regions()
    data = generate_data(wikidata_info)
    with open("s00001_sample.json", "w") as f:
        sampled_data = []
        for i in range(len(sentences)):
            sampled_data += data[i * COUNT_PER_SENTENCE_TYPE : (i * COUNT_PER_SENTENCE_TYPE + SAMPLE_SIZE_PER_SENTENCE_TPYE)]
        json.dump(sampled_data, f)

    col = db["s00001"]
    col.insert_many(data)

