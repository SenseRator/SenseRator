from utils import image_processing
import torch
from utils.file_utils import join_paths


def detect_objects(filename, folder, model): 
    device = torch.device("cuda" if torch.cuda.is_available() else 'cpu')
    resize = (600,450) # 4:3 ratio #Change to 820,615) if there is no semantic segmentation

    # Convert images to rgb (cv2 frames). Run predictions on frame. Add results to list.
    img = image_processing.read_and_resize_image(join_paths(folder, filename), resize)
    results = model.predict(img, show= True, show_conf=True, conf=0.77, device=device)

    return results
