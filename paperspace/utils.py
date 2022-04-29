import re
from time import sleep
import torch
import pandas as pd
import pickle
from datasets.arrow_dataset import Dataset
from datasets import concatenate_datasets

GEO_DATAPATH = './m_data/geoqueries880'
SATOH_DATAPATH = './m_data/pair_synset_by_lesk.txt'
MY_DATAPATH = './m_data/echr_labeled_data_v1.0.csv'
SPLIT_DATAPATH = './m_data/data_splits/dataset_split_{}'
SATOH2_DATAPATH = './m_data/artificial.txt'
PATTERN = re.compile('parse\(\[(.*)\], answer\((.*)\)\)\.')


def _format_geodata_x(data):
    return " ".join([word.replace('\'.\'', '.') for word in data])


def _format_geodata_y(data):
    return data
        

def get_geo880_classification():
    with open(GEO_DATAPATH, 'r') as datastream:
        raw_data = datastream.readlines()
    
    x_data = [_format_geodata_x(re.search(PATTERN, datapoint).groups()[0].split(',')) \
              for datapoint in raw_data]
    y_data = [_format_geodata_y(re.search(PATTERN, datapoint).groups()[1]) \
              for datapoint in raw_data]
    
    pre_dataset = {"text": (x_data + y_data), "label": ([1] * len(x_data) + [0] * len(y_data))}
    
    dataset = Dataset.from_dict(pre_dataset)
    
    return dataset


def get_geo880(train_percentage=0.8, val_percentage=0.1):
    with open(GEO_DATAPATH, 'r') as datastream:
        raw_data = datastream.readlines()
    
    x_data = [_format_geodata_x(re.search(PATTERN, datapoint).groups()[0].split(',')) \
              for datapoint in raw_data]
    y_data = [_format_geodata_y(re.search(PATTERN, datapoint).groups()[1]) \
              for datapoint in raw_data]
    
    pre_dataset = {"text": x_data, "logical_form": y_data}
    
    dataset = Dataset.from_dict(pre_dataset)
    
    train_size = int(train_percentage * len(dataset))
    val_size = int(val_percentage * len(dataset))
    test_size = len(dataset) - train_size - val_size

    dataset_dict = dataset.train_test_split(train_size=train_size, test_size=(val_size + test_size))
    test_val_dict = dataset_dict["test"].train_test_split(train_size=val_size, test_size=test_size)
    
    dataset_dict["val"] = test_val_dict["train"]
    dataset_dict["test"] = test_val_dict["test"]
    
    return dataset_dict


def batch_predict(dataset, trainer, tokenizer, limit=50):
    results = []
    original_texts = []
    original_logical_forms = []
    predicted_logical_forms = []
    split_dataset = dataset.train_test_split(train_size=1, test_size=(len(dataset) - 1))
    
    for i in range(len(dataset) - 2):
        results.append(trainer.predict(split_dataset["train"]).predictions)
        original_logical_forms.append(split_dataset["train"]["logical_form"][0])
        original_texts.append(split_dataset["train"]["text"][0])
        split_dataset = split_dataset["test"].train_test_split(train_size=1, test_size=(len(dataset) - 2 - i))
        if i == limit - 3:
            break
        
    results.append(trainer.predict(split_dataset["train"]).predictions)
    if split_dataset["test"].num_rows == 1:
        results.append(trainer.predict(split_dataset["test"]).predictions)
    
    original_logical_forms.append(split_dataset["train"]["logical_form"][0])
    original_logical_forms.append(split_dataset["test"]["logical_form"][0])
    
    
    original_texts.append(split_dataset["train"]["text"][0])
    original_texts.append(split_dataset["test"]["text"][0])
    
    for result in results:
        text = []
        for value in result[0][0][1:]:
            _lst = list(value)
            _id = _lst.index(max(_lst))
            chunk = tokenizer.convert_ids_to_tokens(_id)
            if chunk == "</s>":
                break
                
            text.append(chunk)
        
        predicted_logical_forms.append("".join(text))
        
    return original_texts, original_logical_forms, predicted_logical_forms


def get_satoh_data(train_percentage=0.8, val_percentage=0.1):
    with open(SATOH_DATAPATH, 'r') as datastream:
        raw_data = datastream.readlines()
    
    x_data = []
    y_data = []
    for line in raw_data:
        i = 0
        indices = []
        while len(indices) < 4:
            i += line[i:].find("\"") + 1
            indices.append(i)

        x_data.append(line[indices[2]:indices[3] - 1])
        y_data.append(line[indices[0]:indices[1] - 1])
            
    pre_dataset = {"text": x_data, "logical_form": y_data}
    
    dataset = Dataset.from_dict(pre_dataset)
    
    train_size = int(train_percentage * len(dataset))
    val_size = int(val_percentage * len(dataset))
    test_size = len(dataset) - train_size - val_size

    dataset_dict = dataset.train_test_split(train_size=train_size, test_size=(val_size + test_size))
    test_val_dict = dataset_dict["test"].train_test_split(train_size=val_size, test_size=test_size)
    
    dataset_dict["val"] = test_val_dict["train"]
    dataset_dict["test"] = test_val_dict["test"]
    
    return dataset_dict


EXCLUDE_TYPES = ['designates_at_that', 'is_a_party_of', 'is_a_member_of', 'is_a_small_business_entity_as_informed_by', 'it_is_the_end_of', 'has_paid_itself', 'end_of_the_world']
#'is_the_aggregated_turnover_of', 'is_connected_to_as_informed_by']


def get_satoh_data_unseen(val_percentage=0.1):
    with open(SATOH_DATAPATH, 'r') as datastream:
        raw_data = datastream.readlines()
    
    x_data = []
    y_data = []
    for line in raw_data:
        i = 0
        indices = []
        while len(indices) < 4:
            i += line[i:].find("\"") + 1
            indices.append(i)

        x_data.append(line[indices[2]:indices[3] - 1])
        y_data.append(line[indices[0]:indices[1] - 1])
        
    unseen_x = []
    unseen_y = []
    for i, point in enumerate(y_data):
        name = point[:point.find("(")]
        if name in EXCLUDE_TYPES:
            unseen_x.append(x_data[i])
            unseen_y.append(point)
            
    for i, point in enumerate(unseen_x):
        x_data.remove(point)
        y_data.remove(unseen_y[i])
                    
    pre_dataset = {"text": x_data, "logical_form": y_data}
    
    dataset = Dataset.from_dict(pre_dataset)
    unseen_dataset = Dataset.from_dict({"text": unseen_x, "logical_form": unseen_y})
    
    val_size = int(val_percentage * len(dataset))
    test_size = 50
    train_size = len(dataset) - val_size - test_size

    dataset_dict = dataset.train_test_split(train_size=train_size, test_size=(val_size + test_size))
    test_val_dict = dataset_dict["test"].train_test_split(train_size=val_size, test_size=test_size)
    
    dataset_dict["val"] = test_val_dict["train"]
    dataset_dict["test"] = test_val_dict["test"]
    dataset_dict["test"] = unseen_dataset#concatenate_datasets([dataset_dict["test"], unseen_dataset])
    
    return dataset_dict


def get_satoh2_data(train_percentage=0.8, val_percentage=0.1):
    with open(SATOH2_DATAPATH, 'r') as datastream:
        raw_data = datastream.readlines()
    
    x_data = []
    y_data = []
    for line in raw_data:
        i = 0
        indices = []
        while len(indices) < 4:
            i += line[i:].find("\"") + 1
            indices.append(i)

        x_data.append(line[indices[0]:indices[1] - 1])
        y_data.append(line[indices[2]:indices[3] - 1])
            
    pre_dataset = {"text": y_data, "logical_form": x_data}
    
    dataset = Dataset.from_dict(pre_dataset)
    
    train_size = int(train_percentage * len(dataset))
    val_size = int(val_percentage * len(dataset))
    test_size = len(dataset) - train_size - val_size

    dataset_dict = dataset.train_test_split(train_size=train_size, test_size=(val_size + test_size))
    test_val_dict = dataset_dict["test"].train_test_split(train_size=val_size, test_size=test_size)
    
    dataset_dict["val"] = test_val_dict["train"]
    dataset_dict["test"] = test_val_dict["test"]
    
    return dataset_dict


def get_my_data(train_percentage=0.8, val_percentage=0.1):
    data = pd.read_csv(MY_DATAPATH)        
    pre_dataset = {"text": data["text"].tolist(), "logical_form": data["logical_form"].tolist()}
    
    dataset = Dataset.from_dict(pre_dataset)
    
    train_size = int(train_percentage * len(dataset))
    val_size = int(val_percentage * len(dataset))
    test_size = len(dataset) - train_size - val_size

    dataset_dict = dataset.train_test_split(train_size=train_size, test_size=(val_size + test_size))
    test_val_dict = dataset_dict["test"].train_test_split(train_size=val_size, test_size=test_size)
    
    dataset_dict["val"] = test_val_dict["train"]
    dataset_dict["test"] = test_val_dict["test"]
    
    return dataset_dict


def get_split(nr, val_percentage=0.1):
    with open(SPLIT_DATAPATH.format(nr), "rb") as f:
        train, test = pickle.load(f)     
        
    train_data = {"text": [item["text"] for item in train], "logical_form": [item["logical_form"] for item in train]}
    test_data = {"text": [item["text"] for item in test], "logical_form": [item["logical_form"] for item in test]}
    
    dataset = Dataset.from_dict(train_data)
    
    train_size = int((1.0 - val_percentage) * len(dataset))
    val_size = int(val_percentage * len(dataset))

    dataset_dict = dataset.train_test_split(train_size=train_size, test_size=val_size)
    
    dataset_dict["val"] = dataset_dict["test"]
    dataset_dict["test"] = Dataset.from_dict(test_data)
    
    return dataset_dict