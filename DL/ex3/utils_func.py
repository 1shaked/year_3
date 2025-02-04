import torch
import torch.nn as nn
from torchvision import datasets, transforms
from torch.utils.data import DataLoader, random_split
import torch.nn.functional as F
import torchvision.models as models



def get_data_loaders(batch_size=64, train_split=0.8):
    # Define transforms
    train_transform = transforms.Compose([
        transforms.Resize((64, 64)),
        transforms.RandomHorizontalFlip(),
        transforms.RandomRotation(15),
        transforms.ToTensor(),
    ])

    test_transform = transforms.Compose([
        transforms.Resize((64, 64)),
        transforms.CenterCrop(64),
        transforms.ToTensor(),
    ])

    # Load datasets
    train_dataset = datasets.STL10(root="./data", split="train", download=True, transform=train_transform)
    test_dataset = datasets.STL10(root="./data", split="test", download=True, transform=test_transform)

    # Train/Validation split
    train_size = int(train_split * len(train_dataset))
    val_size = len(train_dataset) - train_size
    train_dataset, val_dataset = random_split(train_dataset, [train_size, val_size])

    # Data loaders
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)

    return train_loader, val_loader, test_loader


class LogisticRegression(nn.Module):
    def __init__(self, input_size, num_classes):
        super(LogisticRegression, self).__init__()
        self.linear = nn.Linear(input_size, num_classes)

    def forward(self, x):
        x = x.view(x.size(0), -1)
        out = self.linear(x)
        return out
    

class FullyConnected(nn.Module):
    def __init__(self, input_size, hidden_size_l1,hidden_size_l2 , num_classes, dropout=0.5):
        super(FullyConnected, self).__init__()
        self.fc1 = nn.Linear(input_size, hidden_size_l1)
        self.bn1 = nn.BatchNorm1d(hidden_size_l1)
        self.dropout1 = nn.Dropout(dropout)  # Dropout after first layer
        self.fc2 = nn.Linear(hidden_size_l1, hidden_size_l2)
        self.bn2 = nn.BatchNorm1d(hidden_size_l2)
        self.dropout2 = nn.Dropout(dropout)  # Dropout after second layer
        self.fc3 = nn.Linear(hidden_size_l2 , num_classes)



    def forward(self, x):
        x = x.view(x.size(0), -1)
        out = self.fc1(x)
        out = self.bn1(out)
        out = nn.Tanh()(out)
        out = self.dropout1(out)
        out = self.fc2(out)
        out = self.bn2(out)
        out = nn.Tanh()(out)
        out = self.fc3(out)
        return out


def train_model(model, num_epochs=10, device="cpu",learning_rate=0.01,weight_decay=0.0, batch_size=64 ):
    train_loader, val_loader, test_loader = get_data_loaders(batch_size)
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate, weight_decay=weight_decay)
    train_losses, val_losses = [], []
    train_accuracies, val_accuracies = [], []
    for epoch in range(num_epochs):
        # Training phase
        model.train()
        train_loss, train_correct = 0, 0

        for inputs, targets in train_loader:
            inputs, targets = inputs.to(device), targets.to(device)
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, targets)
            loss.backward()
            optimizer.step()

            train_loss += loss.item()
            train_correct += (outputs.argmax(1) == targets).sum().item()

        train_acc = train_correct / len(train_loader.dataset)
        train_losses.append(train_loss)
        train_accuracies.append(train_acc)
        print(f"Epoch {epoch+1}: Train Loss={train_loss:.4f}, Train Accuracy={train_acc:.4f}")

        # Validation phase
        model.eval()
        val_loss, val_correct = 0, 0
        with torch.no_grad():
            for inputs, targets in val_loader:
                inputs, targets = inputs.to(device), targets.to(device)
                outputs = model(inputs)
                loss = criterion(outputs, targets)
                val_loss += loss.item()
                val_correct += (outputs.argmax(1) == targets).sum().item()

        val_acc = val_correct / len(val_loader.dataset)
        val_losses.append(val_loss)
        val_accuracies.append(val_acc)
        print(f"Epoch {epoch+1}: Val Loss={val_loss:.4f}, Val Accuracy={val_acc:.4f}")
    return val_loss, val_acc, optimizer, train_losses, val_losses, train_accuracies, val_accuracies


def save_model(model,optimizer , file_path="model_checkpoint.pth", **kwargs):
    """Saves the model state and optimizer state to a file."""
    checkpoint = {
        "model_state_dict": model.state_dict(),  # Save model weights
        "optimizer_state_dict": optimizer.state_dict(),  # Save optimizer parameters
    }
    # add the **kwargs to save more parameters
    checkpoint.update(kwargs)
    torch.save(checkpoint, file_path)
    print(f"✅ Model saved to {file_path}")
def load_model(model, optimizer, file_path="model_checkpoint.pth", device="cpu"):
    """Loads a saved model and optimizer state from a file."""
    checkpoint = torch.load(file_path, map_location=device)  # Load on correct device

    model.load_state_dict(checkpoint["model_state_dict"])  # Load model weights
    optimizer.load_state_dict(checkpoint["optimizer_state_dict"])  # Load optimizer state
    epoch = checkpoint["epoch"]  # Get last trained epoch
    loss = checkpoint["loss"]  # Get last loss

    print(f"✅ Model loaded from {file_path}, resuming at epoch {epoch+1}")
    return model, optimizer, epoch, loss





class CNN(nn.Module):
    def __init__(self, num_classes=10, dropout_rate=0.5):
        super(CNN, self).__init__()

        # Convolutional Layer 1
        self.conv1 = nn.Conv2d(in_channels=3, out_channels=32, kernel_size=3, padding=1)  # Output: 32x64x64
        self.bn1 = nn.BatchNorm2d(32)  # Batch Normalization
        self.pool1 = nn.MaxPool2d(kernel_size=2, stride=2)  # Output: 32x32x32

        # Convolutional Layer 2
        self.conv2 = nn.Conv2d(in_channels=32, out_channels=64, kernel_size=3, padding=1)  # Output: 64x32x32
        self.bn2 = nn.BatchNorm2d(64)  # Batch Normalization
        self.pool2 = nn.MaxPool2d(kernel_size=2, stride=2)  # Output: 64x16x16

        # Fully Connected Layers
        self.fc1 = nn.Linear(64 * 16 * 16, 512)  # Flattened input size: 64 * 16 * 16 = 16384
        self.dropout1 = nn.Dropout(dropout_rate)

        self.fc2 = nn.Linear(512, 256)
        self.dropout2 = nn.Dropout(dropout_rate)

        # Classification Layer
        self.fc3 = nn.Linear(256, num_classes)

    def forward(self, x):
        x = self.pool1(F.relu(self.bn1(self.conv1(x))))  # Conv1 -> BatchNorm -> ReLU -> MaxPool
        x = self.pool2(F.relu(self.bn2(self.conv2(x))))  # Conv2 -> BatchNorm -> ReLU -> MaxPool

        x = x.view(x.size(0), -1)  # Flatten the tensor for FC layers

        x = F.relu(self.fc1(x))
        x = self.dropout1(x)

        x = F.relu(self.fc2(x))
        x = self.dropout2(x)

        x = self.fc3(x)  # Classification Layer (No activation, CrossEntropyLoss handles Softmax)
        return x




class MobileNetV2FeatureExtractor(nn.Module):
    def __init__(self, num_classes=10, dropout_rate=0.5):
        super(MobileNetV2FeatureExtractor, self).__init__()

        # Load pre-trained MobileNetV2 model
        self.mobilenet = models.mobilenet_v2(pretrained=True)

        # Freeze all layers (we don't want to update them)
        for param in self.mobilenet.features.parameters():
            param.requires_grad = False

        # Get the number of features from MobileNetV2 last conv layer
        num_features = self.mobilenet.last_channel  # 1280 for MobileNetV2

        # Define the new classification head
        self.task_head = nn.Sequential(
            nn.Linear(num_features, 512),  # FC1: Reduce to 512 neurons
            nn.ReLU(),
            nn.Dropout(dropout_rate),
            nn.Linear(512, 256),  # FC2: Reduce to 256 neurons
            nn.ReLU(),
            nn.Dropout(dropout_rate),
            nn.Linear(256, num_classes)  # Final Classification Layer
        )

    def forward(self, x):
        x = self.mobilenet.features(x)  # Extract features from MobileNetV2
        x = x.mean([2, 3])  # Global Average Pooling (GAP) → (batch_size, 1280)
        x = self.task_head(x)  # Pass through the fully connected task head
        return x


class MobileNetV2FineTuned(nn.Module):
    def __init__(self, num_classes=10, dropout_rate=0.5):
        super(MobileNetV2FineTuned, self).__init__()

        # Load pre-trained MobileNetV2 model
        self.mobilenet = models.mobilenet_v2(pretrained=True)

        # ✅ Unfreeze MobileNetV2 Layers → Train the entire model
        for param in self.mobilenet.parameters():
            param.requires_grad = True  # Make all layers trainable

        # Get the number of features from MobileNetV2 last conv layer
        num_features = self.mobilenet.last_channel  # 1280 for MobileNetV2

        # Define the new classification head
        self.task_head = nn.Sequential(
            nn.Linear(num_features, 512),  # FC1: Reduce to 512 neurons
            nn.ReLU(),
            nn.Dropout(dropout_rate),
            nn.Linear(512, 256),  # FC2: Reduce to 256 neurons
            nn.ReLU(),
            nn.Dropout(dropout_rate),
            nn.Linear(256, num_classes)  # Final Classification Layer
        )

    def forward(self, x):
        x = self.mobilenet.features(x)  # Extract features from MobileNetV2
        x = x.mean([2, 3])  # Global Average Pooling (GAP) → (batch_size, 1280)
        x = self.task_head(x)  # Pass through the fully connected task head
        return x