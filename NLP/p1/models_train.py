

# Path to GloVe file and embedding dimensions
from utils_classes import SentimentGRUTwoLayers, SentimentLSTMTwoLayers, create_embedding_matrix, get_vocabulary, load_glove_embeddings, pad_sequences, tokenize_comments
import torch
import torch.nn as nn
import os

glove_file_path = "glove.6B.100d.txt"
embedding_dim = 100
hidden_dim = 128
output_dim = 1
learning_rate = 0.001
num_epochs = 20 # Number of epochs
NUM_LAYERS = 2
batch_size = 50
train_size = 0.8
test_size = 0.2
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

# Getting the comments
batched_comments = []
pos = os.listdir('train/pos')
neg = os.listdir('train/neg')
pos = list(filter(lambda x: '._' not in x, pos))
neg = list(filter(lambda x: '._' not in x, neg))
# Read the comments from files
pos_comments = [open(f'train/pos/{f}', 'r').read() for f in pos]
neg_comments = [open(f'train/neg/{f}', 'r').read() for f in neg]

# Label the comments
pos_labels = [1] * len(pos_comments)
neg_labels = [0] * len(neg_comments)

# Combine and shuffle the comments and labels
comments = pos_comments + neg_comments
labels = pos_labels + neg_labels
combined = list(zip(comments, labels))
random.shuffle(combined)
comments, labels = zip(*combined)
batched_comments = [(comments[i:i + batch_size], labels[i:i + batch_size]) for i in range(0, len(comments), batch_size)]

train_len = train_size * len(batched_comments)
test_len = len(batched_comments) - train_len
train_comments = batched_comments[:int(train_len)]
val_comments = labels[:int(train_len)]

test_comments = batched_comments[int(train_len):]
test_labels = labels[int(train_len):]
losses = []
accuracies = []

# Training Loop
for epoch in range(num_epochs):
    model.train()  # Set model to training mode
    epoch_loss = 0
    correct_predictions = 0
    total_predictions = 0

    # Loop through batches
    for comments, labels in train_comments:  # Assuming train_comments is a list of (comments, labels) batches
        # Move data to device
        comments_padded = pad_sequences(tokenize_comments(comments, vocab), max_len=200, pad_value=vocab["<PAD>"])
        
        comments = torch.tensor(comments_padded, dtype=torch.long).to(device)  # Shape: [batch_size, sequence_length]
        labels = torch.tensor(labels, dtype=torch.float32).to(device)  # Shape: [batch_size]

        # Forward pass
        predictions = model(comments).squeeze(1)  # Shape: [batch_size]

        # Compute loss
        loss = criterion(predictions, labels)
        # Backward pass
        optimizer.zero_grad()  # Reset gradients
        loss.backward()  # Backpropagation
        optimizer.step()  # Update model weights

        # Accumulate loss and accuracy
        epoch_loss += loss.item()
        preds = (predictions >= 0.5).float()  # Convert probabilities to binary labels
        correct_predictions += (preds == labels).sum().item()
        total_predictions += labels.size(0)


    # Print epoch summary
    accuracy = correct_predictions / total_predictions
    losses.append(epoch_loss / len(train_comments))
    accuracies.append(accuracy)
    print(f"Epoch {epoch+1}/{num_epochs}, Loss: {epoch_loss / len(train_comments):.4f}, Accuracy: {accuracy:.4f}")