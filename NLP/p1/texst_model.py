# %%
from transformers import pipeline
from transformers import AutoTokenizer
import torch
import numpy as np
import pandas as pd
from transformers import TrainingArguments, Trainer
from utils_classes import load_and_process_comments, CommentsDataset
model="distilbert-base-uncased-finetuned-sst-2-english"
# Load tokenizer for the model

tokenizer = AutoTokenizer.from_pretrained(model)

print(torch.cuda.is_available())  # Returns True if a GPU is available
print(torch.cuda.device_count())  # Number of GPUs



train_comments, val_comments, test_comments, test_labels = load_and_process_comments(
    train_path='train',
    batch_size=50,
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




# Create dataset objects
train_dataset = CommentsDataset(train_encodings, train_labels)
test_dataset = CommentsDataset(test_encodings, test_labels)

# %%
training_args = TrainingArguments(
    output_dir="./results",          # Directory to save the model
    evaluation_strategy="epoch",    # Evaluate after each epoch
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
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=test_dataset,
    tokenizer=tokenizer,
)

trainer.train()
# evaluate the model
results = trainer.evaluate()
# save the evaluation results

