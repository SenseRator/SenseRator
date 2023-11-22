import os
import torch
from torchvision.io import read_image
from dataset import load_annotations

class ProcessImageDataSet(Dataset):
    def __init__(self, annotations,y_annotations, img_dir,y_label_dir, dataset_type, transform=None, target_transform=None):
        self.img_dir = img_dir
        self.y_label_dir = y_label_dir
        self.annotations = annotations
        self.y_annotations = y_annotations
        self.dataset_type = dataset_type  # 'train' or 'val'
        self.transform = transform
        self.target_transform = target_transform
        
        # Ensure the directory for saving transformed train images exists
        transformed_img_dir = "./data/transformed_images/train/"
        os.makedirs(transformed_img_dir, exist_ok=True)  # Use exist_ok to avoid error if the directory exists

        # Ensure the directory for saving transformed val images exists
        transformed_img_dir = "./data/transformed_images/val/"
        os.makedirs(transformed_img_dir, exist_ok=True)  # Use exist_ok to avoid error if the directory exists

    def __len__(self):
        return len(self.annotations)

    def __getitem__(self, idx):
        img_path = os.path.join(self.img_dir, self.annotations.iloc[idx])
        y_path = os.path.join(self.y_label_dir, self.y_annotations.iloc[idx])
        image_x =  read_image(img_path) / 255
        image_y =  read_image(y_path)
        
        if self.transform:
            image_x = self.transform(image_x)
        if self.target_transform:
            image_y = self.target_transform(image_y)
        if self.dataset_type == 'train':
            pt = "./data/transformed_images/train/" + self.y_annotations.iloc[idx]
        elif self.dataset_type == 'val':
            pt = "./data/transformed_images/val/" + self.y_annotations.iloc[idx]
        else:
            raise ValueError("Invalid dataset type specified")
        try:
            torch.save(image_y.type(torch.ByteTensor),pt)
            print(f"Saved transformed label to {pt}")
        except:
            print(f"ERROR EXISTS while saving to {pt}: {e}")        
        
        return image_x, image_y.double()

if __name__ == '__main__':
    # Load annotations
    X_train_annot, y_train_annot = load_annotations(
        './data/train',
        '{}_L.{}'  # Pattern to convert X to Y
    )

    # Load Annotations
    X_valid_annot, y_valid_annot = load_annotations(
        './data/val',
        '{}_L.{}'  # Pattern to convert X to Y
    )

    # For the training dataset, apply transformations
    preprocess_dataset = ProcessImageDataSet(
        X_train_annot, y_train_annot,
        "./data/train",
        "./data/train_labels",
        'train',
    )

    # For the validation dataset, apply transformations
    preprocess_dataset = ProcessImageDataSet(
        X_valid_annot, y_valid_annot,
        "./data/val",
        "./data/val_labels",
        'val',
    )
    
    # # Process and save each image
    for idx in range(len(preprocess_dataset)):
        image, label = preprocess_dataset[idx]