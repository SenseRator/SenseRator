import os
from torch.utils.data import Dataset
import cv2

class CamVidDataset(Dataset):
    def __init__(self, image_dir, mask_dir, transform=None):
        self.image_dir = image_dir
        self.mask_dir = mask_dir
        self.transform = transform
        self.images = os.listdir(image_dir)

    def __len__(self):
        return len(self.images)

    def __getitem__(self, index):
        img_filename = self.images[index]
        mask_filename = img_filename[:-4] + "_L" + img_filename[-4:]  # Add '_L' before the file extension

        img_path = os.path.join(self.image_dir, img_filename)
        mask_path = os.path.join(self.mask_dir, mask_filename)
        
        # Debug
        # print(f"Attempting to read {img_path} and {mask_path}")  # Debugging statement

        image = cv2.imread(img_path)
        mask = cv2.imread(mask_path, 0)
        
        if image is None:
            raise FileNotFoundError(f"Image at {img_path} could not be found or read.")
            
        if mask is None:
            raise FileNotFoundError(f"Mask at {mask_path} could not be found or read.")

        if self.transform is not None:
            image = self.transform(image)
            mask = self.transform(mask)

        return image, mask
