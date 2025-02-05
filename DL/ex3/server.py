from fastapi.responses import FileResponse
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
import torch
import os
# Set device (use MPS for Mac M1, fallback to CUDA or CPU)
device = torch.device("mps") if torch.backends.mps.is_available() else (
    torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
)
print(f"Using device: {device}")


app = FastAPI()
# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)
app.mount("/static", StaticFiles(directory="public"), name="static")
app.mount("/assets", StaticFiles(directory="public/assets"), name="assets")

def extract_values_from_file(name: str):
    # file_name = f"./models/{name_file}_lr_{lr}_wd_{wd}.pth"
    name_file = name.split("_")[0]
    lr = name.split("_lr_")[1].split('_')[0]

    wd = name.split("_")[-1].split(".")[0]
    return {"name": name_file, "lr": lr, "weight_decay": wd, "file": name}
@app.get("/get_models")
async def get_models():
    models = os.listdir("models")
    models_arr = list(map(lambda x: extract_values_from_file(x), models))
    # file_name = f"./models/{name_file}_lr_{lr}_wd_{wd}.pth"
    # extract the name of the model

    return models_arr

@app.get("/get_model/{model_name}")
async def get_model(model_name):
    file_name = f"./models/{model_name}"
    # read the pth file and return the content
    checkpoint = torch.load(file_name, map_location=torch.device(device))
    # model_state_dict = checkpoint.get("model_state_dict", None)  # Model weights
    data = dict(checkpoint)
    # remove the model_state_dict and optimizer_state_dict
    data.pop("model_state_dict")
    data.pop("optimizer_state_dict")
    return data

@app.get("/")
async def read_root():
    import os
    print(os.listdir("public"))
    return FileResponse("public/index.html")
