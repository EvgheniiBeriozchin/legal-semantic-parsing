import json
import nltk
from nltk.tokenize.punkt import PunktSentenceTokenizer, PunktParameters

alphabet = ["A","B","C","D","E","F","G","H","I","J","K","L","M","N","O","P","Q","R","S","T","U","V","W","X","Y","Z"]
ABBREVIATIONS = set(["para", "art", "no", "mr", "mrs"] + [" " + letter.lower() for letter in alphabet])


class ECHRData():
    
    
    def __init__(self):
        with open("../Datasets/echr_2_0_0_unstructured_cases.json", "r") as f:
            self.data = json.load(f)
        self.sentences = None
        self.texts = None
        punkt_parameters = PunktParameters()
        punkt_parameters.abbrev_types = ABBREVIATIONS
        self.tokenizer = PunktSentenceTokenizer(punkt_parameters)
    
    def get_unstructured_data(self):
        return self.data
    
    def get_data_as_texts(self):
        if self.texts is not None:
            return self.texts
        
        if self.sentences is None:
            self.get_data_as_sentences()
            
        self.texts = ["\n".join(case).replace("\n", " ") for case in self.sentences]
        return self.texts
            
    def get_data_as_sentences(self):
        if self.sentences is not None:
            return self.sentences
        
        nltk.download("punkt")
        cases = []
        for case in self.data:
            sentences = []
            to_parse = []
            for file in case["content"]:
                to_parse += case["content"][file][::-1]
                while len(to_parse) > 0:
                    parsed_block = to_parse.pop()
                    if parsed_block["content"] != "":
                        sentences += self.tokenizer.tokenize(parsed_block["content"])
                    if len(parsed_block["elements"]) > 0:
                        to_parse += parsed_block["elements"][::-1]
            cases.append(sentences)
            
        self.sentences = cases
        return self.sentences