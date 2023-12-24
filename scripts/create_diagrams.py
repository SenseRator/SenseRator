# Segment.py diagram: 
import matplotlib.pyplot as plt
from graphviz import Digraph
import sys
from pathlib import Path

# Add the parent directory to the sys.path
parent_dir = Path(__file__).parent.parent
sys.path.append(str(parent_dir))

# def create_segment_py_flowchart():
#     # Create a directed graph
#     dot = Digraph(comment='Segment.py Flowchart')

#     # Adding nodes (functions and key steps)
#     dot.node('A', 'Read Image')
#     dot.node('B', 'Preprocess Image')
#     dot.node('C', 'Model Inference')
#     dot.node('D', 'Generate Output Mask')
#     dot.node('E', 'Invert Mask to RGB')
#     dot.node('F', 'Calculate Centroids')
#     dot.node('G', 'Draw Labels on Mask')
#     dot.node('H', 'Combine Masks')
#     dot.node('I', 'Save Processed Mask')

#     # Adding edges to represent the flow
#     dot.edge('A', 'B', 'read_image, Resize, Normalize')
#     dot.edge('B', 'C', 'Model Input')
#     dot.edge('C', 'D', 'Model Output')
#     dot.edge('D', 'E', 'invert_y')
#     dot.edge('D', 'F', 'calculate_centroid')
#     dot.edge('D', 'G', 'draw_labels_on_mask')
#     dot.edge('E', 'H', 'RGB Mask')
#     dot.edge('F', 'G', 'Centroid Info')
#     dot.edge('G', 'H', 'Labeled Mask')
#     dot.edge('H', 'I', 'Combined Mask')

#     return dot

# # Creating the flowchart
# segment_flowchart = create_segment_py_flowchart()

# # Specifying the file path to save the diagram as an JPG file
# flowchart_path = '/mnt/data/segment_py_flowchart.jpg'

# # Rendering the flowchart to a file
# segment_flowchart.render(flowchart_path, format='jpg', cleanup=True)

# # Displaying the flowchart path
# print(f"Flowchart saved as {flowchart_path}")

# System Diagram for entire application: 
# from graphviz import Digraph

# def create_senserator_system_design():
#     # Create a directed graph
#     dot = Digraph(comment='Senserator System Design')

#     # Adding nodes (components of the Senserator project)
#     dot.node('A', 'dataset.py\n(Data Loading & Preprocessing)')
#     dot.node('B', 'model.py\n(Model Architecture)')
#     dot.node('C', 'train.py\n(Model Training)')
#     dot.node('D', 'deeplabv3_model.pt\n(Pre-trained Model)')
#     dot.node('E', 'evaluate.py\n(Model Evaluation)')
#     dot.node('F', 'inference.py\n(Model Inference)')
#     dot.node('G', 'debug.py\n(Debugging)')
#     dot.node('H', 'requirements.txt\n(Dependencies)')
#     dot.node('I', 'test.ipynb\n(Testing/Demo)')

#     # Adding edges to represent the workflow
#     dot.edge('A', 'C', 'Train Data Input')
#     dot.edge('B', 'C', 'Model Definition')
#     dot.edge('D', 'C', 'Pre-trained Weights')
#     dot.edge('C', 'E', 'Trained Model')
#     dot.edge('C', 'F', 'Trained Model')
#     dot.edge('B', 'F', 'Model Definition for Inference')
#     dot.edge('A', 'F', 'Data for Inference')
#     dot.edge('G', 'C', 'Debug Training Process')
#     dot.edge('G', 'F', 'Debug Inference Process')
#     dot.edge('H', 'A', 'Dependencies for Data Processing')
#     dot.edge('H', 'B', 'Dependencies for Model')
#     dot.edge('H', 'C', 'Dependencies for Training')
#     dot.edge('H', 'E', 'Dependencies for Evaluation')
#     dot.edge('H', 'F', 'Dependencies for Inference')
#     dot.edge('H', 'G', 'Dependencies for Debugging')
#     dot.edge('H', 'I', 'Dependencies for Testing/Demo')
#     dot.edge('I', 'E', 'Test/Demo Evaluation')
#     dot.edge('I', 'F', 'Test/Demo Inference')

#     return dot

# # Creating the system design diagram
# senserator_system_design = create_senserator_system_design()

# # Rendering the diagram to a file
# system_design_path = '/mnt/data/senserator_system_design.svg'
# senserator_system_design.render(system_design_path, format='svg', cleanup=True)

# # Displaying the diagram path
# system_design_path

# # # Displaying the flowchart path
# print(f"Flowchart saved as {system_design_path}")


# Model Architecture Diagram
def create_deeplab_model_diagram():
    # Create a directed graph for the DeepLabV3 model structure
    dot = Digraph(comment='DeepLabV3 Model Structure')

    # Adding nodes for main components
    dot.node('A', 'DeepLabV3')
    dot.node('B', 'Backbone')
    dot.node('C', 'Classifier')
    dot.node('D', 'Aux Classifier')

    # Adding sub-nodes for Backbone
    dot.node('B1', 'Conv2dNormActivation (Initial Convolution)')
    dot.node('B2', 'InvertedResidual (Repeated Blocks)')

    # Adding sub-nodes for Classifier
    dot.node('C1', 'ASPP (Atrous Spatial Pyramid Pooling)')
    dot.node('C2', 'Conv2d + BatchNorm2d + ReLU (Final Layers)')
    dot.node('C3', 'Conv2d (Output Layer)')

    # Adding sub-nodes for Aux Classifier
    dot.node('D1', 'Conv2d + BatchNorm2d + ReLU (Aux Layers)')
    dot.node('D2', 'Conv2d (Aux Output Layer)')

    # Adding edges to represent the flow
    dot.edge('A', 'B', 'Input to Backbone')
    dot.edge('B', 'B1', 'Start with Conv2dNormActivation')
    dot.edge('B1', 'B2', 'Followed by InvertedResidual Blocks')
    dot.edge('B', 'C', 'Pass to Classifier')
    dot.edge('C', 'C1', 'Start with ASPP')
    dot.edge('C1', 'C2', 'Followed by Conv2d + BN + ReLU')
    dot.edge('C2', 'C3', 'Output Layer for Segmentation')
    dot.edge('B', 'D', 'Pass to Aux Classifier')
    dot.edge('D', 'D1', 'Aux Conv2d + BN + ReLU')
    dot.edge('D1', 'D2', 'Aux Output Layer')

    return dot

# Creating the DeepLabV3 model structure diagram
deeplab_model_diagram = create_deeplab_model_diagram()

# Rendering the diagram to a file
deeplab_model_diagram_path = '/mnt/data/deeplab_model_diagram.jpg'
deeplab_model_diagram.render(deeplab_model_diagram_path, format='jpg', cleanup=True)

# Displaying the diagram path
deeplab_model_diagram_path
