import random
import names
import json
from db import db
from wikidata_queries import WikidataQueries
from utils import random_names


def generate_data(wikidata_courts):
    courts = wikidata_courts
    medium_sentences = []
    random_courts = courts + (["court"] * int(len(courts) * 0.05))
    for dec in ["accepted", "refused", "dismissed", "allowed"]:
        for app in ["applications", "inquiries"]:
            for co in ["all", "none", "two", "three", "four"]:
                min_num = 3 if co == "two" else (4 if co == "three" else (5 if co == "four" else 2))
                for i in range(min_num, 6):
                    num = 5
                    for _ in range(num):
                        all_names = random_names(i)
                        court = random.choice(random_courts)
                        medium_sentences.append({
                            "text" : "The {court} received {app} by {names} and {dec} {co} of them".format(app=app, co=co, dec=dec, court=court, names=all_names),
                            })
    return medium_sentences


if __name__=="__main__":
    wikidata = WikidataQueries()
    wikidata_courts = wikidata.get_courts()
    data = generate_data(wikidata_courts)
    with open("s00004_sample.json", "w") as f:
        sampled_data = []
        sampled_data = random.choices(data, k=25)
        json.dump(sampled_data, f)

    col = db["s00004"]
    col.insert_many(data)