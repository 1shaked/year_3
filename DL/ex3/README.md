## Report for Exercise 3
### 1. Introduction
we implemented 5 types of networks:


## implementation
we can see all the implementation in the file `utils_func.py` where we have all the functions that will be used include the actual models.
* In the `exp_model.ipynb` is the file I ran in order to get the actual models.
  The file first choose device (mps for me because I have a mac GPU) configure the input_size, num_classes, and epochs.
  Then 5 blocks of example on how to run the models (there is no reason to run it manually because we already generalize it).
  Then you will see a train_with_variations function that will run the model with different parameter for the learning rate and for weight_decay (learning rate are [0.001, 0.01], weight_decay are [0, 0.0001] ).
  I choose to compare them and because it was time consuming to choose more 
* the file `server.py` is the file that will run the server and will be able to get the model and the data and will return the prediction.
* STL_10 is the react project that display the data 
* the `vis_p1.ipynb` is the file that will run the visualization of the data and the model (first question).