# SenseRator
Senior Design project UCF Spring 2023 - Fall 23.

## Members:
- Alex Varga - Project Manager
- Alek Dussuau
- Gabriela Shamblin
- Jose Puche
- Trevor Geiger

# Road Infrastructure Damage Detection Module

Detect damaged road infrastructure using video analysis.

## Overview

This module aims to detect damaged road infrastructure through video file analysis. Using video processing and feature extraction techniques, the goal is to identify and highlight areas of roads that show signs of damage or deterioration.

## Current State

Currently, the project can load and display video files. The next stages involve implementing damage detection through various preprocessing, feature extraction, and post-processing techniques.

## Prerequisites

- Python 3.x
- OpenCV (cv2)
- PySDL2

For Debian-based systems, dependencies can be installed using:

bash

`sudo apt-get install python3-opencv pip install pysdl2`

## Usage

Run the main application with:
bash
`python3 road_inspector.py`

This will display the video with the filename `test.mp4`. Make sure the video is located in the project's root directory.

## Project Structure

- `video_display.py`: Handles the loading and displaying of video files using the SDL2 library.
- `road_inspector.py`: Main application. Currently, it loads and displays a video. Feature extraction and damage detection will be added here.

## Future Enhancements

1. **Video Preprocessing**: Implement stabilization, denoising, and color normalization.
2. **Feature Extraction**: Incorporate techniques like edge detection or deep learning models to detect damages.
4. **Post-processing**: Filter out false positives and aggregate information.