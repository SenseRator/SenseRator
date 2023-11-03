import PySimpleGUI as sg
import cv2
import numpy as np
import os
import convertImage

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
            [sg.Text('Embedded video display via opencv. Pointcloud rendering opens in new window.')],
            [sg.Image(key='-IMAGE-')],
            [sg.Slider(range=(0,num_frames-1), size=(60,10), orientation='h', key = '-SLIDER-')],
            
            # TODO embed detected objects
            # This is the display page
            [sg.Push(), sg.Button('Cancel')]
        ]

    layout[-1].append(sg.Sizegrip())

    window = sg.Window('SenseRator', layout, keep_on_top = True, finalize = True, resizable = True)
    window.set_min_size(window.size)
    return window


def main():
    window = set_layout('startup')
    folder = ''
    # LiDar packets
    pcap = []
    # Metadata for LiDar visualization in Ouster
    json = []
    # RGB video frames
    frames = []

    # Event Loop
    while True:
        event, values = window.read()
        
        # Open output folder from vehicle
        if event in ('Open Folder'):
            folder = ''
            while(folder == '') :
                folder = sg.popup_get_folder('Choose your folder', keep_on_top=True)
            files = np.asarray(os.listdir(folder))
            size = files.size
            pcap = files[size-1]
            json = files[size-2]
            frames = files[0:size-3]
            
            if folder not in (None, ''):
                window.close()
                window = set_layout('folder selected', [frames.size])

        # Process images and pcap file from vehicle output
        elif event in ('Confirm'):
            window.close()
            window = set_layout('processing', [frames.size])
            progress_bar = window['-PROGRESS BAR-']
            import time
            for i in range(frames.size):
                # Read in image to array
                # Do object detection on image

                progress_bar.update(current_count = i+1)

            # Process PCAP file

            # Pair images with LiDar scan
            
            window.close()
            window = set_layout('object detected', [frames.size])

            # Vision Results are displayed

            img_elem = window['-IMAGE-']
            slider_elem = window['-SLIDER-']
            timeout = 50 # 1000 ms / 10 fps = 100 ms per frame

            # Play Video
            cur_frame = 0
            while True:
                event, values = window.read(timeout=timeout)
                if event in ('Cancel', None, 'Exit'):
                    break

                if int(values['-SLIDER-']) != cur_frame-1:
                    cur_frame = int(values['-SLIDER-'])

                slider_elem.update(cur_frame)
                cur_frame = (cur_frame + 1)%frames.size
                
                bgr_image = convertImage.rgb(folder+'/'+frames[cur_frame], (720,540))
                # --==-- Plan B --==--
                # If calling the file for each frame ends up taking too long at runtime,
                # the ML algo can be initialized before this loop and called for each
                # frame as in Plan A
                #
                #
                # --==-- TODO Jose (Plan A) --==--
                # bgr_image is a 720x540 np array in cv2's bgr format
                # import your file at the head of main
                # run machine learning on bgr_image here
                # detected_image = yourfile.yourfuncion(bgr_image)
                # Change from bgr_image to detected_image
                frame = bgr_image
                im_bytes = cv2.imencode('.png', frame)[1].tobytes()
                img_elem.update(data=im_bytes)



    

        #elif event in ():
        elif event in ('Cancel'):
            pcap = []
            json = []
            frames = []

            window.close()
            window = set_layout('startup')

        # End of Program
        if event in (None, 'Exit'):
            break
            
            
    return 0

if __name__ == '__main__':
    sg.theme('DarkAmber')
    main()