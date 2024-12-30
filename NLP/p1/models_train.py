

# Path to GloVe file and embedding dimensions
from utils_classes import SentimentGRUTwoLayers, embedding_dim, output_dim ,hidden_dim ,batch_size, train_size,SentimentLSTMTwoLayers, create_embedding_matrix, get_vocabulary, load_and_process_comments, load_glove_embeddings, pad_sequences, test_model, tokenize_comments, train_model
import torch
import torch.nn as nn
import os
import random
random.seed(42)
import torch.optim as optim


glove_file_path = "glove.6B.100d.txt"
learning_rate = 0.001
num_epochs = 20 # Number of epochs
NUM_LAYERS = 2

glove_embeddings = load_glove_embeddings(glove_file_path, embedding_dim)


vocab, vocab_size = get_vocabulary()


embedding_matrix = create_embedding_matrix(vocab, glove_embeddings, embedding_dim)
embedding_tensor = torch.tensor(embedding_matrix, dtype=torch.float32)
embedding_layer = nn.Embedding(len(vocab), embedding_dim)
embedding_layer.weight.data.copy_(embedding_tensor)  # Load pre-trained weights
embedding_layer.weight.requires_grad = False

model_type = os.environ['MODEL']
model = SentimentLSTMTwoLayers(vocab_size, embedding_dim, hidden_dim, output_dim,NUM_LAYERS ,embedding_matrix, freeze_embeddings=True,)
if model_type == 'GRU':
    model = SentimentGRUTwoLayers(vocab_size, embedding_dim, hidden_dim, output_dim,NUM_LAYERS ,embedding_matrix, freeze_embeddings=True,)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = model.to(device)
criterion = nn.BCELoss()  # Binary Cross Entropy Loss for binary classification
optimizer = optim.Adam(model.parameters(), lr=learning_rate)

# Usage
train_comments, val_comments, test_comments, test_labels = load_and_process_comments(
    train_path='train',
    batch_size=batch_size,
    train_size=train_size
)

losses = []
accuracies = []



# Call the training function
losses, accuracies = train_model(
    model=model,
    train_comments=train_comments,
    val_comments=val_comments,
    vocab=vocab,
    criterion=criterion,
    optimizer=optimizer,
    device=device,
    num_epochs=num_epochs,
    batch_size=batch_size
)




