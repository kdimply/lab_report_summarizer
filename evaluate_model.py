# evaluate_model.py
import spacy
from spacy.scorer import Scorer
from spacy.training import Example
from test_data import TEST_DATA

nlp = spacy.load("ner_model")

scorer = Scorer()
examples = []

for text, ann in TEST_DATA:
    example = Example.from_dict(nlp.make_doc(text), ann)
    examples.append(example)

scores = scorer.score(examples)
print("\n=== MODEL ACCURACY ===")
print("Precision:", scores["ents_p"])
print("Recall:", scores["ents_r"])
print("F-score:", scores["ents_f"])
print("\nPer-Entity Breakdown:")
print(scores["ents_per_type"])
