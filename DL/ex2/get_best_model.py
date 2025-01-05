
import os
import math
import json

from utils import eval_model , get_data
def get_best_model():
    output_size = 10
    models = os.listdir('model_saved')
    best_acc = 0
    best_model = None
    for file_name in models:
        with open(f'model_saved/{file_name}') as f:
            data = json.load(f)
        W1 = data['W1']
        b1 = data['b1']
        W2 = data['W2']
        b2 = data['b2']
        batch_size = data['batch_size']
        learning_rate = data['learning_rate']
        epochs = data['epochs']
        X_train_batches, y_train_batches_one_hot , X_test ,y_test =  get_data(output_size, batch_size)
        acc = eval_model(X_test, y_test, W1, b1, W2, b2)

        if acc > best_acc:
            best_acc = acc        
            best_model = file_name
            print(f'The accuracy is {acc} of model {file_name}')
            print(f'-----------------------------')
    print(f"The best model is {best_model} with accuracy {best_acc}")
    return best_model

get_best_model()