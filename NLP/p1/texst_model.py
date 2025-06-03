from transformers import AutoTokenizer, AutoModelForSequenceClassification, TrainingArguments, Trainer, EvalPrediction
import torch
import numpy as np
import pandas as pd
# Removed redundant import, consolidated into a single line above
from utils_classes import load_and_process_comments, CommentsDataset
from datasets import load_metric
import torch.nn.utils.prune as prune
from onnxruntime.quantization import quantize_dynamic, QuantType
import onnx
import onnxruntime as ort
from sklearn.metrics import accuracy_score

if torch.backends.mps.is_available():
    device = torch.device("mps")  # Use MPS (Metal GPU)
elif torch.backends.cuda.is_available():
    device = torch.device("cuda")
else:
    device = torch.device("cpu")  # Fallback to CPU

# Check if MPS is available
# device = 0 if torch.backends.mps.is_available() else -1
print(f"Using device: {device}")


# Load accuracy metric from Hugging Face
accuracy_metric = load_metric("accuracy")

def compute_metrics(eval_pred: EvalPrediction):
    """
    Compute accuracy for evaluation.
    
    Args:
        eval_pred (EvalPrediction): Predictions from the model.

    Returns:
        dict: Dictionary containing accuracy.
    """
    logits, labels = eval_pred
    predictions = np.argmax(logits, axis=-1)  # Convert logits to predicted class
    return accuracy_metric.compute(predictions=predictions, references=labels)


def prep_data(tokenizer):
    train_comments, val_comments, test_comments, test_labels = load_and_process_comments(
        train_path='train',
        batch_size=50,
    )
    # Flatten train_comments
    train_texts = [text for batch in train_comments for text in batch[0]]
    train_labels = [label for batch in train_comments for label in batch[1]]
    # Flatten test_comments
    test_texts = [text for batch in test_comments for text in batch[0]]
    test_labels = [label for batch in test_comments for label in batch[1]]
    # Tokenize training and test data
    train_encodings = tokenizer(train_texts, truncation=True, padding=True, max_length=512)
    test_encodings = tokenizer(test_texts, truncation=True, padding=True, max_length=512)
    # Create dataset objects
    train_dataset = CommentsDataset(train_encodings, train_labels)
    test_dataset = CommentsDataset(test_encodings, test_labels)
    return train_dataset, test_dataset

def train_model(model: str, saved_model: str, evaluation_results: str):
    tokenizer = AutoTokenizer.from_pretrained(model)
    model_new = AutoModelForSequenceClassification.from_pretrained(
        model, 
        num_labels=2  # Adjust `num_labels` based on your dataset (e.g., binary classification)
    )
    model_new.to(device)
    train_dataset, test_dataset = prep_data(tokenizer)

    training_args = TrainingArguments(
        output_dir="./results",          # Directory to save the model
        evaluation_strategy="epoch",    # Evaluate after each epoch
        learning_rate=2e-5,             # Learning rate
        per_device_train_batch_size=16, # Batch size for training
        per_device_eval_batch_size=16,  # Batch size for evaluation
        num_train_epochs=3,             # Number of epochs
        weight_decay=0.01,              # Weight decay
        logging_dir="./logs",           # Directory for logs
        logging_steps=10,               # Log every 10 steps
        save_strategy="epoch",          # Save checkpoint each epoch
        load_best_model_at_end=True,    # Load best model at the end of training
    )

    trainer = Trainer(
        model=model_new,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=test_dataset,
        tokenizer=tokenizer,
        compute_metrics=compute_metrics,
    )
    trainer.train()
    trainer.save_model(f"{saved_model}.pt")
    # evaluate the model
    results = trainer.evaluate()
    # save the evaluation results
    df = pd.DataFrame([results])
    df.to_csv(f"{evaluation_results}.csv", index=False)

def load_model_from_checkpoint(checkpoint_path: str):
    """
    Loads a trained model and tokenizer from a specific checkpoint.

    Args:
        checkpoint_path (str): Path to the checkpoint directory.

    Returns:
        model (torch.nn.Module): Loaded model ready for inference.
        tokenizer (AutoTokenizer): Tokenizer associated with the model.
    """
    print(f"Loading model from checkpoint: {checkpoint_path}")

    # Load model
    model = AutoModelForSequenceClassification.from_pretrained(checkpoint_path)
    model.to(device)  # Move to GPU if available

    # Load tokenizer
    tokenizer = AutoTokenizer.from_pretrained(checkpoint_path)

    return model, tokenizer

def eval_model(path: str, evaluation_results: str):
    model, tokenizer = load_model_from_checkpoint(path)
    _, test_dataset = prep_data(tokenizer)
    trainer = Trainer(
        model=model,
        tokenizer=tokenizer,
        compute_metrics=compute_metrics,
    )
    results = trainer.evaluate(test_dataset)
    # Save results to CSV
    df = pd.DataFrame([results])
    df.to_csv(f"{evaluation_results}.csv", index=False)

def eval_onnx_model(onnx_path: str, evaluation_results: str):
    """
    Evaluates an ONNX model's performance on a test dataset.

    Args:
        onnx_path (str): Path to the ONNX model file.
        evaluation_results (str): Path to save the evaluation results CSV.
    """
    # Load the ONNX model
    onnx_model = onnx.load(onnx_path)
    onnx.checker.check_model(onnx_model)

    # Initialize ONNX Runtime session
    ort_session = ort.InferenceSession(onnx_path)

    # Load tokenizer
    tokenizer = AutoTokenizer.from_pretrained('distilbert-base-uncased')

    # Prepare test data
    _, test_dataset = prep_data(tokenizer)
    test_loader = torch.utils.data.DataLoader(test_dataset, batch_size=16, shuffle=False)

    all_labels = []
    all_predictions = []

    # Iterate over the test data
    for batch in test_loader:
        input_ids = batch['input_ids'].numpy()
        attention_mask = batch['attention_mask'].numpy()
        labels = batch['labels'].numpy()

        # Run inference
        ort_inputs = {
            'input_ids': input_ids,
            'attention_mask': attention_mask
        }
        ort_outs = ort_session.run(None, ort_inputs)
        logits = ort_outs[0]

        # Get predictions
        predictions = np.argmax(logits, axis=1)

        all_labels.extend(labels)
        all_predictions.extend(predictions)

    # Compute accuracy
    accuracy = accuracy_score(all_labels, all_predictions)

    # Save results to CSV
    results = {'accuracy': [accuracy]}
    df = pd.DataFrame(results)
    df.to_csv(evaluation_results, index=False)

    print(f"Model evaluation completed. Accuracy: {accuracy:.4f}")
    print(f"Results saved to {evaluation_results}")



def to_onnx_model(path_from: str, onnx_path: str, quantized_onnx_path: str = None):
    """
    Converts a trained Hugging Face model checkpoint to ONNX format using a batch of inputs.

    Args:
        path_from (str): Path to the checkpoint directory.
        onnx_path (str): Path where the ONNX model should be saved.
    """
    # Load model and tokenizer from checkpoint
    model = AutoModelForSequenceClassification.from_pretrained(path_from)
    tokenizer = AutoTokenizer.from_pretrained(path_from)

    if torch.cuda.is_available():
        model.to("cuda")
    else:
        # Move model to CPU, because mac doesn't support ONNX with MPS
        model.to("cpu")
    model.eval()  # Set the model to evaluation mode

    # Prepare data
    train_dataset, _ = prep_data(tokenizer)
    # increase it if you can
    batch_size = 50
    train_loader = torch.utils.data.DataLoader(train_dataset, batch_size=batch_size, shuffle=False)
    batch = next(iter(train_loader))

    # Extract input_ids and attention_mask
    input_ids = batch['input_ids']
    attention_mask = batch['attention_mask']
    # prune the model
    apply_pruning(model, amount=0.15)
    # Export the model to ONNX
    torch.onnx.export(
        model,  # Model being run
        (input_ids, attention_mask),  # Model inputs as a tuple
        onnx_path,  # Where to save the model
        export_params=True,  # Store the trained parameter weights inside the model file
        opset_version=14,  # ONNX version to export the model to
        do_constant_folding=True,  # Whether to execute constant folding for optimization
        input_names=["input_ids", "attention_mask"],  # The model's input names
        output_names=["output"],  # The model's output name
        dynamic_axes={
            "input_ids": {0: "batch_size"},  # Variable length axes
            "attention_mask": {0: "batch_size"},
            "output": {0: "batch_size"},
        },
    )
    print(f"✅ Model successfully exported to ONNX format at: {onnx_path}")

    # Load the ONNX model
    onnx_model = onnx.load(onnx_path)

    # Apply dynamic quantization to the ONNX model
    quantize_dynamic(
        model_input=onnx_model,
        model_output=quantized_onnx_path,
        weight_type=QuantType.QInt8,
    )
    print(f"✅ Quantized ONNX model saved at: {quantized_onnx_path}")

def apply_pruning(model, amount=0.2):
    """
    Apply global unstructured pruning to the model.

    Args:
        model (nn.Module): The neural network model to be pruned.
        amount (float): The proportion of connections to prune (0 < amount < 1).
    """
    parameters_to_prune = []
    for name, module in model.named_modules():
        if isinstance(module, torch.nn.Linear):
            parameters_to_prune.append((module, 'weight'))

    # Apply global pruning
    prune.global_unstructured(
        parameters_to_prune,
        pruning_method=prune.L1Unstructured,
        amount=amount,
    )

    # Remove pruning reparameterization to maintain sparsity
    for module, _ in parameters_to_prune:
        prune.remove(module, 'weight')

# This was is the is best text with spellinng mistakes
# eval_model('./output/distilbert-base-uncased/checkpoint-5625', './results/evaluation_results_distilbert-base-uncased')
# to_onnx_model('./output/distilbert-base-uncased/checkpoint-5625', './results/distilbert-base-uncased.onnx')