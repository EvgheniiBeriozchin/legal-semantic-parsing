from crypt import methods
import logging 

from flask import Flask, request
from db import db
from bson import ObjectId

app = Flask(__name__)


@app.route("/get_collections")
def get_collections():
    return {"collections" : [{"name": name} for name in db.list_collection_names()]}

@app.route("/get_collection_items/<collection_name>")
def get_collection_items(collection_name):
    items = [item for item in list(db[collection_name].find()) if "logical_form" not in item]
    for item in items:
        item["_id"] = str(item["_id"])

    return {"collectionItems" : items}

@app.route("/set_item_logical_form", methods = ['POST'])
def set_item_logical_form():
    collection_name = request.json["collectionName"]
    item_id = request.json["itemId"]
    logical_form = request.json["logicalForm"]

    db[collection_name].update_one(
    {
    '_id': ObjectId(item_id)
    },
    {
        '$set': {
        'logical_form': logical_form
        }
    }, upsert=False)

    return "Updated"

if __name__=='__main__':
    app.run(debug=True)