import numpy as np
import pandas as pd
import random
import json
lambda_val = 0.01

# split the data into train and test
def split_data(data: list, split_ratio : float=0.8):
    train_size = int(len(data) * split_ratio)
    random.shuffle(data)
    return data[:train_size], data[train_size:]
# Initialize weights and biases
def initialize_parameters(input_size, hidden_size, output_size):
    np.random.seed(42)  # For reproducibility
    W1 = np.random.randn(input_size, hidden_size) * np.sqrt(2 / input_size)
    b1 = np.zeros((1, hidden_size))
    W2 = np.random.randn(hidden_size, output_size) * np.sqrt(2 / hidden_size)
    b2 = np.zeros((1, output_size))
    return W1, b1, W2, b2

# Forward propagation
def forward_propagation(X, W1, b1, W2, b2):
    # Hidden layer: Z1 = X.W1 + b1, A1 = ReLU(Z1)
    linear_l1 = np.dot(X, W1) + b1
    relu_res = np.maximum(0, linear_l1)  # ReLU activation

    # Output layer: Z2 = A1.W2 + b2, A2 = softmax(Z2)
    linear_l2 = np.dot(relu_res, W2) + b2
    y = softmax(linear_l2)
    
    return linear_l1, relu_res, linear_l2, y

# Softmax function (numerically stable)
def softmax(Z):
    # print("Z max:", np.max(Z), "Z min:", np.min(Z))
    exp_Z = np.exp(Z - np.max(Z, axis=1, keepdims=True))
    return exp_Z / np.sum(exp_Z, axis=1, keepdims=True)

# Cross-entropy loss
def compute_loss(y_true, y_pred):
    m = y_true.shape[0]
    loss = -np.sum(y_true * np.log(y_pred + 1e-8)) / m  # Add small epsilon for numerical stability
    return loss

def compute_loss_reg(y_true, y_pred, W1, W2, lambda_val=0.01):
    m = y_true.shape[0]
    cross_entropy_loss = -np.sum(y_true * np.log(y_pred + 1e-8)) / m
    reg_loss = (lambda_val / (2 * m)) * (np.sum(W1**2) + np.sum(W2**2))
    return cross_entropy_loss + reg_loss

# Back propagation
def backward_propagation(X, y_true, Z1, A1, Z2, A2, W1, W2):
    m = X.shape[0]

    # Output layer gradients
    dZ2 = A2 - y_true
    dW2 = np.dot(A1.T, dZ2) / m
    db2 = np.sum(dZ2, axis=0, keepdims=True) / m

    # Hidden layer gradients
    dA1 = np.dot(dZ2, W2.T)
    dZ1 = dA1 * (Z1 > 0)  # Derivative of ReLU
    dW1 = np.dot(X.T, dZ1) / m
    db1 = np.sum(dZ1, axis=0, keepdims=True) / m
    dW1 += (lambda_val / m) * W1
    dW2 += (lambda_val / m) * W2

    return dW1, db1, dW2, db2

def clip_gradients(gradients, threshold):
    for grad in gradients:
        np.clip(grad, -threshold, threshold, out=grad)
# Gradient descent update
def update_parameters(W1, b1, W2, b2, dW1, db1, dW2, db2, learning_rate):
    clip_gradients([dW1, db1, dW2, db2], threshold=1.0)
    W1 -= learning_rate * dW1
    b1 -= learning_rate * db1
    W2 -= learning_rate * dW2
    b2 -= learning_rate * db2
    return W1, b1, W2, b2

def one_hot_encode(y, num_classes):
    m = y.shape[0]
    one_hot = np.zeros((m, num_classes))
    one_hot[np.arange(m), y] = 1
    return one_hot


def train_neural_network_with_batches(X_train_batches, y_train_batches, hidden_size, learning_rate, epochs, output_size, init_params=None):
    input_size = X_train_batches.shape[2]
    batches_len = X_train_batches.shape[0]
    # Initialize parameters
    if init_params:
        W1, b1, W2, b2 = init_params
    else:
        W1, b1, W2, b2 = initialize_parameters(input_size, hidden_size, output_size)
    losses = []
    for epoch in range(epochs):
        total_loss = 0  # Initialize total loss for the epoch

        for batch in range(batches_len):
            X_train = X_train_batches[batch]
            y_train = y_train_batches[batch]
            # Forward propagation
            Z1, A1, Z2, A2 = forward_propagation(X_train, W1, b1, W2, b2)

            # Compute loss
            loss = compute_loss(y_train, A2)
            total_loss += loss
            # Backward propagation
            dW1, db1, dW2, db2 = backward_propagation(X_train, y_train, Z1, A1, Z2, A2, W1, W2)

            # Update parameters
            W1, b1, W2, b2 = update_parameters(W1, b1, W2, b2, dW1, db1, dW2, db2, learning_rate)
            # print("Z2 max:", np.max(Z2), "Z2 min:", np.min(Z2))
            # print("W1 max:", np.max(W1), "W1 min:", np.min(W1))

            # Print loss every 10 epochs
        losses.append(total_loss)
        if epoch % 100 == 0:
            print(f"Epoch {epoch}, Loss: {total_loss:.4f}")
    return W1, b1, W2, b2, losses

def get_x_and_labels(data: list[dict]):
    labels = []
    X = []
    for row in data:
        labels.append(row['label'])
        del row['label'] 
        X.append(list(row.values()))
    return X, labels

def split_to_batches(X, y, batch_size):
    X_batches = np.array_split(X, batch_size)
    y_batches = np.array_split(y, batch_size)
    return X_batches, y_batches

def normalize(X):
    X = np.array(X)
    X = (X - np.mean(X, axis=0)) / np.std(X, axis=0)
    return X

def eval_model(X_test, y_test, W1, b1, W2, b2):
    _, _, _, y_pred = forward_propagation(X_test, W1, b1, W2, b2)
    y_pred = np.argmax(y_pred, axis=1)
    accuracy = np.mean(y_pred == y_test)
    return accuracy

def save_model(W1, b1, W2, b2, batch_size, learning_rate, epochs, losses  ,filename):
    with open(f'model_saved/{filename}', 'w') as f:
        f.write(json.dumps({
            'batch_size': batch_size, 'learning_rate': learning_rate, 'epochs': epochs,
            'losses': losses,
            "W1": W1.tolist(), "b1": b1.tolist(), "W2": W2.tolist(), "b2": b2.tolist()}, indent=4))