# Standard Libraries
import sys
import PySimpleGUI as sg
import keyboard
from ultralytics import YOLO  # Ultralytics is a package for YOLO model

# Code imports
import semseg  # Semantic segmentation module
import lidar_utils  # Utilities for LiDAR processing
from event_handlers import handle_about_event, handle_help_event  # Event handling functions
from image_processing import process_images_and_pcap  # Image processing functions
from video_player import VideoPlayer  # Video player class
from semseg import init_semseg_model  # Semantic segmentation model initialization
from gui_utils import set_layout, folder_select  # GUI utilities

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
    semantic_segmentation_model = init_semseg_model('./data/class_dict.csv')  # Semantic segmentation model
    object_detection_model = YOLO('final.pt')  # YOLO model for object detection

    # Main event loop
    while True:
        event, values = window.read(timeout=100)

        if event in (None, 'Exit', sg.WIN_CLOSED):
            if video_player is not None: 
                video_player.stop_video()
            break

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

            # Debug
            # print("Calling process_images_and_pcap...")
            object_results, seg_paths = process_images_and_pcap(folder, frames, object_detection_model, semantic_segmentation_model, progress_bar)
            # Debug
            # print("Finished process_images_and_pcap")

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
            lidar_utils.resetScene()
            window.close()
            window, _ = set_layout('startup')

        # Handle video player events
        if video_player:
            if event == '-PLAY-':
                print("Play button pressed.")
                video_player.play_video()
            elif event == '-PAUSE-':
                print("Pause button pressed")
                video_player.pause_video()
            elif event == '-RESTART-':
                print("Restart button pressed")
                video_player.restart_video()


    # Close the window and end the program
    window.close()
    programEnd()

if __name__ == '__main__':
    sg.theme('DarkAmber')
    main()