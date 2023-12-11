# library imports
import PySimpleGUI as sg
import keyboard
import sys
import numpy as np
import os
# code imports
import lidar_utils
from timestamp_utils import extract_timestamp

def ImageButton(title, key):
    return sg.Button(title, border_width=0, key=key)

# Set up various layouts to be called later
def set_layout(state, info = []):
    resize = (600, 450)  # 4:3 ratio
    sg.theme('DarkAmber')
    
    # Defines the dropdown menu
    menu_def = [['Menu', ['About', 'Help']]]

    # Window Layout
    layout = [
        [sg.MenubarCustom(menu_def, key = '-MENU-', tearoff = True)],
        [sg.Text('SenseRator', size = (40,1), justification = 'center')]
    ]

    if state in ('startup'):
        layout += [
            [sg.Text('Select Vehicle Output Folder')],
            [sg.Button('Open Folder')]
        ]

    elif state in ('about'):
        layout += [
            [sg.Text('A small electric vehicle affixed with sensors for the purpose of disaster management and terrain mapping. Using cameras and LIDAR, the vehicle’s purpose is to collect data from those sensors, combine it, input the data in a machine-learning algorithm and output insight on the current state of the environment for use in rescue efforts.', size = (100,4), justification = 'center')],
            [sg.Push(), sg.Button('Close'), sg.Push()]
        ]

    elif state in ('help'):
        layout += [
            [sg.Text('Images are in .jpg format. Point clouds can be in .pcd, .ply, or .pcap formats. If .pcap is selected, it will be automatically unpacked into .pcd.', size = (100,2), justification = 'center')],
            [sg.Text('When the object detection is done processing, you will be able to traverse through the video, pause, play, and restart. The clouds will update along with the video.', size = (100,2), justification = 'center')],
            [sg.Text('To close the entire program, close all windows or tap the [esc] key. (It may take a second)', size = (100,2), justification = 'center')],
            [sg.Push(), sg.Button('Close'), sg.Push()]
        ]

    elif state in ('folder select'):
        layout += [
            [sg.Frame('Input Folder', [
                [sg.InputText(key='-FOLDER-', change_submits=True), 
                 sg.FolderBrowse(target='-FOLDER-')]] )],
            [sg.Text(key='-UPDATE-')],
            [sg.Button('Ok'), sg.Button('Cancel'), sg.Push()]
        ]

    elif state in ('folder selected'):
        n = info[0]
        time = [int(n/600), int((n/10)%60)]
        disp_text = 'The selected file has ' + str(n) + ' frames, totalling ' + '{}:{:02d}'.format(time[0],time[1]) + ' of video.'
        layout += [
            [sg.Text(disp_text)],
            [sg.Text('Press Confirm to begin object detection')],
            [sg.Button('Confirm'), sg.Button('Cancel')]
        ]

    elif state in ('processing'):
        n = info[0]
        layout += [
            [sg.Text('Processing...')],
            [sg.ProgressBar(n, orientation='h', size=(60,20), key='-PROGRESS BAR-')]
        ]
    
    elif state in ('object detected'):
        num_frames = info[0]
        layout += [
            [sg.Image(key='-IMAGE-', size=resize, background_color='black')], 
            [sg.Image(key='-IMAGE2-', size=resize, background_color='white')],
            [sg.Slider(range=(0,num_frames-1), default_value=0, size=(60,10), orientation='h', enable_events=True, key = '-SLIDER-')],
            [ImageButton('Restart', key='-RESTART-'), 
             ImageButton('Pause', key='-PAUSE-'),
             ImageButton('Play', key='-PLAY-')],
            
            # TODO embed detected objects
            # This is the display page
            [sg.Push(), sg.Button('Back')]
        ]

    layout[-1].append(sg.Sizegrip())

    window = None
    if state in ('startup'):
        window = sg.Window('SenseRator', layout, keep_on_top = True, finalize = True, resizable = True, element_justification='center', location=(750,850))
    elif state in ('processing'):
        window = sg.Window('SenseRator', layout, keep_on_top = True, finalize = True, resizable = True, element_justification='center', location=(550,850))
    elif state in ('object detected'):
        window = sg.Window('SenseRator', layout, keep_on_top = True, finalize = True, resizable = True, element_justification='center', location=(20,20))
    else:
        window = sg.Window('SenseRator', layout, keep_on_top = True, finalize = True, resizable = True, element_justification='center')
    window.set_min_size(window.size)

    return window, layout


# Let user input folders for images and point clouds
def folder_select(window):
    frames = []
    window, _ = set_layout('folder select')
    folder = ''
    files = np.asarray([])

    while True:
        event, values = window.read()
        try:
            folderCam = values['-FOLDER-']+'/jpg'
            folderLid = values['-FOLDER-']+'/pcd'

            if (event == '-FOLDER-'):
                if not os.path.exists(folderCam):
                    print(f"Camera folder does not exist: {folderCam}")
                elif not os.path.exists(folderLid):
                    window['-UPDATE-'].update(f"Lidar folder does not exist: {folderLid}")
                else: 
                    dir = os.listdir(folderCam)
                    n = len(dir)
                    time = extract_timestamp(dir[n-3]) - extract_timestamp(dir[0])
                    window['-UPDATE-'].update('The selected folder has ' + str(n) + ' frames, totalling ' + '{}:{:.0f}'.format(int(time/60), time%60) + ' of video.')
            
            if event == 'Ok':
                window['-UPDATE-'].update('Loading...')
                window.Refresh()

                files = np.asarray(os.listdir(folderCam))
                frames = files[0:len(files)-3]
                break

            if event in ('Cancel', sg.WIN_CLOSED):
                window.close()
                break

        except OSError as e:
            print(f"File operation error: {e}")
            window['-UPDATE-'].update("Error accessing folders. Please check folder paths and permissions.")
        except IndexError as e:
            print(f"Index error: {e}")
            window['-UPDATE-'].update("Error processing folder contents. Please check the folder structure.")
        except Exception as e:
            print(f"Unexpected error: {type(e).__name__}, {e}")
            window['-UPDATE-'].update("An unexpected error occurred.")

    window.close()
    window, _ = set_layout('folder selected', [len(frames)])
    return folderCam, frames, window

            # if (event == 'Ok'):
            #     window['-UPDATE-'].update('Loading...')
            #     window.Refresh()

            #     if folderLid in (None, ''):
            #         window['-UPDATE-'].update('No point cloud folder selected.')
            #     else:
            #         print("VALUES")
            #         lidar_utils.initWindow(folderLid)

            #     files = np.asarray(os.listdir(folderCam))
            #     size = files.size
            #     frames = files[0:size-3]
            #     if folderCam in (None, ''):
            #         window['-UPDATE-'].update('No image folder selected.')
            #     else:
            #         break
            
            # if event in ('Cancel', sg.WIN_CLOSED):
            #     window.close()
            #     window, _ = set_layout('folder selected', [frames.size])
            #     raise Exception ('Window Closed')

    #     except Exception as e:
    #         if str(e) == 'Window Closed':
    #             programEnd()
    #         else:
    #             print("Exception type:", type(e).__name__)
    #             print("Exception message:", e)
    #         window['-UPDATE-'].update('Something went wrong with Folder Selection.')
    # window.close()
    # window, _ = set_layout('folder selected', [frames.size])
    # return folderCam, frames, window


def open_about_window():
    about_window, _ = set_layout('about')
    while True:
        event, _ = about_window.read()
        if event in (None, 'Close', sg.WIN_CLOSED):
            about_window.close()
            break

def open_help_window():
    help_window, _  = set_layout('help')
    while True:
        event, _ = help_window.read()
        if event in (None, 'Close', sg.WIN_CLOSED):
            help_window.close()
            break