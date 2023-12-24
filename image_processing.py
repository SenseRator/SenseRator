import cv2
import numpy as np
from semseg import segment
from object_detection import detect_objects

def process_images_and_pcap(folder, frames, model, seg_model, progress_bar):
    """
    Processes a series of image frames for object detection and segmentation, and reads corresponding LiDAR data.

    This function iterates over a given list of image frames. For each frame, it performs semantic segmentation and 
    object detection, and reads the corresponding LiDAR data. The segmentation paths and object detection results are 
    collected and returned. Additionally, it updates a progress bar after processing each frame.

    Parameters:
        folder (str): The directory where the processed files and results will be stored.
        frames (list): A list of frame names (str) to be processed.
        model (object): The object detection model to be used for detecting objects in the frames.
        seg_model (object): The segmentation model to be used for segmenting the frames.
        progress_bar (object): A progress bar object to be updated as the frames are processed.

    Returns:
        tuple: A tuple containing two lists:
               - The first list contains the object detection results for each frame.
               - The second list contains the file paths of the segmented images.
    """
    from lidar_visualization_gui import readFile
    # Stores object detections information as YOLO results objects
    object_results = []
    seg_image_paths = []
    # Process each frame, performing segmentation and object detection.
    for i, frame_name in enumerate(frames):
        # Segment and save masks to file.
        seg_path = segment(frame_name, folder, seg_model)
        seg_image_paths.append(seg_path)

        # Object detection on frames, return as object_results
        detection_results = detect_objects(frame_name, folder, model)
        object_results.append(detection_results[0])

        # Read Lidar 
        readFile(i)
        
        # Update progress bar
        progress_bar.update(current_count=i+1)
    
    return object_results, seg_image_paths

def read_and_resize_grayscale_image(file_path, resize=None):
    """
    Reads a grayscale image file from the specified path and optionally resizes it.

    Parameters:
        file_path (str): The path to the grayscale image file to be read.
        resize (tuple or None): Optional. A tuple (width, height) specifying the desired
                                dimensions for resizing the image. If None, no resizing
                                will be performed.

    Returns:
        numpy.ndarray: The grayscale image data as a NumPy array (height, width).
                      If resizing is applied, the image will be resized accordingly.
    """
    fd = open(file_path)
    rows = 1080
    cols = 1440
    f = np.fromfile(fd, dtype=np.uint8, count=rows * cols)
    im = f.reshape((rows, cols))  # notice row, column format

    if resize is not None:
        im = cv2.resize(im, dsize=resize, interpolation=cv2.INTER_AREA)

    return im

def read_and_resize_image(file_path, resize=None):
    """
    Reads an image file from the specified path and optionally resizes it.

    Parameters:
        file_path (str): The path to the image file to be read.
        resize (tuple or None): Optional. A tuple (width, height) specifying the desired
                                dimensions for resizing the image. If None, no resizing
                                will be performed.

    Returns:
        numpy.ndarray: The image data as a NumPy array in RGB format (height, width, channels).
                      If resizing is applied, the image will be resized accordingly.
    """
    im = cv2.imread(file_path)

    if resize is not None:
        im = cv2.resize(im, dsize=resize, interpolation=cv2.INTER_AREA)

    return im

def read_raw_image(file_path, resize=None):
    """
    Reads a raw image file from the specified path and optionally resizes it.

    Parameters:
        file_path (str): The path to the raw image file to be read.
        resize (tuple or None): Optional. A tuple (width, height) specifying the desired
                                dimensions for resizing the image. If None, no resizing
                                will be performed.

    Returns:
        numpy.ndarray: The image data as a NumPy array in RGB format (height, width, channels).
                      If resizing is applied, the image will be resized accordingly.

    Note:
        The function reads a raw image file, assumes a fixed size of 1080x1440 pixels, 
        converts it from grayscale to RGB format, and optionally resizes it.
    """
    fd = open(file_path)
    rows = 1080
    cols = 1440
    f = np.fromfile(fd, dtype=np.uint8, count=rows * cols)
    im = f.reshape((rows, cols))  # notice row, column format

    # Grayscale -> RGB
    im = cv2.cvtColor(im, cv2.COLOR_BAYER_BG2BGR)

    if resize is not None:
        im = cv2.resize(im, dsize=resize, interpolation=cv2.INTER_AREA)

    return im
