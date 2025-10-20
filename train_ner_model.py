# train_ner_model.py

import spacy
from spacy.training.example import Example
import random
from pathlib import Path
from training_data import TRAIN_DATA # Import your labeled data

def train_spacy_ner_model():
    """Trains a custom spaCy NER model."""
    
    # Define the output directory to save the trained model
    output_dir = Path("./ner_model")
    n_iter = 100  # Number of training iterations

    # Load a blank English model
    nlp = spacy.blank("en")
    print("Created blank 'en' model")

    # Create the NER pipeline component
    if "ner" not in nlp.pipe_names:
        ner = nlp.add_pipe("ner", last=True)
    else:
        ner = nlp.get_pipe("ner")

    # Add our custom labels to the NER component
    for _, annotations in TRAIN_DATA:
        for ent in annotations.get("entities"):
            ner.add_label(ent[2])

    # Get names of other pipes to disable them during training to train only NER
    pipe_exceptions = ["ner", "trf_wordpiecer", "trf_tok2vec"]
    unaffected_pipes = [pipe for pipe in nlp.pipe_names if pipe not in pipe_exceptions]

    # Start the training
    print("Starting training...")
    with nlp.disable_pipes(*unaffected_pipes):
        optimizer = nlp.begin_training()
        for itn in range(n_iter):
            random.shuffle(TRAIN_DATA)
            losses = {}
            for text, annotations in TRAIN_DATA:
                try:
                    # Create an Example object
                    example = Example.from_dict(nlp.make_doc(text), annotations)
                    # Update the model
                    nlp.update([example], drop=0.5, sgd=optimizer, losses=losses)
                except Exception as e:
                    # Some annotations might be misaligned, so we skip them
                    # In a real project, you would fix these in your training_data.py
                    pass 
            
            # Print the losses every 10 iterations
            if itn % 10 == 0:
                print(f"Iteration {itn}/{n_iter}, Losses: {losses}")

    # Save the trained model to the output directory
    nlp.to_disk(output_dir)
    print(f"✅ Saved trained model to '{output_dir}'")

if __name__ == "__main__":
    train_spacy_ner_model()