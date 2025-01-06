# Fashion MNIST Classification Project

This repository contains all the files and code for building, training, and deploying a neural network to classify the Fashion MNIST dataset. The project includes derivations, notebooks, utility functions, and a deployed website for showcasing results.

---

## **Project Overview**

1. **Dataset**: Fashion MNIST (28x28 grayscale images of 10 clothing categories).
2. **Objective**: 
   - Train and test a neural network for classification.
   - Optimize hyperparameters (batch size, learning rate, hidden layer size, etc.).
   - Deploy the model via a FastAPI server and a React website.
3. **Website**: [DL-Fashion-MNIST](https://dl-fashion-mnist.onrender.com)

---

## **Files and Directories**

### **Notebooks**
- **`p1_visualize.ipynb`**:
  - Visualizes the Fashion MNIST dataset as required in Task 1.
  - Creates a 10x4 grid of examples from each class.

- **`nn.ipynb`**:
  - Contains the complete implementation of the neural network.
  - Includes data preprocessing, model architecture, training, and testing.
  - Serves as the main development file before splitting the code into modular files.

### **Derivations**
- **`DL_derivate.pdf`**:
  - Detailed derivations of gradients and backpropagation used in the neural network.
  - Includes mathematical explanations and step-by-step derivations.

### **Python Files**
- **`utils.py`**:
  - Contains utility functions for the project, such as preprocessing, model evaluation, and other helpers.

- **`model_run.py`**:
  - Runs multiple versions of the neural network.
  - Experiments with different hyperparameters:
    - Batch size
    - Learning rate
    - Hidden layer size
    - Number of epochs
  - Saves the trained models in the `model_saved` folder.

- **`get_best_model.py`**:
  - Evaluates all saved models and identifies the one with the highest accuracy.

- **`train_best_model.py`**:
  - Loads the best model from `get_best_model.py`.
  - Trains the best model on the labeled test data.
  - Runs the model on unlabeled test data (`test.csv`).

- **`server.py`**:
  - A FastAPI server for deploying the neural network.
  - Provides an easy interface for interacting with the model.

### **Web Application**
- **`fashin_mnist`**:
  - A React-based website for demonstrating the model's performance.

- **`public/`**:
  - Compiled version of the React website for deployment.

### **Additional Files**
- **`requirements.txt`**:
  - List of all Python libraries required to run the project.
  - Use `pip install -r requirements.txt` to install dependencies.

---

## **Website**

Visit the deployed project at [https://dl-fashion-mnist.onrender.com](https://dl-fashion-mnist.onrender.com) to:
- Visualize the dataset.
- Test the model predictions.
- Explore the performance of the trained neural network.

---

## **Setup Instructions**

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-username/dl-fashion-mnist.git
   cd dl-fashion-mnist
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Server**:
   ```bash
   uvicorn server:app --reload
   ```

4. **View the Website**:
   Open your browser and navigate to [http://127.0.0.1:8000](http://127.0.0.1:8000).

---

## **How to Use**

### **Train and Save Models**
1. Use `model_run.py` to train multiple models with varying parameters.
2. Models are saved automatically in the `model_saved` folder.

### **Find the Best Model**
1. Run `get_best_model.py` to identify the model with the highest accuracy.

### **Test and Predict**
1. Use `train_best_model.py` to:
   - Train the best model on the test dataset.
   - Predict results on unlabeled data from `test.csv`.

---
