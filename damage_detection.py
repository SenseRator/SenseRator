#!/usr/bin/env python3
import os
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset
from torchvision import transforms
import cv2
from unet.unet_model import UNet
from video_display import Display

# Constants
WIDTH = 1920 // 2
HEIGHT = 1080 // 2
VIDEO_PATH = "test.mp4"

# Model Initialization
model = UNet()
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)


def process_frame(img):
    img = cv2.resize(img, (WIDTH, HEIGHT))
    
    # Convert the image to PyTorch Tensor
    input_tensor = transforms.ToTensor()(img).unsqueeze(0)
    
    # Run the segmentation model
    with torch.no_grad():
        output = model(input_tensor)
    
    # Generate the mask
    mask = torch.argmax(output.squeeze(), dim=0).detach().cpu().numpy()
    
    # Create a color map for the mask and overlay it on the original image
    mask_colored = cv2.applyColorMap(mask, cv2.COLORMAP_JET)
    overlay = cv2.addWeighted(img, 0.6, mask_colored, 0.4, 0)
    
    disp.paint(overlay)


if __name__ == "__main__":
    cap = cv2.VideoCapture(VIDEO_PATH)

    if not cap.isOpened():
        print(f"Error: Couldn't open the video file {VIDEO_PATH}")
        exit(1)

    disp = Display(WIDTH, HEIGHT)

    while cap.isOpened():
        ret, frame = cap.read()
        if ret:
            process_frame(frame)
        else:
            break

    cap.release()
    disp.close()
