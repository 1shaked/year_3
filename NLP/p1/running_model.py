from transformers import pipeline
from transformers import AutoTokenizer
import torch
# import numpy as np
import pandas as pd
from transformers import TrainingArguments, Trainer
import os
from utils_classes import CommentsDataset, load_and_process_comments
from transformers import AutoModelForSequenceClassification

# Set the environment variable
os.environ["MKL_SERVICE_FORCE_INTEL"] = "1" # need for mac m1 , you may not need this

# Check PyTorch version
print("PyTorch version:", torch.__version__)
device = torch.device("cpu")  # Use CPU
# Check for GPU (CUDA) on Windows/Linux
if torch.cuda.is_available():
    device = torch.device("cuda")  # Use NVIDIA GPU (CUDA)
    print("CUDA is available! Using GPU for acceleration.")
# Check for MPS on macOS
elif torch.backends.mps.is_available():
    device = torch.device("mps")  # Use Metal Performance Shaders (MPS)
    print("MPS is available! Using GPU for acceleration.")
# Fallback to CPU
else:
    print("No GPU available. Using CPU.")

# model= 'distilbert-base-uncased' # "distilbert-base-uncased-finetuned-sst-2-english"

def train_model(model , batch_size=50):
    tokenizer = AutoTokenizer.from_pretrained(model)
    train_comments, val_comments, test_comments, test_labels = load_and_process_comments(
        train_path='train',
        batch_size=batch_size,
    )
    # Flatten train_comments
    train_texts = [text for batch in train_comments for text in batch[0]]
    train_labels = [label for batch in train_comments for label in batch[1]]
    # Flatten test_comments
    test_texts = [text for batch in test_comments for text in batch[0]]
    test_labels = [label for batch in test_comments for label in batch[1]]
    
    # Tokenize training and test data
    train_encodings = tokenizer(train_texts, truncation=True, padding=True, max_length=512)
    test_encodings = tokenizer(test_texts, truncation=True, padding=True, max_length=512)

    train_dataset = CommentsDataset(train_encodings, train_labels)
    test_dataset = CommentsDataset(test_encodings, test_labels)
    model_new = AutoModelForSequenceClassification.from_pretrained(
        model, 
        num_labels=2  # Adjust `num_labels` based on your dataset (e.g., binary classification)
    ).to(device)
    training_args = TrainingArguments(
        output_dir=f"./output/{model}",          # Directory to save the model
        eval_strategy="epoch",          # Evaluate after each epoch (updated argument)
        learning_rate=2e-5,             # Learning rate
        per_device_train_batch_size=16, # Batch size for training
        per_device_eval_batch_size=16,  # Batch size for evaluation
        num_train_epochs=3,             # Number of epochs
        weight_decay=0.01,              # Weight decay
        logging_dir="./logs",           # Directory for logs
        logging_steps=10,               # Log every 10 steps
        save_strategy="epoch",          # Save checkpoint each epoch
        load_best_model_at_end=True,    # Load best model at the end of training
    )
    trainer = Trainer(
        model=model_new,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=test_dataset,
        tokenizer=tokenizer,
    )
    trainer.train()
    print("Training completed!")


if __name__ == "__main__":
    train_model('distilbert-base-uncased')
    train_model('siebert/sentiment-roberta-large-english')

