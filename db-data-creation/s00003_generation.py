import random
import names
import json
from db import db
from wikidata_queries import WikidataQueries


def generate_data(wikidata_courts):
    courts = wikidata_courts
    simple_sentences = []
    for dec in ["accepted", "refused", "quashed", "dismissed", "allowed"]:
        for app in ["application", "appeal", "inquiry"]:
            r_courts = ["by the " + c for c in random.sample(courts, k=3)]
            for court in ["", " by the court"] + r_courts:
                i = 10
                for _ in range(i):
                    last_name = random.choice(["Mr.", "Mrs."]) + " " + names.get_last_name()
                    full_name = names.get_full_name()
                    if random.choice(["Mr.", "Mrs."]) == "Mr.":
                        polite_full_name = "Mr. " + names.get_full_name(gender='male')
                    else:
                        polite_full_name = "Mrs. " + names.get_full_name(gender='female')

                    simple_sentences.append({
                        "text" : "The {app} by {name} was {dec}{court}.".format(app=app, name=last_name, dec=dec, court=court),
                        "logical_form" : app.capitalize() + "(\\a)^Author(\\a, {name})" + "^Court(\\b)^CourtName(\\b, {court})^" + dec[:-2].capitalize() + "(\\c)" + "^{dec}Subject(\\c, \\b)" + "^{dec}Object(\\c, \\a)".format(name=last_name, court=court, dec=dec.capitalize())
                    })
                    simple_sentences.append({
                        "text" : "The {app} by {name} was {dec}{court}.".format(app=app, name=full_name, dec=dec, court=court),
                        "logical_form" : app.capitalize() + "(\\a)^Author(\\a, {name})" + "^Court(\\b)^CourtName(\\b, {court})^" + dec[:-2].capitalize() + "(\\c)" + "^{dec}Subject(\\c, \\b)" + "^{dec}Object(\\c, \\a)".format(name=full_name, court=court, dec=dec.capitalize())
                    })
                    simple_sentences.append({
                        "text" : "The {app} by {name} was {dec}{court}.".format(app=app, name=polite_full_name, dec=dec, court=court),
                        "logical_form" : (app.capitalize() + "(\\a)^Author(\\a, {name})" + "^Court(\\b)^CourtName(\\b, {court})^" + dec[:-2].capitalize() + "(\\c)" + "^{dec}Subject(\\c, \\b)" + "^{dec}Object(\\c, \\a)").format(name=polite_full_name, court=court, dec=dec.capitalize())
                    })

    return simple_sentences


if __name__=="__main__":
    wikidata = WikidataQueries()
    wikidata_courts = wikidata.get_courts()
    data = generate_data(wikidata_courts)
    with open("s00003_sample.json", "w") as f:
        sampled_data = []
        sampled_data = random.choices(data, k=25)
        json.dump(sampled_data, f)

    col = db["s00003"]
    col.insert_many(data)