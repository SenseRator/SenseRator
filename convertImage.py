import os
import cv2
import numpy as np

# TODO: Delete this comment, this function was previously grayscale 
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

# TODO: Delete this comment, this function was previously rgbJpg
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

# TODO: Delete this comment, this function was previously rgbRaw
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
