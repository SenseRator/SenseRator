import torch
import cv2
import logging
import albumentations as A
from torch.utils.data import DataLoader
from torchmetrics.detection import MeanAveragePrecision
from dataset import LocalCarImageDataset, collate, load_annotations
from .model import create_deeplabv3, get_optimizer, get_loss, get_binary
from torch.profiler import profile, ProfilerActivity
from torch.utils.data import Subset
    
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def train_model(train_dataset, device, n_epoch=50):
    # Debug
    print(f"Number of samples in the dataset: {len(train_dataset)}")
    # Prepare DataLoader
    train_loader = DataLoader(train_dataset, batch_size=11, shuffle=True, collate_fn=collate, num_workers=2)
    
    # Prepare model, optimizer, and loss function
    model = create_deeplabv3(output_channels=32)
    model = model.to(device)
    model.train()
    optimizer = get_optimizer(model)
    loss_function = get_loss()

    # Training loop
    for e in range(n_epoch):
        cur_loss = 0
        train_gen = iter(train_loader)
        train_map = MeanAveragePrecision(iou_type="segm")

        for imgs_x,imgs_y in train_gen:
            # Debug
            # print(f"Shape of images (should be [N, C, H, W]): {torch.stack(imgs_x).shape}")
            # print(f"Shape of labels (should be [N, H, W]): {torch.stack(imgs_y).shape}")  
            optimizer.zero_grad()  # Reset gradients
            # Input
            x = torch.stack(imgs_x).to(device)
            y_train = torch.stack(imgs_y).to(device)

            # Train
            y_pred = model(x)  # Forward pass

            l1 = loss_function(y_pred['out'], y_train)
            l2 = loss_function(y_pred['aux'], y_train)
            l = 0.3 * l2 + l1

            # No gradient calculation needed for metric computation and logging
            with torch.no_grad():
                cur_loss += l.item()
                y_pred = y_pred['out']
                ytrain = y_train

                masks_pred,masks_true = [],[]
                for i in range(y_pred.shape[0]):
                    masks_pred.append({
                        "masks": get_binary(y_train[i]),
                        "labels": torch.tensor(list(range(32))),
                        "scores": torch.ones(32)
                    })
                    masks_true.append({
                        "masks": get_binary(y_pred[i]),
                        "labels": torch.tensor(list(range(32))),
                        "scores": torch.ones(32)
                    }) 
                res = train_map(masks_pred,masks_true)

            l.backward()  # Backpropagation
            optimizer.step()  # Update weights

            # Log current loss and mean average precision
            # print(f"Epoch [{e}] - Loss: {cur_loss} - MAP: {train_map.compute()}")
        logger.info(f"Epoch [{e}] - Loss: {cur_loss} - MAP: {train_map.compute()}")
    
    # Return Model
    return model



if __name__ == '__main__':
    # Load annotations
    X_train_annot, y_train_annot = load_annotations(
        './data/train',
        '{}_L.{}'  # Pattern to convert X to Y
    )

    # # Define the albumentations transforms for augmenting the images.
    x_transform = A.Compose([
        A.RandomBrightnessContrast(p=0.5),
        A.GridDistortion(p=0.5),
        A.Downscale(scale_min=0.25, scale_max=0.25, interpolation=cv2.INTER_LINEAR, p=0.5)
    ])

    # # Define the albumentations transform for the additional augmentations.
    transform = A.Compose([
        A.HorizontalFlip(p=0.3),
        A.Rotate(limit=30, p=0.3)
    ], is_check_shapes=False)

    # For the training dataset, apply transformations
    train_dataset = LocalCarImageDataset(
        X_train_annot, y_train_annot,
        "./data/train",
        "./data/transformed_images/train",
        x_transform=x_transform,
        transform=transform
    )

    # Define device
    device = torch.device("cuda")

    # Start training
    model = train_model(train_dataset, device)

    # Save Model
    torch.save(model.state_dict(), "deeplabv3_model.pt")
