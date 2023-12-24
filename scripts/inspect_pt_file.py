import torch
import sys
from pathlib import Path

# Add the parent directory to the sys.path
parent_dir = Path(__file__).parent.parent
sys.path.append(str(parent_dir))

file_path = 'UltralyticsModel_snapshot.pt'
loaded_dict = torch.load(file_path)

for key, value in loaded_dict.items():
    print(f"Key: {key}")
    print(f"Type of value: {type(value)}")
    # Add more specific print statements if needed, for example, to show tensor shapes
    if isinstance(value, torch.Tensor):
        print(f"Shape of tensor: {value.shape}")
    print("-----------")
