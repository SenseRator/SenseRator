import torch
import torchvision
import numpy as np
from torchmetrics.detection.mean_ap import MeanAveragePrecision

# Function to modify the DeepLabV3 model to fit the number of classes in the dataset
def create_deeplabv3(output_channels=32):
    """
    Creates a modified DeepLabV3 model with a MobileNet backbone tailored for a specified number of output channels.

    Parameters:
        output_channels (int): The number of output channels (classes) for the final classification layer.

    Returns:
        model (torch.nn.Module): The modified DeepLabV3 model ready for training or inference.
    """
    model = torch.hub.load('pytorch/vision:v0.10.0', 'deeplabv3_mobilenet_v3_large', weights=torchvision.models.segmentation.DeepLabV3_MobileNet_V3_Large_Weights.DEFAULT)
    
    # Modify the auxiliary classifier
    model.aux_classifier[4] = torch.nn.Conv2d(output_channels, output_channels, kernel_size=(1, 1), stride=(1, 1))
    model.aux_classifier[0] = torch.nn.Conv2d(40, output_channels, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), bias=False)
    model.aux_classifier[1] = torch.nn.BatchNorm2d(output_channels, eps=1e-05, momentum=0.1, affine=True, track_running_stats=True)
    
    # Modify the main classifier
    model.classifier[4] = torch.nn.Conv2d(256, output_channels, kernel_size=(1, 1), stride=(1, 1))
    
    # Freeze layers
    for param in model.parameters():
        param.requires_grad = False
    # Unfreeze some layers for training
    for param in model.backbone['14'].parameters():
        param.requires_grad = True
    # ... repeat for other layers to unfreeze ...
    for param in model.backbone['15'].parameters():
        param.requires_grad = True
    for param in model.backbone['16'].parameters():
        param.requires_grad = True
    for param in model.classifier.parameters():
        param.requires_grad = True
    for param in model.aux_classifier.parameters():
        param.requires_grad = True

    return model

# Function to get the optimizer
def get_optimizer(model):
    return torch.optim.Adam(params=model.parameters())

# Function to get the loss function
def get_loss():
    return torch.nn.CrossEntropyLoss()

# Convert model outputs to binary masks
def get_binary(mask):
    binary_mask = torch.zeros_like(mask)

    max_values, max_indices = torch.max(mask, dim=0, keepdim=True)
    binary_mask[max_indices, torch.arange(mask.size(1)).view(-1, 1), torch.arange(mask.size(2))] = 1
    return binary_mask.bool()

#  Transform model predictions into a visually inspectable format.
def invert_y(img, labels):
    # Convert the index to a column if not already done
    if 'index' not in labels.columns:
        labels = labels.reset_index()

    # Create a mapping from index to RGB
    index_to_rgb = labels[['r', 'g', 'b']].values

    # Get the class index for each pixel
    class_indices = img.argmax(2).numpy()

    # Map the class indices to RGB values
    rgb_image = np.take(index_to_rgb, class_indices, axis=0)
    return rgb_image
