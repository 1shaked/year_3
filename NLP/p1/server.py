


from utils_classes import SentimentLSTMTwoLayers, tokenize_comments, pad_sequences
import torch
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI(
)
# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

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

embedding_dim = 100  # Same as GloVe
hidden_dim = 128
output_dim = 1
learning_rate = 0.01
num_epochs = 10
# Initialize the LSTM model
# Load model and state dict
model = SentimentLSTMTwoLayers(vocab_size, embedding_dim, hidden_dim, output_dim, 2)
model.load_state_dict(torch.load("model_parameters_2_LAYERS_layers_new.pth"))
# model_gru = SentimentGRU(vocab_size, embedding_dim, hidden_dim, output_dim, embedding_matrix_gru, freeze_embeddings=True)


# Define the request schema
class PredictRequest(BaseModel):
    comments: List[str]  # List of input comments

# Define the prediction endpoint
@app.post("/predict")
async def predict(request: PredictRequest):
    try:
        # Preprocess the input comments
        max_len = 200  # Maximum sequence length
        
        tokenized_comments = pad_sequences(tokenize_comments(request.comments, vocab), max_len=max_len, pad_value=vocab["<PAD>"])
        input_tensor = torch.tensor(tokenized_comments, dtype=torch.long)

        # Make predictions
        with torch.no_grad():
            predictions = model(input_tensor)
        
        # Convert predictions to probabilities and labels
        results = [
            {"probability": float(pred.item()), "label": "positive" if pred >= 0.5 else "negative"}
            for pred in predictions.squeeze(1)
        ]
        return {"results": results}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
