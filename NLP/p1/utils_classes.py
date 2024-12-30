import torch.nn as nn
import torch
import numpy as np
import random
import os


batch_size = 50
train_size = 0.8
test_size = 0.2
embedding_dim = 100
hidden_dim = 128
output_dim = 1
class SentimentLSTMTwoLayers(nn.Module):
    def __init__(self, vocab_size, embedding_dim, hidden_dim, output_dim, num_layers=2, embedding_matrix=None, freeze_embeddings=True):
        super(SentimentLSTMTwoLayers, self).__init__()

        # Step 1. Embedding Layer
        self.embedding = nn.Embedding(vocab_size, embedding_dim)
        if embedding_matrix is not None:
            self.embedding.weight.data.copy_(torch.tensor(embedding_matrix, dtype=torch.float32))
            self.embedding.weight.requires_grad = not freeze_embeddings
        
        # Step 2. LSTM Layer with Multiple Layers
        self.lstm = nn.LSTM(embedding_dim, hidden_dim, num_layers=num_layers, batch_first=True, dropout=0.2)
        
        # Step 3. Fully Connected Layers (Stacked for Depth)
        self.fc1 = nn.Linear(hidden_dim, hidden_dim // 2)
        self.fc2 = nn.Linear(hidden_dim // 2, output_dim)
        
        # Step 4. Activation Functions
        self.relu = nn.ReLU()
        self.sigmoid = nn.Sigmoid()
    
    def forward(self, x):
        # Pass input through embedding layer
        embedded = self.embedding(x)
        
        # Pass embeddings through the LSTM layer
        lstm_out, (hidden, cell) = self.lstm(embedded)
        
        # Take the output from the last hidden state
        hidden_state = hidden[-1]
        
        # Pass through fully connected layers
        fc1_out = self.relu(self.fc1(hidden_state))
        final_output = self.sigmoid(self.fc2(fc1_out))
        
        return final_output



class SentimentGRUTwoLayers(nn.Module):
    def __init__(self, vocab_size, embedding_dim, hidden_dim, output_dim, embedding_matrix=None, freeze_embeddings=True):
        super(SentimentGRUTwoLayers, self).__init__()
        
        # Step 1. Embedding Layer
        self.embedding = nn.Embedding(vocab_size, embedding_dim)
        if embedding_matrix is not None:
            self.embedding.weight.data.copy_(torch.tensor(embedding_matrix, dtype=torch.float32))  # Load pre-trained embeddings
            self.embedding.weight.requires_grad = not freeze_embeddings  # Freeze or allow fine-tuning
        
        # Step 2. GRU Layer
        self.gru = nn.GRU(embedding_dim, hidden_dim, num_layers=1, batch_first=True)
        
        # Step 3. Fully Connected Layer
        self.fc = nn.Linear(hidden_dim, output_dim)
        
        # Step 4. Sigmoid Activation for Binary Classification
        self.sigmoid = nn.Sigmoid()
    
    def forward(self, x):
        # Pass input through embedding layer
        embedded = self.embedding(x)
        
        # Pass embeddings through the GRU layer
        gru_out, hidden = self.gru(embedded)
        
        # Take the output from the last hidden state
        final_output = self.fc(hidden[-1])
        
        # Apply sigmoid activation
        output = self.sigmoid(final_output)
        return output

def load_glove_embeddings(file_path, embedding_dim):
    """
    Load GloVe embeddings from the file into a dictionary.
    """
    embedding_dict = {}
    with open(file_path, 'r', encoding="utf-8") as f:
        for line in f:
            values = line.split()
            word = values[0]  # The word
            vector = np.array(values[1:], dtype="float32")  # The embedding vector
            embedding_dict[word] = vector
    print(f"Loaded {len(embedding_dict)} word vectors.")
    return embedding_dict



# Tokenize comments
def tokenize_comments(comments, vocab):
    tokenized_comments = []
    for comment in comments:
        tokens = comment.split()  # Simple whitespace tokenizer
        token_indices = [vocab.get(token, vocab["<UNK>"]) for token in tokens]
        tokenized_comments.append(token_indices)
    return tokenized_comments

# Pad sequences to a fixed length
def pad_sequences(sequences, max_len, pad_value):
    padded_sequences = []
    for seq in sequences:
        if len(seq) < max_len:
            seq = seq + [pad_value] * (max_len - len(seq))
        else:
            seq = seq[:max_len]
        padded_sequences.append(seq)
    return padded_sequences


def create_embedding_matrix(vocab, glove_embeddings, embedding_dim):
    """
    Create an embedding matrix where each row corresponds to a token in the vocabulary.
    """
    vocab_size = len(vocab)
    embedding_matrix = np.zeros((vocab_size, embedding_dim))  # Initialize matrix with zeros

    for word, idx in vocab.items():
        if word in glove_embeddings:
            embedding_matrix[idx] = glove_embeddings[word]
        else:
            # Initialize randomly for missing words
            embedding_matrix[idx] = np.random.uniform(-0.01, 0.01, embedding_dim)

    return embedding_matrix

def get_vocabulary():
    vocab_file = 'imdb.vocab'
    with open(vocab_file, 'r') as f:
        vocab_words = f.read().splitlines()

    tokenized_sentences = vocab_words
    tokenized_sentences.append('<UNK>')  # Add <UNK> token for unknown words
    tokenized_sentences.append('<PAD>')  # Add <PAD> token to pad sequences
    # Create vocabulary
    vocab_size = len(vocab_words)
    # tokens = list(chain(*tokenized_sentences))
    vocab = {word: idx for idx, word in enumerate(tokenized_sentences)}
    return vocab, vocab_size


def train_model(model, train_comments, val_comments, vocab, criterion, optimizer, device, num_epochs, batch_size, max_len=200):
    """
    Train the model using the provided training data.

    Args:
        model: The neural network model to train.
        train_comments: List of training data batches (comments and labels).
        val_comments: List of validation data labels.
        vocab: Vocabulary mapping for tokenization.
        criterion: Loss function.
        optimizer: Optimizer.
        device: Device to run the training (CPU or GPU).
        num_epochs: Number of training epochs.
        batch_size: Batch size for training.
        max_len: Maximum length for padding sequences.

    Returns:
        losses: List of epoch-wise training losses.
        accuracies: List of epoch-wise training accuracies.
    """
    losses = []
    accuracies = []

    for epoch in range(num_epochs):
        model.train()  # Set model to training mode
        epoch_loss = 0
        correct_predictions = 0
        total_predictions = 0

        # Loop through batches
        for comments, labels in train_comments:
            # Move data to device
            comments_padded = pad_sequences(
                tokenize_comments(comments, vocab), max_len=max_len, pad_value=vocab["<PAD>"]
            )
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

    return losses, accuracies



def test_model(model, test_comments, test_labels, batch_size=32 , device=None, max_len=200, criterion=None , vocab = None):
    model.eval()  # Set model to evaluation mode
    
    total_loss = 0
    correct_predictions = 0
    total_predictions = 0

    with torch.no_grad():  # Disable gradient calculations
        for comment_obj in test_comments:
            # Extract batch
            comments_batch = comment_obj[0]
            labels_batch = comment_obj[1]
            comments_padded = pad_sequences(tokenize_comments(comments_batch, vocab), max_len=200, pad_value=vocab["<PAD>"])

            # Convert to tensors and move to device
            comments = torch.tensor(comments_padded, dtype=torch.long).to(device)
            labels = torch.tensor(labels_batch, dtype=torch.float32).to(device)

            # Forward pass
            predictions = model(comments).squeeze(1)

            # Compute loss
            loss = criterion(predictions, labels)
            total_loss += loss.item()

            # Accuracy calculations
            preds = (predictions >= 0.5).float()
            correct_predictions += (preds == labels).sum().item()
            total_predictions += labels.size(0)

    # Compute metrics
    average_loss = total_loss / (len(test_comments) // batch_size)
    accuracy = correct_predictions / total_predictions

    print(f"Test Loss: {average_loss:.4f}, Test Accuracy: {accuracy:.4f}")
    return average_loss, accuracy




def load_and_process_comments(train_path='train', batch_size=50, train_size=0.8):
    """
    Load, label, shuffle, and batch comments for training and testing.

    Args:
        train_path (str): Path to the training data directory.
        batch_size (int): Size of each batch.
        train_size (float): Proportion of data to use for training.

    Returns:
        train_comments: Batches of training comments and labels.
        val_comments: Validation labels.
        test_comments: Batches of testing comments and labels.
        test_labels: Testing labels.
    """
    # Get positive and negative comment file names
    pos = os.listdir(f'{train_path}/pos')
    neg = os.listdir(f'{train_path}/neg')
    pos = list(filter(lambda x: '._' not in x, pos))
    neg = list(filter(lambda x: '._' not in x, neg))

    # Read the comments from files
    pos_comments = [open(f'{train_path}/pos/{f}', 'r').read() for f in pos]
    neg_comments = [open(f'{train_path}/neg/{f}', 'r').read() for f in neg]

    # Label the comments
    pos_labels = [1] * len(pos_comments)
    neg_labels = [0] * len(neg_comments)

    # Combine and shuffle the comments and labels
    comments = pos_comments + neg_comments
    labels = pos_labels + neg_labels
    combined = list(zip(comments, labels))
    random.shuffle(combined)
    comments, labels = zip(*combined)

    # Create batches
    batched_comments = [
        (comments[i:i + batch_size], labels[i:i + batch_size])
        for i in range(0, len(comments), batch_size)
    ]

    # Split into training and testing
    train_len = int(train_size * len(batched_comments))
    train_comments = batched_comments[:train_len]
    val_comments = labels[:train_len]

    test_comments = batched_comments[train_len:]
    test_labels = labels[train_len:]

    return train_comments, val_comments, test_comments, test_labels
