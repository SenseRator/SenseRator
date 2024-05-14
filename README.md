# SenseRator
![SenseRator arcimoto vehicle](senserator.png)

## Table of Contents
- [What is SenseRator?](#what-is-senserator?) 
- [Quick start](#quick-start)
	- [With Conda](#with-conda)
- [Usage](#usage)
    - [Training the Semantic Segmentation Model](#training-the-semantic-segmentation-model)
    - [Visualizing Predictions](#visualizing-predictions)
- [Data](#data)
- [Directory Structure](#directory-structure)
- [Members](#members)

## What is SenseRator? 
The SenseRator is a small, sensor-equipped electric vehicle designed for disaster management and terrain mapping. This vehicle, equipped with cameras and LIDAR technology, is tasked with gathering comprehensive environmental data. 

The SenseRator is engineered to perform state-of-the-art object detection. It is specifically trained to identify disaster damage, particularly focusing on flooding, potholes, and fallen trees. This is crucial for assessing post-disaster scenarios where such information is vital for rescue and recovery operations.

Additionally, the algorithm integrates the collected data to provide a detailed semantic understanding of the environment, which can be instrumental for planning rescue efforts.

In summary, the SenseRator is an advanced AI-powered sensor platform that can provide immediate, actionable intelligence in disaster-stricken areas.

<table>
  <tr>
    <td>
      <a href="https://youtu.be/T1tO6F1z9bk" title="SenseRator Application Demo">
        <img src="assets/video_thumbnail_2.png" alt="SenseRator Application Demo Thumbnail">
      </a>
    </td>
    <td>
      <a href="https://youtu.be/rFd1qQmFYQ0" title="Video demo for Senior Design Fall 2023 Showcase">
        <img src="assets/video_thumbnail.png" alt="Video demo for Senior Design Fall 2023 Showcase Thumbnail">
      </a>
    </td>
  </tr>
</table>



## Quick Start

### With Conda
1. Open terminal or Anaconda Prompt
2. Navigate to the directory containing the `environment.yml` file.
1. Create the environment using the following command:    

```bash
conda env create -f environment.yml
```

This command will set up a new Conda environment identical which should work to run all parts of the project (**with the exception of Open3D / LIDAR.**)

### Without Conda
1. [Install CUDA](https://developer.nvidia.com/cuda-downloads)
    
2. [Install PyTorch 1.13 or later](https://pytorch.org/get-started/locally/)
    
3. Install dependencies
    

```shell
pip install -r requirements.txt
```

4. Download the data and run training:

``` 
scripts/download_data.sh
```
## Usage
1. Run the program using terminal `python main.py`
2. Load the capture data from the SenseRator vehicle (which can be downloaded from the Google Drive link) when prompted to select the folder. 
3. Confirm that the expected amount of frames have been loaded, and click 'Confirm' to begin visualization. 
### Download Capture data (.jpg and .pcd) from the SenseRator vehicle
- Capture data from the SenseRator vehicle can be located at this [Google Drive Link](https://drive.google.com/file/d/1wnIPu1QEisPGQWcJxTs4667XRNohbg2G/view)
- This will be the folder you select during the 'File Selection' process of the program. 

**Note: Use Python 3.9.18+**

## Data
The Camvid dataset used for training the semantic segmentation module of the SenseRator project is available on the [Kaggle website](https://www.kaggle.com/datasets/carlolepelaars/camvid). 

You can also download it using the helper script:
```
scripts/download_data.sh
```

The completed data directory should appear as follows: 
```
.
└── data/
    ├── camvid/
    │   ├── images
    │   └── labels
    ├── train
    ├── train_labels
    ├── val
    ├── val_labels
    └── class_dict.csv
```

## Project Directory Structure
```
.
├── assets                          # Contains assets for this README
├── data                            # Contains camvid dataset
├── processed_masks                 # Output folder for semseg masks
├── scripts                         # Utility scripts
│   ├── download_data.sh            # Shell script for downloading CamVid dataset
│   ├── inspect_pt_file.py          # Script for inspecting the contents of a .pt file
│   ├── create_diagrams.py          # Script for creating various project-related diagrams using graphviz
├── src/
│   ├── interfaces/     
│   │   ├── gui.py                          # Handles video player functionality and GUI                                          
│   ├── models/                                                     
│   │   ├── semseg/                         # Semantic Segmentation training, evaluation, and visualization. 
│   │   │   ├── batch_segment.py            # Segments a directory full of images
│   │   │   ├── dataset.py                  # Dataset loader for CamVid dataset
│   │   │   ├── evaluate.py                 # Evaluate the DeepLabV3 model
│   │   │   ├── model.py                    # Setup and utility functions for the semantic segmentation model
│   │   │   ├── preprocess_images.py        # Loads, transforms, and saves images with their corresponding labels for training
│   │   │   ├── segment.py                  # Segments one image specified by the arguments
│   │   │   └── train.py                    # Trains a modified DeepLabV3 semantic segmentation model
│   │   ├── __init__.py
│   │   ├── lidar.py                        # GUI and utilities for visualizing LIDAR
│   │   ├── object_detection.py             # Runs object detection using YOLO
│   ├── utils/                                                     
│   │   ├── gui_utils.py                    # GUI-related utilities (folder select, open windows)
│   │   ├── image_processing.py             # Various image-processing utilities for images and pcap files
│   │   ├── file_utils.py                   # File-handling utilities
│   │   ├── timestamp_utils.py              # Extracts timestamp for video playback
│   │   ├── event_handlers.py               # GUI-related event handlers (help, about)
│   ├── main.py                         # Runs the application and handles events for entire program
│   ├── config.py                       # Config file for the object detection model
├── tests/                          # Unit tests, system tests             
├── UltralyticsModel_snapshot.pt    # Custom YOLO dictionary containing: epoch, best_fitness, model, etc. 
```

## Members:
The SenseRator was a Senior Design project at UCF for the Spring 2023 - Fall 2023 semesters. We were delighted to be included in the semi-finalist's showcase. Listed below are the members of our team and their areas of focus for this project. 

- Alex Varga - Project Manager, Front End, Hardware
- Alek Dussuau - Backend, Data Collection
- Gabriela Shamblin - Front End, Point Cloud Renders
- Jose Puche - Backend, Object Detection
- Trevor Geiger - Backend, Semantic Segmentation, Documentation