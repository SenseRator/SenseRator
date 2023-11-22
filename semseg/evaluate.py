import pandas as pd
import seaborn as sns
import torch
import logging
import random
import os
from torchmetrics.classification import MultilabelAccuracy,MulticlassConfusionMatrix
from torchmetrics.detection.mean_ap import MeanAveragePrecision
from dataset import LocalCarImageDataset, collate
from semseg.model import get_binary, invert_y, create_deeplabv3
from dataset import load_annotations
from matplotlib import pyplot as plt
from torch.utils.data import DataLoader


def evaluate_model(model, device, valid_loader, labels):
    # Prepare the model and set it to evaluation mode
    model = create_deeplabv3(output_channels=32)
    state_dict = torch.load("./deeplabv3_model.pt", map_location=torch.device('cpu'))
    device = torch.device("cuda" if torch.cuda.is_available() else 'cpu')
    model.to(device)
    model.load_state_dict(state_dict)
    model.eval()

    # Define the metrics
    val_acc = MultilabelAccuracy(num_labels=32)
    val_confmat = MulticlassConfusionMatrix(num_classes=32, normalize='true')
    valid_map = MeanAveragePrecision(iou_type="segm", class_metrics=True)

    # Define our labels
    labels = pd.read_csv("./data/class_dict.csv")

    # Create folder
    folder_name = 'evaluation_results'
    os.makedirs(folder_name, exist_ok=True)

    # Evaluation loop
    with torch.no_grad():
        for imgs_x, imgs_y in valid_loader:
            #Input 
            x = torch.stack(imgs_x)
            y_train = torch.stack(imgs_y)
            y_train=y_train.to(device)


            x=x.to(device)
            y_pred = model(x)["out"]
            
            
            val_acc(y_pred.to("cpu"),y_train.to("cpu"))

            cf = val_confmat(y_pred.permute(2,3,0,1).reshape(-1,32).argmax(1).to("cpu"),y_train.permute(2,3,0,1).reshape(-1,32).argmax(1).to("cpu"))
            a,b = y_pred,imgs_y
            masks_pred,masks_true = [],[]
            
            for i in range(y_pred.shape[0]):
                masks_pred.append({
                    "masks": get_binary(a[i].to("cpu")),
                    "labels": torch.tensor(list(range(32))),
                    "scores": torch.ones(32) / 32.0
                })
                masks_true.append({
                    "masks": get_binary(b[i].to("cpu")),
                    "labels": torch.tensor(list(range(32)))
                }) 
                
            mp = valid_map(masks_pred,masks_true)
            print(mp)
            for i in random.sample(range(len(imgs_x)),2):
                img_x = x[i]
                img_y = y_pred[i]
                true_y= imgs_y[i]
                fig,axs=plt.subplots(1,3, figsize=(15, 5))
                axs[0].imshow(img_x.to("cpu").permute(1, 2, 0).numpy())
                axs[0].set_title("Input Image")
                axs[1].imshow(invert_y(img_y.to("cpu").detach().permute(1, 2, 0), labels))
                axs[1].set_title("Model Prediction")
                axs[2].imshow(invert_y(true_y.to("cpu").detach().permute(1, 2, 0), labels))
                axs[2].set_title("Ground Truth")
                plt.tight_layout()
                plt.savefig(os.path.join(folder_name, f'mask_{i}.png'))
                plt.close(fig)
    

    # Compute and print metrics
    mp = valid_map.compute()
    accuracy = val_acc.compute()
    #confusion_matrix_df = pd.DataFrame(val_confmat.compute(), columns=labels.name.values, index=labels.name.values).apply(lambda d: d.round(2)),annot=True)

    # Visualization of metrics
    fig, ax = plt.subplots()
    sns.heatmap(pd.DataFrame(val_confmat.compute(),columns=labels.name.values,index=labels.name.values).apply(lambda d: d.round(2)),annot=True)
    #sns.heatmap(confusion_matrix_df.apply(lambda r: r.round(2)), annot=True)
    plt.savefig('confusion_matrix.png')
    logging.info("Confusion matrix saved to confusion_matrix.png")
    print(f"General accuracy is: {accuracy}")
    print(mp)

    return accuracy
    #, confusion_matrix_df

if __name__ == '__main__':
    # Load Annotations
    X_valid_annot, y_valid_annot = load_annotations(
        './data/val',
        '{}_L.{}'  # Pattern to convert X to Y
    )

    # For the validation dataset, do not apply transformations
    valid_dataset = LocalCarImageDataset(
        X_valid_annot, y_valid_annot,
        "./data/val",
        "./data/transformed_images/val",
        x_transform=None,  # No augmentation
        transform=None,  # No additional transformations
        target_transform=None
    )

    # Prepare DataLoader
    valid_loader = DataLoader(valid_dataset, batch_size=16, shuffle=False, collate_fn=collate)

    # Load labels
    labels = pd.read_csv("./data/class_dict.csv").set_index(["r", "g", "b"])

    # Define device
    device = torch.device("cuda" if torch.cuda.is_available() else 'cpu')

    # Load the trained model
    model = torch.load('deeplabv3_model.pt')

    # Evaluate the model
    evaluate_model(model, device, valid_loader, labels)
