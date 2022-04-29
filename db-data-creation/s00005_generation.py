import random
import names
import json
from db import db
from wikidata_queries import WikidataQueries
from utils import random_names_partition


def generate_data(wikidata_courts):
    courts = wikidata_courts
    hard_sentences = []
    random_courts = courts + (["court"] * int(len(courts) * 0.05))
    for dec in ["accepted", "allowed", "refused", "dismissed"]:
        while_l = ["accepting", "allowing"] if dec in ["refused", "dismissed"] else ["refusing", "dismissing"]
        for while_v in while_l:
            for app in ["applications", "inquiries"]:
                for i in range(2, 6):
                    num = 5 * i
                    for _ in range(num):
                        all_names, first, second = random_names_partition(i, partition=random.choice(range(1, i)), partition_by_name=random.choice([True, False]))
                        second = random.choices([second, "rest"], weights=[0.95, 0.05])[0]
                        court = random.choice(random_courts)
                        hard_sentences.append({
                            "text" : "The {court} received {app} by {names} and {dec} the {g1}, while {while_v} the {g2}".format(app=app, while_v=while_v, dec=dec, court=court, names=all_names, g1=first, g2=second),
                            })
                                
    return hard_sentences


if __name__=="__main__":
    wikidata = WikidataQueries()
    wikidata_courts = wikidata.get_courts()
    data = generate_data(wikidata_courts)
    with open("s00005_sample.json", "w") as f:
        sampled_data = []
        sampled_data = random.choices(data, k=25)
        json.dump(sampled_data, f)

    col = db["s00005"]
    col.insert_many(data)