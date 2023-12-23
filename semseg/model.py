"""
This Python script is dedicated to the setup and utility functions for a Deep Learning semantic segmentation model, specifically using a modified DeepLabV3 with a MobileNet backbone. Key functionalities include:

1. init_semseg_model: Initializes and loads a pre-trained semantic segmentation model for evaluation, adjusting its output channels to match the number of classes as defined in a provided CSV file.

2. create_deeplabv3: Constructs a customized DeepLabV3 model with a specified number of output channels, suitable for semantic segmentation tasks. It includes modifications to the model's auxiliary and main classifiers and manages layer-wise freezing for training.

3. get_optimizer: Provides an optimizer (Adam) for the model, useful in the training process.

4. get_loss: Returns a CrossEntropyLoss function, commonly used for segmentation tasks.

5. get_binary: Converts the model's multi-class segmentation output into a binary mask, useful for post-processing and evaluation.

6. invert_y: Transforms the model's output from class indices to an RGB format for visual inspection, aiding in understanding and analyzing the model's predictions.

The script is focused on the aspects of model initialization, customization for specific tasks, and utilities for processing and visualizing the model's outputs.
"""
import os
import pandas as pd
import torch
import torchvision
import numpy as np
from torchmetrics.detection.mean_ap import MeanAveragePrecision

# Function to initalize the semseg model and put into eval mode. 
def init_semseg_model(filepath):
    """
    Initializes and loads a semantic segmentation model from a given file path.

    This function loads the model state from a specified file path and configures the model for evaluation. It also 
    reads class labels from a CSV file and adjusts the model's output channels to match the number of classes.

    Parameters:
        filepath (str): The file path where the model's state dictionary is stored.

    Returns:
        torch.nn.Module: The loaded and initialized semantic segmentation model in evaluation mode.
    """
    # Define our labels
    labels_df = pd.read_csv("./data/class_dict.csv")
    labels_df['index'] = range(len(labels_df))  # Add an index column

    # Load the trained SemSeg model
    seg_model = create_deeplabv3(output_channels=len(labels_df))
    # Set Model path
    seg_model_path = os.path.join(os.path.dirname(__file__), 'deeplabv3_model.pt')
    # Load State_dict
    seg_state_dict = torch.load(seg_model_path, map_location='cuda' if torch.cuda.is_available() else 'cpu')
    seg_model.load_state_dict(seg_state_dict)
    # Set device
    seg_model = seg_model.to('cuda' if torch.cuda.is_available() else 'cpu')
    seg_model.eval()
    
    return seg_model

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
    """
    Creates and returns an optimizer for the given model.

    This function currently returns an Adam optimizer that can be used to optimize the provided model's parameters.

    Parameters:
        model (torch.nn.Module): The model for which the optimizer is to be created.

    Returns:
        torch.optim.Optimizer: An Adam optimizer configured for the model.
    """
    return torch.optim.Adam(params=model.parameters())

# Function to get the loss function
def get_loss():
    """
    Returns a loss function suitable for a segmentation task.

    This function provides a CrossEntropyLoss function, commonly used for multi-class segmentation tasks.

    Returns:
        torch.nn.modules.loss.CrossEntropyLoss: The CrossEntropy loss function.
    """
    return torch.nn.CrossEntropyLoss()

# Convert model outputs to binary masks
def get_binary(mask):
    """
    Converts a multi-class segmentation mask to a binary mask.

    This function processes a tensor representing class predictions for each pixel and converts it into a binary mask,
    indicating the most likely class for each pixel.

    Parameters:
        mask (torch.Tensor): A tensor of shape (num_classes, H, W) representing class predictions for each pixel.

    Returns:
        torch.Tensor: A binary mask of shape (1, H, W) where each pixel is 1 if it belongs to the most likely class, else 0.
    """
    binary_mask = torch.zeros_like(mask)

    max_values, max_indices = torch.max(mask, dim=0, keepdim=True)
    binary_mask[max_indices, torch.arange(mask.size(1)).view(-1, 1), torch.arange(mask.size(2))] = 1
    return binary_mask.bool()

#  Transform model predictions into a visually inspectable format.
def invert_y(img, labels):
    """
    Transforms model predictions into a visually inspectable RGB format.

    This function converts class indices in the model's output to corresponding RGB values using a provided label mapping.
    It's useful for visualizing the model's predictions.

    Parameters:
        img (torch.Tensor): The output tensor from the model, containing class indices for each pixel.
        labels (pd.DataFrame): A DataFrame containing the RGB values for each class index.

    Returns:
        numpy.ndarray: An RGB image representing the model's predictions.
    """
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
