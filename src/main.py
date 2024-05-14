# Standard Libraries
import sys
import os
import subprocess
import PySimpleGUI as sg
import keyboard
from ultralytics import YOLO  # Ultralytics is a package for YOLO model

# Ensure the src directory is in the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


# Check if the data folder exists, if not create it and run download_data.sh
def setup_data_folder():
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    data_dir = os.path.join(root_dir, 'data')
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        script_path = os.path.join(root_dir, 'scripts', 'download_data.sh')
        subprocess.run(['bash', script_path], check=True)


# Run the setup function
setup_data_folder()

# Code imports using absolute imports
from models.lidar import resetScene  # Utilities for LiDAR processing
from utils.event_handlers import handle_about_event, handle_help_event  # Event handling functions
from utils.image_processing import process_images_and_pcap  # Image processing functions
from interfaces.gui import VideoPlayer  # Video player class
from models.semseg import init_semseg_model  # Semantic segmentation model initialization
from utils.gui_utils import set_layout, folder_select  # GUI utilities


def programEnd():
    """Handle program termination."""
    print('Bye bye')
    sys.exit(0)


# Global hotkey to exit the program
keyboard.add_hotkey('esc', programEnd)


def main():
    """Main function to run the GUI application."""
    # Initialize the startup layout
    window, _ = set_layout('startup')

    # Initialize variables
    folder = ''
    frames = []
    video_player = None
    resize = (600, 450)  # 4:3 ratio

    # Load models
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    data_path = os.path.join(root_dir, 'data', 'class_dict.csv')
    semantic_segmentation_model = init_semseg_model(data_path)  # Semantic segmentation model
    object_detection_model = YOLO(
        os.path.join(root_dir, 'UltralyticsModel_snapshot.pt'))  # YOLO model for object detection

    # Main event loop
    while True:
        event, values = window.read(timeout=100)

        if event in (None, 'Exit', sg.WIN_CLOSED):
            if video_player is not None:
                video_player.stop_video()

        elif event == '-SLIDER-':
            # When the slider is moved, update images to that frame
            new_frame_index = int(values['-SLIDER-'])
            video_player.update_images_to_slider(new_frame_index)

        if event == '-PLAY-':
            video_player.play_video()

        elif event == '-PAUSE-':
            video_player.pause_video()

        elif event == '-RESTART-':
            video_player.restart_video()

        if event == 'Open Folder':
            # Folder selection
            window.close()
            folder, frames, window = folder_select(window)
            # Debug
            # print("Keys in the new window:", window.AllKeysDict.keys())

        elif event == 'Confirm':
            # Process images and lidar data
            window.close()
            window, _ = set_layout('processing', [len(frames)])
            progress_bar = window['-PROGRESS BAR-']
            object_results, seg_paths = process_images_and_pcap(folder, frames, object_detection_model,
                                                                semantic_segmentation_model, progress_bar)

            # Update GUI after processing
            window.close()
            window, _ = set_layout('object detected', [len(frames)])

            # Initialize video player
            video_player = VideoPlayer(frames, window, folder, resize, object_results, seg_paths)

        elif event in ('About', 'Help'):
            # Handle 'About' and 'Help' events
            {'About': handle_about_event, 'Help': handle_help_event}[event]()

        elif event in ('Cancel', 'Back'):
            # Handle 'Cancel' and 'Back' events
            frames = []
            resetScene()
            window.close()
            window, _ = set_layout('startup')

    # Close the window and end the program
    window.close()
    programEnd()


if __name__ == '__main__':
    sg.theme('DarkAmber')
    main()
