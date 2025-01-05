


import json
from fastapi.responses import FileResponse
import numpy as np
import pandas as pd
from utils import eval_model, forward_propagation
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
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
# app.mount("/static", StaticFiles(directory="public"), name="static")
# app.mount("/assets", StaticFiles(directory="public/assets"), name="assets")

# Define the request schema
class PredictRequest(BaseModel):
    model: str
    number_of_samples: int
# Define the prediction endpoint
@app.post("/get_examples")
async def get_examples(request: PredictRequest):
    df = pd.read_csv('test.csv')
    X_test = df.values.tolist()
    models_names = os.listdir("model_saved")
    if request.model not in models_names:
        request.model = "LAST_TRAIN_MODEL"
    with open(f'model_saved/{request.model}') as f:
        data = json.load(f)
    W1 = data['W1']
    b1 = data['b1']
    W2 = data['W2']
    b2 = data['b2']
    # select 10 random samples
    import random
    random.shuffle(X_test)
    X_test = X_test[:request.number_of_samples]
    _, _, _, y_pred = forward_propagation(X_test, W1, b1, W2, b2)
    y_pred = np.argmax(y_pred, axis=1)
    y_pred = y_pred.tolist()
    X_test = list(X_test)
    return {
        'data': X_test,
        'predictions': y_pred
    }

@app.get("/get_models")
async def get_models():
    models = os.listdir("model_saved")
    return models

@app.get("/")
async def read_root():
    import os
    print(os.listdir("public"))
    return FileResponse("public/index.html")
