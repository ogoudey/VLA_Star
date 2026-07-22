import spacy
import sys
from distutils.util import strtobool
import json
# Load English tokenizer, tagger, parser and NER
nlp = spacy.load("en_core_web_sm")

with open(f"{sys.argv[1]}") as f:
    responses = {}
    for line in f:
        j = json.loads(line)
        print(f"@{list(j.values())[0][0]['timestamp']}")
        try:
            text = f"{j['robot'][0]['content']}\n"
            print(f"\tRobot: {text}")
            doc = nlp(text)
            
            for chunk in doc.noun_chunks:
                response = strtobool(input(f"{chunk.text} (y or no): "))
                responses[f"{chunk.text}"] = response
                
            for token in doc:
                if token.pos_ == "VERB":
                    response = strtobool(input(f"{token.lemma_} (y or no): "))
                    responses[f"{token.lemma_}"] = response
        except KeyError:
            print(f"\tUser: {list(j.values())[0][0]['content']}")
print(f"Done.\nResponses:\n{json.dumps(responses)}")
