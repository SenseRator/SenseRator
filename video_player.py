# Library Imports
import cv2
import time
import gui_utils
import os
import PySimpleGUI as sg
import sys

# Code Imports
from lidar_utils import readFile
from convertImage import read_and_resize_image
from timestamp_utils import extract_timestamp

class VideoPlayer:
    def __init__(self, frames, window, folder, resize, object_results, seg_paths):
        self.frames = frames
        self.window = window
        self.folder = folder
        self.resize = resize
        self.object_results = object_results
        self.seg_paths = seg_paths
        self.cur_frame = 0 # Start at 0
        self.paused = True # Start Paused

    def play_video(self):
            self.paused = False
            while not self.paused:
                self.update_frame()
                self.update_slider()
                event, values = self.window.read(timeout=100)
                self.handle_event(event, values)
                if event in (None, 'Exit', 'Cancel', 'Back', sg.WIN_CLOSED):
                    self.paused = True
                if not self.paused: 
                    self.cur_frame = (self.cur_frame + 1) % len(self.frames)


    def pause_video(self):
        self.paused = True

    def restart_video(self):
        self.cur_frame = 0
        self.update_frame()
        self.update_slider()
        self.paused = True

    def stop_video(self):
        self.paused = True
        print('Bye bye')
        sys.exit(0)

    def update_frame(self):
        if self.cur_frame >= len(self.frames):
            self.cur_frame = 0

        frame_name = self.frames[self.cur_frame]
        # Load the original frame
        original_frame = read_and_resize_image(os.path.join(self.folder, frame_name), self.resize)
        # Display object detection results
        detection_image = self.object_results[self.cur_frame].plot()
        # Display segmentation results
        seg_image = cv2.imread(self.seg_paths[self.cur_frame])
        seg_image_resized = cv2.resize(seg_image, self.resize)

        # Update the GUI elements
        detection_im_bytes = cv2.imencode('.png', detection_image)[1].tobytes()
        seg_im_bytes = cv2.imencode('.png', seg_image_resized)[1].tobytes()

        self.window['-IMAGE-'].update(data=detection_im_bytes)
        self.window['-IMAGE2-'].update(data=seg_im_bytes)

        # Read Lidar data
        readFile(self.cur_frame)


    def update_images_to_slider(self, frame_index):
        if frame_index < 0 or frame_index >= len(self.frames):
            return  # Invalid frame index

        self.cur_frame = frame_index  # Update the current frame
        self.update_frame()

    
    def calculate_frame_duration(self, frame_index):
        if frame_index + 1 < len(self.frames):
            try:
                timestamp1 = extract_timestamp(self.frames[frame_index])
                timestamp2 = extract_timestamp(self.frames[frame_index + 1])
                return timestamp2 - timestamp1
            except ValueError:
                # Handle the case where timestamps are not valid numbers
                print(f"Invalid timestamps for frames {frame_index} and {frame_index + 1}")
                return 0
        return 0


    def limit_fps(self, duration):
        start_time = time.time()
        while time.time() - start_time < duration:
            # Process any pending events
            event, values = self.window.read(timeout=100)
            if event:
                self.handle_event(event, values)
    
    def update_slider(self):
        # Debug print to list all keys in the window
        # print("Available keys in the window:", self.window.AllKeysDict.keys())
        # Update the slider
        self.window['-SLIDER-'].update(self.cur_frame)


    def handle_event(self, event, values):
        if event == '-PLAY-':
            self.play_video()
        elif event == '-PAUSE-':
            self.pause_video()
        elif event == '-RESTART-':
            self.restart_video()
        elif event == '-SLIDER-': 
            # When the slider is moved, update images to that frame
            new_frame_index = int(values['-SLIDER-'])
            self.update_images_to_slider(new_frame_index)
