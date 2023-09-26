#!/usr/bin/env python3

import cv2
from video_display import Display

# Constants
WIDTH = 1920 // 2
HEIGHT = 1080 // 2
VIDEO_PATH = "test.mp4"

def process_frame(img):
    img = cv2.resize(img, (WIDTH, HEIGHT))
    disp.paint(img)

if __name__ == "__main__":
    cap = cv2.VideoCapture(VIDEO_PATH)

    if not cap.isOpened():
        print(f"Error: Couldn't open the video file {VIDEO_PATH}")
        exit(1)

    disp = Display(WIDTH, HEIGHT)

    while cap.isOpened():
        ret, frame = cap.read()
        if ret:
            process_frame(frame)
        else:
            break

    cap.release()
    disp.close()
