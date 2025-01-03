# NLP Sentiment Analysis Project

This project focuses on **Sentiment Analysis** of text using **Deep Learning** techniques, applied to the IMDB dataset. It explores various neural network architectures and techniques to classify movie reviews as positive or negative.

## Project Overview

- **Dataset**: IMDB dataset for sentiment analysis.
- **Goal**: Build and evaluate sentiment analysis models using LSTM and GRU architectures.
- **Features**:
  - Use of pretrained word embeddings.
  - Hyperparameter tuning for model optimization.
  - Comprehensive evaluation of model performance.

## Project Components

### 1. `model_2_layer.py`
Contains the implementation of a two-layer neural network architecture, optimized for better performance in sentiment analysis tasks.

### 2. `utils_classes.py`
Provides utility classes and helper functions to facilitate data preprocessing, model training, and evaluation.

### 3. `server.py`
Hosts a simple website that can classify user-submitted comments as "good" or "bad." Try it live at: [NLP Comments Analyser](https://nlp-comments-analyser.onrender.com/).

### 4. `models_train.py`
Script for training models, including setting up configurations, initializing models, and managing training loops.

### 5. `model_test.py`
Includes the evaluation routines for trained models, enabling the analysis of their performance on validation and test datasets.

## Instructions

1. Clone this repository:
   ```bash
   git clone https://github.com/1shaked/year_3.git
   cd NLP/p1
