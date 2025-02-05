# Exercise 3 - Report

## Introduction
In this exercise, we implemented **five types of neural networks** and built a system to train, evaluate, and visualize the results. Below is a detailed explanation of the implementation, the models, and the tools used.

---

## Implementation Details

### Core Files and Functionality

1. **`utils_func.py`**:
   - This file contains all the utility functions required for the exercise, including the implementation of the models.
   - All core logic, including model architectures and helper functions for training and evaluation, is defined here.

2. **`exp_model.ipynb`**:
   - This Jupyter notebook is used to train and test the models.
   - Key steps performed in this notebook:
     - Configuring the device (e.g., **`mps`** for macOS GPUs).
     - Setting input parameters such as `input_size`, `num_classes`, and `epochs`.
     - Demonstrating how to run each of the five models through blocks of example code (though running them manually is unnecessary as the process has been generalized).
     - Using the `train_with_variations` function to train models with different parameter configurations:
       - **Learning rates**: `[0.001, 0.01]`
       - **Weight decay**: `[0, 0.0001]`
     - Since training can be time-consuming, only a limited set of configurations was compared.

3. **`server.py`**:
   - This file runs a FastAPI server to interact with the trained models.
   - The server provides endpoints to:
     - Load a model.
     - Input data for prediction.
     - Return predictions in a structured format.

4. **`STL_10` React Project**:
   - This is a React-based frontend application that displays the data and results of the models.
   - The app fetches data from the server (`server.py`) and visualizes predictions interactively.

5. **`vis_p1.ipynb`**:
   - This Jupyter notebook handles the visualization of the models and data (specifically for question 1).
   - Provides plots and metrics to evaluate the performance of each model.

---

## Models and Naming Conventions
The models implemented in this exercise are:

| Model Name                          | Abbreviation Used |
|-------------------------------------|-------------------|
| Logistic Regression                 | `logistic`        |
| Fully Connected Neural Network      | `fully`           |
| Convolutional Neural Network (CNN)  | `CNN`             |
| MobileNetV2 Feature Extractor       | `MobileNetV2FeatureExtractor` |
| MobileNetV2 Fine-Tuned Model        | `MobileNetV2FineTuned` |

---

## Key Features

### Training Configuration
- Device selection: The implementation supports running on macOS GPUs using `mps`, or defaults to `cuda`/`cpu` depending on availability.
- Parameters such as learning rate and weight decay can be varied and compared using `train_with_variations`.

### Frontend and Visualization
- The React app provides an interface to visualize predictions and compare results.
- The `vis_p1.ipynb` notebook offers detailed plots and insights into model performance.

### Server API
- The FastAPI server (`server.py`) allows the backend to handle model loading, data submission, and predictions efficiently.

---

## Conclusion
This exercise demonstrated the implementation of five neural network models, along with their training, evaluation, and visualization. The project integrates backend functionality (FastAPI), model implementation (PyTorch), and frontend visualization (React), creating a complete pipeline for machine learning workflows. 

### Notes:
- The project uses structured and modularized files for easier scalability and reproducibility.
- The training and testing processes have been generalized to avoid manual intervention.
- [Link to the website](https://year-3.onrender.com)