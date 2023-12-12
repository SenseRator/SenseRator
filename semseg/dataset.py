import os
import pandas as pd
import torch
from torchvision.io import read_image
from torchvision.transforms import Normalize
from torch.utils.data import Dataset

def load_annotations(x_dir, x_to_y_pattern):
    """
    Loads annotations for images and labels from the given directory.

    Parameters:
    x_dir (str): The path to the directory containing input image files.
    x_to_y_pattern (str): The pattern to transform X filenames into Y filenames.

    Returns:
    Tuple[pd.Series, pd.Series]: The image and label annotations as Pandas Series.
    """
    X_annot = []
    for dirname, _, filenames in os.walk(x_dir):
        for filename in filenames:
            X_annot.append(filename)
    
    # Transform X filenames into Y filenames based on the provided pattern
    y_annot = pd.Series([x_to_y_pattern.format(x.split('.')[0], x.split('.')[1]) for x in X_annot])

    return pd.Series(X_annot), y_annot


# Collates a batch of data. 
def collate(batch):
    """
    Collates a batch of data.

    This function is called by the DataLoader to combine individual data samples into a batch. It separates the
    image and label pairs for each sample in the batch into two lists, one for images and one for labels.

    Parameters:
    batch (list): A list of tuples where each tuple is a pair of an image and a label.

    Returns:
    Tuple[List, List]: A tuple containing two lists: one with all the images, and one with all the labels.
    """
    data_x = [] # This array contains all images.
    data_y = [] # This array contains all labels. 
    for i in range(len(batch)):
        data_x.append(batch[i][0])
        data_y.append(batch[i][1])
    return data_x,data_y

# Define the custom dataset class
class LocalCarImageDataset(Dataset):
    """
    A dataset class for loading and transforming images for semantic segmentation using PyTorch.

    Attributes:
        img_dir (str): Directory path where input images are stored.
        y_label_dir (str): Directory path where label images are stored.
        annotations (pd.Series): Annotations for the input images.
        y_annotations (pd.Series): Annotations for the label images.
        transform (callable, optional): A function/transform that takes in an image and returns a transformed version.
        target_transform (callable, optional): A function/transform that takes in a target and returns a transformed version.
    """
    def __init__(self, annotations, y_annotations, img_dir, y_label_dir,
                 x_transform=None, transform=None, target_transform=None):
        self.img_dir = img_dir
        self.y_label_dir = y_label_dir
        self.annotations = annotations
        self.y_annotations = y_annotations
        self.transform = transform
        self.target_transform = target_transform
        self.x_transform = x_transform
        
        # Load the label color mappings once at initialization
        self.label_colors = pd.read_csv("./data/class_dict.csv").reset_index()
        self.label_colors.set_index(["r", "g", "b"], inplace=True)
        self.labels_map = {tuple(k): v for k, v in self.label_colors.to_dict()['index'].items()}

        if self.annotations.empty:
            raise ValueError("No annotations found. Check the provided annotations file or directory.")
        if self.y_annotations.empty:
            raise ValueError("No label annotations found. Check the provided label annotations file or directory.")

    def __len__(self):
        return len(self.annotations)

    # Convert color-coded label image into single channel image where erach pixel's value corresponds to a class index. 
    def process_y(self, img):
        # Convert RGB image to class indexes using the mapping
        img = img.permute(1, 2, 0).to(torch.int)
        h, w, _ = img.shape
        class_idx_map = torch.zeros((h, w), dtype=torch.long)

        # Convert the RGB values to class indexes
        for rgb, idx in self.labels_map.items():
            mask = torch.all(img == torch.tensor(rgb, dtype=torch.int), dim=-1)
            class_idx_map[mask] = torch.tensor(idx)

        # One-hot encode the class indexes
        dest = torch.nn.functional.one_hot(class_idx_map, num_classes=len(self.labels_map)).permute(2, 0, 1).to(torch.float32)
        
        return dest


    # Working but slow
    def __getitem__(self, idx):
        img_path = os.path.join(self.img_dir, self.annotations.iloc[idx])
        image_x = read_image(img_path).float() / 255.0

        y_path = os.path.join(self.y_label_dir, self.y_annotations.iloc[idx])
        image_y = torch.load(y_path)

        image_x,image_y = image_x.permute(1,2,0),image_y.permute(1,2,0)
        if self.x_transform:
            transformed = self.x_transform(image=image_x.numpy())
            image_x = torch.from_numpy(transformed['image'])
        if self.transform:
            # Convert mask to numpy array and ensure it is in the correct shape
            transformed = self.transform(image=image_x.numpy(), mask=image_y.numpy())
            image_x = torch.from_numpy(transformed['image'])
            image_y = torch.from_numpy(transformed['mask'])

        image_x,image_y = image_x.permute(2,0,1),image_y.permute(2,0,1)
        norm = Normalize(mean=(0.485, 0.456, 0.406), std=(0.229, 0.224, 0.225))
        image_x = norm(image_x)
        image_y_index = self.process_y(image_y)
        # Debug
        # print(f"Returning {image_x.shape} and {image_y_index.shape}")
        return image_x, image_y_index