import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import transforms
from unet.unet_model import UNet
from dataset.camvid_dataset import CamVidDataset
from torch.utils.tensorboard import SummaryWriter

# Data Loading
transform = transforms.Compose([
    transforms.ToTensor(),
])

train_dataset = CamVidDataset(image_dir='data/camvid/images', mask_dir='data/camvid/labels', transform=transform)
train_loader = DataLoader(train_dataset, batch_size=4, shuffle=True)


# Initialize model, loss, optimizer
model = UNet()
criterion = nn.BCEWithLogitsLoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)

# Initialize SummaryWriter
writer = SummaryWriter('runs/experiment_1')

# Training loop
num_epochs = 10
for epoch in range(num_epochs):
    for batch_idx, (data, target) in enumerate(train_loader):
        optimizer.zero_grad()
        output = model(data)
        loss = criterion(output, target)
        loss.backward()
        optimizer.step()
        
        print(f"Epoch [{epoch+1}/{num_epochs}], Step [{batch_idx+1}/{len(train_loader)}], Loss: {loss.item():.4f}")
