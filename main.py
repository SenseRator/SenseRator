import os
import cv2
import sys
import time
import keyboard
import numpy as np
import PySimpleGUI as sg
from ultralytics import YOLO

import lidar
import convertImage

def programEnd():
    print('Bye bye')
    sys.exit()
keyboard.add_hotkey('esc', programEnd)

resize = (600,450) # 4:3 ratio #Change to 820,615) if there is no semantic segmentation

# Stores object detections information as YOLO results objects
frame_results = []

# Object detection model. 
model = YOLO('model.pt')

# TODO initialize semantic segmentation
# Semantic Segmentation

def timestamp(filename):
    ts = filename.split('_')[1:]
    ts = ts[:5]+ts[5].split('.')[:2]
    s = float(ts[2]) * (24 * 60 * 60) + float(ts[3]) * (60 * 60) + float(ts[4]) * 60 + float(ts[5]) * 1 + float(ts[6]) * .0001
    
    return s

def ImageButton(title, key):
	return sg.Button(title, border_width=0, key=key)

# Set up various layouts to be called later
def set_layout(state, info = []):
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
            [sg.Slider(range=(0,num_frames-1), size=(60,10), orientation='h', key = '-SLIDER-')],
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
    return window



# Let user input folders for images and point clouds
def folder_select(window):
    window = set_layout('folder select')
    folder = ''
    files = np.asarray([])

    while True:
        event, values = window.read()

        try:
            folderCam = values['-FOLDER-']+'/jpg'
            folderLid = values['-FOLDER-']+'/pcd'

            #print(folderCam)
            #print(os.listdir(folderCam))
            #print(folderLid)

            if (event == '-FOLDER-'):
                dir = os.listdir(folderCam)
                n = len(dir)
                time = timestamp(dir[n-3]) - timestamp(dir[0])
                window['-UPDATE-'].update('The selected folder has ' + str(n) + ' frames, totalling ' + '{}:{:.0f}'.format(int(time/60), time%60) + ' of video.')
            
            if (event == 'Ok'):
                window['-UPDATE-'].update('Loading...')
                window.Refresh()

                if folderLid in (None, ''):
                    window['-UPDATE-'].update('No point cloud folder selected.')
                else:
                    print("VALUES")
                    lidar.initWindow(folderLid)

                files = np.asarray(os.listdir(folderCam))
                size = files.size
                frames = files[0:size-3]
                if folderCam in (None, ''):
                    window['-UPDATE-'].update('No image folder selected.')
                else:
                    break
            
            if event in ('Cancel', sg.WIN_CLOSED):
                window.close()
                window = set_layout('folder selected', [frames.size])
                raise Exception ('Window Closed')

        except Exception as e:
            if str(e) == 'Window Closed':
                programEnd()
            window['-UPDATE-'].update('Something went wrong.')
            print(e)
            print(values)
    print("debug")
    window.close()
    window = set_layout('folder selected', [frames.size])
    return folderCam, frames, window

def main():
    window = set_layout('startup')
    folder = ''
    # RGB video frames
    frames = []

    # Event Loop
    while True:
        
        event, values = window.read()
        
        # End of Program
        if event in (None, 'Exit', sg.WIN_CLOSED):
            window.close()
            break

        # Open output folder from vehicle
        if event in ('Open Folder'):
            window.close()
            folder, frames, window = folder_select(window)

        # Process images and pcap file from vehicle output
        elif event in ('Confirm'):
            window.close()
            window = set_layout('processing', [frames.size])
            progress_bar = window['-PROGRESS BAR-']
            
            for i in range(frames.size):
                # Convert images to rgb (cv2 frames). Run predictions on frame. Add results to list.
                img = convertImage.rgbJpg(os.path.join(folder,frames[i]), resize)
                results = model.predict(img, show= True, device=0,show_conf=True, conf=0.8)
                frame_results.append(results[0])

                # TODO do semantic segmentation on frames[i], save as "SemSeg_<filename>" in folder: window['-FOLDER-']+'/semseg'
                # frames[i] is the filename, the filepath is window['-FOLDER-']+'/jpg/'
                

                # Grab lidar frame
                lidar.readFile(i)

                progress_bar.update(current_count = i+1)

            
            window.close()
            window = set_layout('object detected', [frames.size])

            img_elem = window['-IMAGE-']
            img_elem2 = window['-IMAGE2-']
            img_test = img_elem
            slider_elem = window['-SLIDER-']
           

            # Play video
            cur_frame = 0
            paused = True
            while True:
                try:
                    while paused:
                        # When timeout runs out it automatically continues without reading
                        event, values = window.read(timeout=100)

                        # Read events while paused
                        if event in (sg.WIN_CLOSED, 'Cancel', 'Back'):
                            raise Exception('CloseWindow')
                        elif event == '-PLAY-':
                            paused = False
                        elif event == '-RESTART-':
                            raise Exception('RestartVideo')
                        elif event in ('About'):
                            about_window = set_layout('about')
                            while True:
                                event, values = about_window.read()
                                if event in (None, 'Close', sg.WIN_CLOSED):
                                    about_window.close()
                                    break
                        elif event in ('Help'):
                            help_window = set_layout('help')
                            while True:
                                event, values = help_window.read()
                                if event in (None, 'Close', sg.WIN_CLOSED):
                                    help_window.close()
                                    break

                    t = time.time()
                    dur = timestamp(frames[cur_frame+1]) - timestamp(frames[cur_frame])
                    event, values = window.read(timeout=0)

                    if event in ('Cancel', None, 'Exit', 'Back'):
                        break

                    # Update image to slider
                    if int(values['-SLIDER-']) != cur_frame-1 and cur_frame != 0:
                        cur_frame = int(values['-SLIDER-'])

                    # Update slider
                    slider_elem.update(cur_frame)
                    cur_frame = (cur_frame + 1)%(frames.size-3)
                    
                    # img = convertImage.rgbJpg(os.path.join(folder,frames[i]), resize)
                    img = frame_results[cur_frame].plot()

                    # Load image and cloud frames
                    frame = img
                    im_bytes = cv2.imencode('.png', frame)[1].tobytes()
                    img_elem.update(data=im_bytes)
                    # TODO load in semantic segmented image and encode to bytes, pass to img_elem2
                    img_elem2.update(data=im_bytes)
                    lidar.readFile(cur_frame)

                    # Read events while playing
                    try:
                        if event == '-PAUSE-':
                            paused = True
                        elif event == '-RESTART-':
                            raise Exception('RestartVideo')
                        elif event in ('About'):
                            about_window = set_layout('about')
                            while True:
                                event, values = about_window.read()
                                if event in (None, 'Close', sg.WIN_CLOSED):
                                    about_window.close()
                                    break
                        elif event in ('Help'):
                            help_window = set_layout('help')
                            while True:
                                event, values = help_window.read()
                                if event in (None, 'Close', sg.WIN_CLOSED):
                                    help_window.close()
                                    break
                    # Catch errors and use for restarting
                    except Exception as e:
                        if str(e) == 'RestartVideo':
                            cur_frame = 0
                            paused = True
                            slider_elem.update(cur_frame)
                            # img_elem.update(data=None, visible=True)
                        else:
                            print(str(e))

                    # Limits FPS by counting the seconds spent on each frame
                    while(time.time()-t < dur):
                        pass
                    
                    # DEBUGGING / TESTING
                    # Uncomment to test the time spent on each frame by the program
                    # To unlimit fps, change fps variable to 1000 or something high like that
                    # print(time.time()-t)

                # Catch errors and use for restarting (from pause)
                except Exception as e:
                    if str(e) == 'RestartVideo':
                        cur_frame = 0
                        paused = True
                        slider_elem.update(cur_frame)
                        # img_elem.update(data=None)
                    elif str(e) == 'CloseWindow':
                        programEnd()
                    else:
                        print(e)

        elif event in ('About'):
            about_window = set_layout('about')
            while True:
                event, values = about_window.read()
                if event in (None, 'Close', sg.WIN_CLOSED):
                    about_window.close()
                    break

        elif event in ('Help'):
            help_window = set_layout('help')
            while True:
                event, values = help_window.read()
                if event in (None, 'Close', sg.WIN_CLOSED):
                    help_window.close()
                    break

        elif event in ('Cancel', 'Back'):
            frames = []
            lidar.resetScene()
            window.close()
            window = set_layout('startup')

        # End of Program
        if event in (None, 'Exit', sg.WIN_CLOSED):
            window.close()
            programEnd()
            
    return 0



if __name__ == '__main__':
    sg.theme('DarkAmber')
    main()
