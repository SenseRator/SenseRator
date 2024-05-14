import cv2
import time
import PySimpleGUI as sg
import sys
from PIL import Image
from io import BytesIO

# Code Imports
from models.lidar import readFile
from utils.image_processing import read_and_resize_image, read_and_resize_grayscale_image
from utils.timestamp_utils import extract_timestamp
from utils.file_utils import join_paths, change_directory, get_current_directory, list_directory_contents

raw_path = 'Data\\raw_images'
abs_path = ''
frames = []
resize = (789, 592)  # 4:3 ratio

sg.theme('DarkAmber')

def ImageButton(title, key):
    return sg.Button(title, border_width=0, key=key)

optionsLayout = [[sg.Text("This is a settings menu")],
                 [sg.Text("Movement Mode"), sg.Combo(['Fly', 'Model', 'Sun', 'Editing'], 'Fly', enable_events=True), sg.Button('Reset Camera', enable_events=True)],
                 [sg.Text("Show Skybox"), sg.Checkbox('', True, s=(3, 3), enable_events=True)],
                 [sg.Text("Point Size"), sg.Slider((1, 10), 3, 1, orientation='h', enable_events=True)],
                 [sg.Text("Shader"), sg.Combo(['Standard', 'Unlit', 'Normals', 'Depth'], 'Standard', enable_events=True)],
                 [sg.Text("Lighting ???")],
                 [sg.Text(key='-UPDATE-')],
                 [sg.Submit(), sg.Cancel()]]

mediaLayout = [[sg.Text('Media File Player')],
               [sg.Graph(canvas_size=resize,
                         graph_bottom_left=(0, 0),
                         graph_top_right=resize,
                         background_color='black', key='-VIDEO-')],
               [ImageButton('Restart', key='-RESTART-'),
                ImageButton('Pause', key='-PAUSE-'),
                ImageButton('Play', key='-PLAY-'),
                ImageButton('Exit', key='-EXIT-')]]

# Options window
def options(vis):
    """
    Opens a window for additional settings and options related to Open3D visualization.

    Parameters:
        vis (Open3D.visualization.O3DVisualizer): The Open3D visualizer object.
    """
    window = sg.Window("More Options", optionsLayout, finalize=True)

    while True:
        event, values = window.read()
        print(f"Event: {event}, Values: {values}")

        try:
            if event == sg.WIN_CLOSED or event == 'Cancel':
                break
            elif event == 'Submit':
                window['-UPDATE-'].update('Saved')
            # Reset camera to original position
            elif event == 'Reset Camera':
                vis.reset_camera_to_default()
                window['-UPDATE-'].update('Reset camera')
            # Update movement mode
            elif event == 0:
                if values[0] == 'Fly':
                    vis.mouse_mode = gui.SceneWidget.Controls.FLY
                elif values[0] == 'Model':
                    vis.mouse_mode = gui.SceneWidget.Controls.ROTATE_MODEL
                elif values[0] == 'Sun':
                    vis.mouse_mode = gui.SceneWidget.Controls.ROTATE_SUN
                elif values[0] == 'Editing':
                    vis.mouse_mode = gui.SceneWidget.Controls.PICK_POINTS
                else:
                    vis.mouse_mode = gui.SceneWidget.Controls.FLY
                window['-UPDATE-'].update('Updated mouse_mode')
            # Update skybox visibility
            elif event == 1:
                vis.show_skybox(values[1])
                window['-UPDATE-'].update('Updated show_skybox()')
            # Update point size
            elif event == 2:
                vis.point_size = int(values[2])
                window['-UPDATE-'].update('Updated point_size')
            # Update scene shader
            elif event == 3:
                if values[3] == 'Standard':
                    vis.scene_shader = vis.STANDARD
                elif values[3] == 'Unlit':
                    vis.scene_shader = vis.UNLIT
                elif values[3] == 'Normals':
                    vis.scene_shader = vis.NORMALS
                elif values[3] == 'Depth':
                    vis.scene_shader = vis.DEPTH
                else:
                    vis.scene_shader = vis.STANDARD
                window['-UPDATE-'].update('Updated scene_shader')
        except Exception as e:
            print(e)

    window.close()

# Convert numpy array to image data
def array_to_data(array):
    """
    Converts a numpy array to image data suitable for displaying in a GUI.

    Parameters:
        array (numpy.ndarray): The image data as a numpy array.

    Returns:
        bytes: The image data in a format suitable for display in the GUI.
    """
    im = Image.fromarray(array)
    with BytesIO() as output:
        im.save(output, format='PNG')
        data = output.getvalue()
    return data

# Video player window
def mediaPlayer(vis=None):
    """
    Launches a media player window to play and control media files, specifically raw image files.

    Parameters:
        vis (Open3D.visualization.O3DVisualizer, optional): The Open3D visualizer object, if used with Open3D visualization.
    """
    window = sg.Window("Video Player", mediaLayout, finalize=True, element_justification='center')
    if 'pcd_files' in get_current_directory() or 'ply_files' in get_current_directory():
        temp = get_current_directory()[-9:]
        change_directory('..\\raw_images')
        frames = list_directory_contents()
        abs_path = get_current_directory()
        change_directory(f'..\\{temp}')
    else:
        change_directory(raw_path)
        frames = list_directory_contents()
        abs_path = get_current_directory()
        change_directory('../../../..')

    paused = True

    while True:
        try:
            # Set screen to black on reset
            print('Black screen')
            window['-VIDEO-'].erase()

            # Go through files in the folder
            for file in frames:
                while paused:
                    event, values = window.read(timeout=100)

                    # Read events while paused
                    if event == sg.WIN_CLOSED or event == '-EXIT-':
                        print("Paused exit")
                        window.close()
                        return
                    if event == '-PLAY-':
                        print("Paused play")
                        paused = False
                    if event == '-RESTART-':
                        print("Paused restart")
                        raise Exception('RestartVideo')

                event, values = window.read(timeout=17)

                if file.endswith(".raw"):
                    image = read_and_resize_grayscale_image(f'{abs_path}\\{file}', resize)
                    window['-VIDEO-'].erase()
                    window['-VIDEO-'].draw_image(data=array_to_data(image), location=(0, resize[1]))
                    window.Refresh()

                try:
                    if event == sg.WIN_CLOSED or event == '-EXIT-':
                        print("Play exit")
                        window.close()
                        return
                    if event == '-PAUSE-':
                        print("Play pause")
                        paused = True
                    if event == '-RESTART-':
                        print("Play restart")
                        raise Exception('RestartVideo')
                except Exception as e:
                    if str(e) == 'RestartVideo':
                        print('Inner restart')
                        paused = True
                        break
                    else:
                        print(e)
        except Exception as e:
            if str(e) == 'RestartVideo':
                print('Outer restart')
                paused = True
                pass
            else:
                print(e)

    window.close()

class VideoPlayer:
    """
    A class to handle the playback and control of video frames, including displaying additional image processing results.

    Attributes:
        frames (list): List of frame file names.
        window (PySimpleGUI.Window): The GUI window for the video player.
        folder (str): Directory path containing the video frames.
        resize (tuple): Dimensions to resize the video frames.
        object_results (list): List of object detection results.
        seg_paths (list): List of segmentation image paths.
        cur_frame (int): Current frame index.
        paused (bool): Pause state of the video.
    """
    def __init__(self, frames, window, folder, resize, object_results, seg_paths):
        self.frames = frames
        self.window = window
        self.folder = folder
        self.resize = resize
        self.object_results = object_results
        self.seg_paths = seg_paths
        self.cur_frame = 0  # Start at 0
        self.paused = True  # Start Paused

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
        original_frame = read_and_resize_image(join_paths(self.folder, frame_name), self.resize)
        detection_image = self.object_results[self.cur_frame].plot()
        seg_image = cv2.imread(self.seg_paths[self.cur_frame])
        seg_image_resized = cv2.resize(seg_image, self.resize)

        detection_im_bytes = cv2.imencode('.png', detection_image)[1].tobytes()
        seg_im_bytes = cv2.imencode('.png', seg_image_resized)[1].tobytes()

        self.window['-IMAGE-'].update(data=detection_im_bytes)
        self.window['-IMAGE2-'].update(data=seg_im_bytes)

        readFile(self.cur_frame)

    def update_images_to_slider(self, frame_index):
        if frame_index < 0 or frame_index >= len(self.frames):
            return

        self.cur_frame = frame_index
        self.update_frame()

    def calculate_frame_duration(self, frame_index):
        if frame_index + 1 < len(self.frames):
            try:
                timestamp1 = extract_timestamp(self.frames[frame_index])
                timestamp2 = extract_timestamp(self.frames[frame_index + 1])
                return timestamp2 - timestamp1
            except ValueError:
                print(f"Invalid timestamps for frames {frame_index} and {frame_index + 1}")
                return 0
        return 0

    def limit_fps(self, duration):
        start_time = time.time()
        while time.time() - start_time < duration:
            event, values = self.window.read(timeout=100)
            if event:
                self.handle_event(event, values)

    def update_slider(self):
        self.window['-SLIDER-'].update(self.cur_frame)

    def handle_event(self, event, values):
        if event == '-PLAY-':
            self.play_video()
        elif event == '-PAUSE-':
            self.pause_video()
        elif event == '-RESTART-':
            self.restart_video()
        elif event == '-SLIDER-':
            new_frame_index = int(values['-SLIDER-'])
            self.update_images_to_slider(new_frame_index)
