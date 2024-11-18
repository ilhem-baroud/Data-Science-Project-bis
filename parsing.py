import warnings
warnings.filterwarnings("ignore")

import spacy
import pickle
import random
from spacy.training import Example
from spacy.util import minibatch
import re

import fitz

# Load training data
TRAIN_DATA = pickle.load(open('train_data.pkl','rb'))

# Initialize the blank English NLP model
nlp = spacy.blank("en")

# Add the 'ner' component if it doesn't already exist
if "ner" not in nlp.pipe_names:
    ner = nlp.add_pipe("ner", last=True)
else:
    ner = nlp.get_pipe("ner")

# Add labels to the 'ner' component from training data
for _, annotations in TRAIN_DATA:
    for ent in annotations['entities']:
        ner.add_label(ent[2])

# Helper functions to clean entity spans and filter overlapping entities
def trim_entity_spans(data):
    invalid_span_tokens = re.compile(r'\s')
    cleaned_data = []
    for text, annotations in data:
        entities = annotations['entities']
        valid_entities = []
        for start, end, label in entities:
            valid_start = start
            valid_end = end
            while valid_start < len(text) and invalid_span_tokens.match(text[valid_start]):
                valid_start += 1
            while valid_end > 1 and invalid_span_tokens.match(text[valid_end - 1]):
                valid_end -= 1
            valid_entities.append([valid_start, valid_end, label])
        cleaned_data.append((text, {'entities': valid_entities}))
    return cleaned_data

def filter_overlapping_entities(entities):
    entities = sorted(entities, key=lambda x: (x[0], -(x[1] - x[0])))
    non_overlapping_entities = []
    for entity in entities:
        start, end, label = entity
        if not non_overlapping_entities or start >= non_overlapping_entities[-1][1]:
            non_overlapping_entities.append(entity)
    return non_overlapping_entities

# Clean the data
NEW_DATA_1 = trim_entity_spans(TRAIN_DATA)
NEW_DATA = [(text, {'entities': filter_overlapping_entities(annotations['entities'])}) for text, annotations in NEW_DATA_1]

# Initialize the optimizer
optimizer = nlp.begin_training()

# Shuffle and batch the data
random.shuffle(NEW_DATA)
losses = {}
for wy in range(10):
    for text, annotations in NEW_DATA:
        doc = nlp.make_doc(text)
        example = Example.from_dict(doc, annotations)
        nlp.update([example], drop=0.35, sgd=optimizer, losses=losses)
    print(f"Losses: {losses}")

# Save the trained model
nlp.to_disk("resume_parser_model")

