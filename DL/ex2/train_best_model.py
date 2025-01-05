

from utils import forward_propagation, get_data, save_model, train_neural_network_with_batches
import json
import pandas as pd
import numpy as np
def train_best_model():
    output_size = 10
    file_name = 'model_saved/model_64_0.01_128_3000.json'
    with open(file_name) as f:
        data = json.load(f)
    W1 = data['W1']
    b1 = data['b1']
    W2 = data['W2']
    b2 = data['b2']
    import pdb; pdb.set_trace()
    batch_size = data['batch_size']
    learning_rate = data['learning_rate']
    epochs = data['epochs']
    # get the hidden from the file name f'model_{batch_size}_{learning_rate}_{hidden_size}_{epochs}.json'
    hidden_size = int(file_name.split('_')[-2])
    X_train_batches, y_train_batches_one_hot , X_test ,y_test =  get_data(output_size, batch_size)
    W1, b1, W2, b2 = np.array(W1) , np.array(b1) , np.array(W2) , np.array(b2) 
    W1, b1, W2, b2, losses = train_neural_network_with_batches(
        X_train_batches, y_train_batches_one_hot, hidden_size=hidden_size, learning_rate=learning_rate, epochs=epochs, output_size=output_size,
        init_params=(W1, b1, W2, b2)    )
    save_model(W1, b1, W2, b2,batch_size, learning_rate, epochs, losses ,f'LAST_TRAIN_MODEL.json')
    

def run_best_model():
    with open('model_saved/LAST_TRAIN_MODEL.json') as f:
        data = json.load(f)
    W1 = data['W1']
    b1 = data['b1']
    W2 = data['W2']
    b2 = data['b2']
    df = pd.read_csv('test.csv')
    import pdb; pdb.set_trace()
    X_test = df.values.tolist()
    _, _, _, y_pred = forward_propagation(X_test, W1, b1, W2, b2)
    y_pred = np.argmax(y_pred, axis=1)
    # save the predictions to csv file
    with open("predictions.csv", "w") as file:
        for pred in y_pred:
            file.write(f"{pred}\n")


train_best_model()
run_best_model()