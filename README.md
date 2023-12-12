# SenseRator
![SenseRator arcimoto vehicle](senserator.png)

## Table of Contents
- [What is SenseRator?](#what-is-senserator?) 
- [Quick start](#quick-start)
	- [With Conda](#with-conda)
- [Usage](#usage)
- [Data](#data)
- [Directory Structure](#directory-structure)
- [Members](#members)

## What is SenseRator? 
The SenseRator is a small, sensor-equipped electric vehicle designed for disaster management and terrain mapping. This vehicle, equipped with cameras and LIDAR technology, is tasked with gathering comprehensive environmental data. 

The SenseRator is engineered to perform state-of-the-art object detection. It is specifically trained to identify disaster damage, particularly focusing on flooding, potholes, and fallen trees. This is crucial for assessing post-disaster scenarios where such information is vital for rescue and recovery operations.

Additionally, the algorithm integrates the collected data to provide a detailed semantic understanding of the environment, which can be instrumental for planning rescue efforts.

In summary, the SenseRator is an advanced AI-powered sensor platform that can provide immediate, actionable intelligence in disaster-stricken areas.

## Quick Start
### With Docker
**WIP**
### With Conda
1. Open terminal or Anaconda Prompt
2. Navigate to the directory containing the `environment.yml` file.
1. Create the environment using the following command:    

```bash
conda env create -f environment.yml
```

This command will set up a new Conda environment identical which should work to run all parts of the project (**with the exception of Open3D / LIDAR.**)

### Without Docker or Conda
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
**WIP**

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

## Directory Structure
**WIP: descriptions needed for each element.**
```
.
├── data
├── datasets
├── processed_masks
├── scripts
├── semseg/
│   ├── batch_segment.py
│   ├── dataset.py
│   ├── evaluate.py
│   ├── model.py
│   ├── preprocess_images.py
│   ├── segment.py
│   └── train.py
├── .gitignore
├── config.py
├── convertCloud.py
├── convertImage.py
├── create_diagrams.py
├── environment.yml
├── event_handlers.py
├── final.pt
├── gui_utils.py
├── image_processing.py
├── lidar_utils.py
├── main.py
├── model_weights.pth
├── object_detection.py
├── timestamp_utils.py
├── video_player.py
└── windows.py
```

## Members:
The SenseRator was a Senior Design project at UCF for the Spring 2023 - Fall 2023 semesters. We were delighted to be included in the semi-finalist's showcase. Listed below are the members of our team and their areas of focus for this project. 

- Alex Varga - Project Manager, Front End, Hardware
- Alek Dussuau - Backend, Data Collection
- Gabriela Shamblin - Front End, Point Cloud Renders
- Jose Puche - Backend, Object Detection
- Trevor Geiger - Backend, Semantic Segmentation