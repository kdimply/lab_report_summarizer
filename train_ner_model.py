# train_ner_model.py
import spacy
import random
from spacy.training.example import Example
from pathlib import Path
from training_data import TRAIN_DATA

def train_spacy_ner_model(output_dir="./ner_model", n_iter=60):

    # ---------------------------------------------------------
    # INITIAL SETUP
    # ---------------------------------------------------------
    print("🔧 Initializing blank spaCy model ('en')...")
    nlp = spacy.blank("en")

    # Create NER component
    if "ner" not in nlp.pipe_names:
        ner = nlp.add_pipe("ner", last=True)
    else:
        ner = nlp.get_pipe("ner")

    # Add labels dynamically from training data
    print("📌 Adding labels...")
    for _, ann in TRAIN_DATA:
        for start, end, label in ann["entities"]:
            ner.add_label(label)

    # ---------------------------------------------------------
    # VALIDATE TRAINING DATA (SAFETY CHECK)
    # ---------------------------------------------------------
    print("🔍 Validating training data...")

    examples = []
    invalid = []

    for text, ann in TRAIN_DATA:
        try:
            example = Example.from_dict(nlp.make_doc(text), ann)
            examples.append(example)
        except Exception as e:
            invalid.append((text, ann, str(e)))

    if invalid:
        print(f"⚠️ Found {len(invalid)} INVALID samples (will be skipped):")
        for i in invalid[:5]:
            print("  ❌", i)
    else:
        print("✅ All training samples are valid!")

    print(f"📦 Total valid examples: {len(examples)}")

    # ---------------------------------------------------------
    # INITIALIZE MODEL
    # ---------------------------------------------------------
    print("⚡ Initializing model parameters...")
    nlp.initialize(lambda: examples)

    # ---------------------------------------------------------
    # TRAINING LOOP
    # ---------------------------------------------------------
    print("🚀 Starting training...\n")

    other_pipes = [p for p in nlp.pipe_names if p != "ner"]
    with nlp.disable_pipes(*other_pipes):

        optimizer = nlp.create_optimizer()

        for epoch in range(n_iter):
            random.shuffle(examples)
            losses = {}

            for batch in spacy.util.minibatch(examples, size=8):
                nlp.update(batch, sgd=optimizer, drop=0.3, losses=losses)

            if epoch % 5 == 0:
                print(f"🟢 Epoch {epoch}/{n_iter} | Loss: {losses}")

    # ---------------------------------------------------------
    # SAVE MODEL
    # ---------------------------------------------------------
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    nlp.to_disk(output_dir)

    print("\n🎉 Training Complete!")
    print(f"📁 Model saved at: {output_dir}")


if __name__ == "__main__":
    train_spacy_ner_model(n_iter=60)
