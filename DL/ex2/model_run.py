

import numpy as np
import pandas as pd
import json
from utils import eval_model, get_data, get_x_and_labels, normalize, one_hot_encode, save_model, split_data, split_to_batches, train_neural_network_with_batches



def multiple_version(output_size):
    batch_sizes = [64, 128, 256 , 512]
    learning_rates = [0.01, 0.001, 0.0001]
    hidden_sizes = [64, 128, 256]
    epochs_sizes = [125 ,250,500,1000, 2000, 3000]
    for batch_size in batch_sizes:
        for learning_rate in learning_rates:
            for hidden_size in hidden_sizes:
                for epochs in epochs_sizes:
                    X_train_batches, y_train_batches_one_hot , X_test ,y_test =  get_data(output_size, batch_size)
                    W1, b1, W2, b2, losses = train_neural_network_with_batches(X_train_batches, y_train_batches_one_hot, hidden_size=hidden_size, learning_rate=learning_rate, epochs=epochs, output_size=10)
                    acc = eval_model(X_test, y_test, W1, b1, W2, b2)
                    print(f'-----------------------------')
                print(f'the accuracy is {acc}')
                print(f"batch_size: {batch_size}, learning_rate: {learning_rate}, hidden_size: {hidden_size}")
                save_model(W1, b1, W2, b2,batch_size, learning_rate, epochs, losses ,f'model_{batch_size}_{learning_rate}_{hidden_size}_{epochs}.json')


                    

def get_parameters_form_file(file):
    with open(file) as f:
        data = json.load(f)
    W1 = data['W1']
    b1 = data['b1']
    W2 = data['W2']
    b2 = data['b2']
    batch_size = data['batch_size']
    learning_rate = data['learning_rate']
    epochs = data['epochs']
    hidden_size = int(file.split('_')[-1].split('.')[0])
    return W1, b1, W2, b2, batch_size, learning_rate, epochs , hidden_size


if __name__ == '__main__':
    multiple_version(10)