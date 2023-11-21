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

resize = (820,615) # 4:3 ratio

# Stores object detections information as YOLO results objects
frame_results = []

# Object detection model. 
model = YOLO('model.pt')

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
    menu_def = [['&Help', ['&About']]]

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

    elif state in ('folder select'):
        layout += [
            [sg.Frame('Images', [
                [sg.InputText(key='-IMGS-', change_submits=True), 
                 sg.FolderBrowse(target='-IMGS-')]] )],
            [sg.Frame('Point Clouds', [
                [sg.Push(), sg.Radio('.pcd/.ply', 0, default=True), 
                 sg.Push(), sg.Radio('.pcap', 0), sg.Push()], 
                [sg.InputText(key='-PCS-', change_submits=True), 
                 sg.FolderBrowse(target='-PCS-')]] )],
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
            folderCam = values['-IMGS-']
            folderLid = values['-PCS-']

            # Image folder changed, update time text
            if (event == '-IMGS-'):
                n = len(os.listdir(folderCam))
                time = [int(n/600), int((n/10)%60)]
                window['-UPDATE-'].update('The selected folder has ' + str(n) + ' frames, totalling ' + '{}:{:02d}'.format(time[0],time[1]) + ' of video.')
            
            if (event == 'Ok'):
                window['-UPDATE-'].update('Loading...')
                window.Refresh()

                if folderLid in (None, ''):
                    window['-UPDATE-'].update('No point cloud folder selected.')
                else:
                    lidar.initWindow(folderLid, values[0])

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
        except Exception as e:
            window['-UPDATE-'].update('Something went wrong.')
            print(e)
    
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
        
        # Open output folder from vehicle
        if event in ('Open Folder'):
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

                # Grab lidar frame
                lidar.readFile(i)

                progress_bar.update(current_count = i+1)

            
            window.close()
            window = set_layout('object detected', [frames.size])

            img_elem = window['-IMAGE-']
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
                        if event == '-PLAY-':
                            paused = False
                        if event == '-RESTART-':
                            raise Exception('RestartVideo')

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
                    lidar.readFile(cur_frame)

                    # Read events while playing
                    try:
                        if event == '-PAUSE-':
                            paused = True
                        if event == '-RESTART-':
                            raise Exception('RestartVideo')
                    # Catch errors and use for restarting
                    except Exception as e:
                        if str(e) == 'RestartVideo':
                            cur_frame = 0
                            paused = True
                            slider_elem.update(cur_frame)
                            # img_elem.update(data=None, visible=True)
                        else:
                            print(e)

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
                        break
                    else:
                        print(e)

        if event in ('Cancel', 'Back'):
            frames = []
            lidar.resetScene()
            window.close()
            window = set_layout('startup')

        # End of Program
        if event in (None, 'Exit', sg.WIN_CLOSED):
            window.close()
            break
            
    return 0



if __name__ == '__main__':
    sg.theme('DarkAmber')
    main()
