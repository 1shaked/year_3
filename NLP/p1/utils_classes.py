import torch.nn as nn
import torch

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