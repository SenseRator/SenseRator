import torch
import numpy as np
from torchvision.io import read_image
from torchvision.transforms import Normalize, Resize, Compose
import matplotlib.pyplot as plt
from .model import create_deeplabv3
import pandas as pd
import cv2
from PIL import Image
from utils.file_utils import join_paths, make_directory

def invert_y(mask, index_to_rgb):
    h, w = mask.shape
    rgb_image = np.zeros((h, w, 3), dtype=np.uint8)
    
    for class_index, rgb in index_to_rgb.items():
        mask_indices = mask == class_index
        rgb_image[mask_indices] = rgb

    return rgb_image

def calculate_centroid(contour):
    M = cv2.moments(contour)
    if M['m00'] == 0:
        return None
    return (int(M['m10'] / M['m00']), int(M['m01'] / M['m00']))

def draw_labels_on_mask(mask, labels_df, class_colors):
    # Initialize an empty image with 3 channels
    labeled_mask = np.zeros((mask.shape[0], mask.shape[1], 3), dtype=np.uint8)

    # Draw labels on the mask
    for class_index in np.unique(mask):
        # Skip the background
        if class_index == 0:
            continue
        
        # Extract the mask for the current class
        class_mask = (mask == class_index).astype(np.uint8)

        # Find the contours of the class region
        contours, _ = cv2.findContours(class_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Calculate the centroid and draw the label for each contour
        for contour in contours:
            M = cv2.moments(contour)
            if M["m00"] > 0:
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])
                
                # Get the class name
                class_name = labels_df[labels_df['index'] == class_index]['name'].values[0]

                # Set the position for the text
                text_pos = (cX - 10, cY)

                # Set the color for the text
                text_color = class_colors[class_index]

                # Draw the text on the mask
                cv2.putText(labeled_mask, class_name, text_pos, cv2.FONT_HERSHEY_SIMPLEX, .7, text_color, 1)

    # Make sure the mask is contiguous
    labeled_mask = np.ascontiguousarray(labeled_mask, dtype=np.uint8)
    
    return labeled_mask

def segment(filename, folder, model): 
    # Directory to load images from and save masks to
    input_dir = folder
    output_dir = folder[:len(folder)-3]+"processed_masks"
    make_directory(output_dir, exist_ok=True)

    # Define our labels
    labels_df = pd.read_csv("./data/class_dict.csv")
    labels_df['index'] = range(len(labels_df))  # Add an index column
    index_to_rgb = {index: [r, g, b] for index, r, g, b in zip(labels_df.index, labels_df['r'], labels_df['g'], labels_df['b'])}

    # Read in a frame (filename) from the input directory
    if filename.endswith('.jpg'):  # Check if the file is a JPEG image
        file_path = join_paths(input_dir, filename)

        # Load and preprocess the input image
        input_image = read_image(file_path).float() / 255.0

        # Resize and normalize the input image
        transform = Compose([
            Resize((720, 960)),  # Resize to the expected input dimensions
            Normalize(mean=(0.485, 0.456, 0.406), std=(0.229, 0.224, 0.225))
        ])

        input_image = transform(input_image)

        # Add a batch dimension and send the image to the model
        input_image = input_image.unsqueeze(0)
        with torch.no_grad():
            output_mask = model(input_image)['out'][0]

        # Convert the output mask to class indices and then to a color mask
        output_mask_class_indices = output_mask.argmax(0).to('cpu') 
        predicted_mask_rgb = invert_y(output_mask_class_indices, index_to_rgb)
        class_colors = {index: (int(b), int(g), int(r)) for index, r, g, b in zip(labels_df.index, labels_df['r'], labels_df['g'], labels_df['b'])}

        # Overlay labels on the segmentation mask
        labeled_mask = draw_labels_on_mask(output_mask_class_indices.numpy(), labels_df, class_colors)

        # Combine the labeled mask with the color mask for visualization
        combined_mask = cv2.addWeighted(predicted_mask_rgb.astype(np.uint8), 0.5, labeled_mask, 0.5, 0)

        # Save the combined mask
        save_path = join_paths(output_dir, f'SemSeg_{filename}')
        Image.fromarray(combined_mask).save(save_path)

        print(f"Mask {save_path} processed and saved.")

        # Return the parth of the saved mask.
        return save_path

    # Handle the case where thef ilename is not a .jpg
    return None