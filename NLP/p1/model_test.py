from utils_classes import SentimentGRUTwoLayers, embedding_dim,hidden_dim,output_dim , batch_size, train_size,SentimentLSTMTwoLayers, create_embedding_matrix, get_vocabulary, load_and_process_comments, load_glove_embeddings, pad_sequences, test_model, tokenize_comments, train_model
import torch
import torch.nn as nn
import os
import random
random.seed(42)
import torch.optim as optim


train_comments, val_comments, test_comments, test_labels = load_and_process_comments(
    train_path='train',
    batch_size=batch_size,
    train_size=train_size
)
vocab, vocab_size = get_vocabulary()

model_type = os.environ['MODEL']
model = SentimentLSTMTwoLayers(vocab_size, embedding_dim, hidden_dim, output_dim, 2)
if model_type == 'GRU':
    model = SentimentGRUTwoLayers(vocab_size, embedding_dim, hidden_dim, output_dim, 2)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = model.to(device)

average_loss, accuracy = test_model(
    model=model,
    test_comments=test_comments,
    test_labels=test_labels,
    device=device,
    batch_size=batch_size
)

print(f"Average Loss: {average_loss}")
print(f"Accuracy: {accuracy}")