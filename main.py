import PySimpleGUI as sg
import numpy as np
import os

# Set up various layouts to be called later
def set_layout(state, info = []):
    sg.theme('DarkAmber')
    
    # Defines the dropdown menu
    menu_def = [['&Help', ['&About', '&Test']]]

    # Window Layout
    layout = [
        [sg.MenubarCustom(menu_def, key = '-MENU-', tearoff = True)],
        [sg.Text('SenseRator', size = (40,1), justification = 'center')]
    ]

    if state in ('startup', 'Cancel'):
        layout += [
            [sg.Text('Select Vehicle Output Folder')],
            [sg.Button('Open Folder')]
        ]

    elif state in ('folder selected'):
        layout += [
            [sg.Text('The selected file has xxxx frames, totalling xx:xx of video.')],
            [sg.Text('Press Confirm to begin object detection')],
            [sg.Button('Confirm'), sg.Button('Cancel')]
        ]
    
    elif state in ('object detected'):
        layout += [
            # TODO embed detected objects
            # This is the display page
        ]

    layout[-1].append(sg.Sizegrip())

    window = sg.Window('SenseRator', layout, keep_on_top = True, finalize = True, resizable = True)
    window.set_min_size(window.size)
    return window


def main():
    window = set_layout('startup')

    # LiDar packets
    pcap = []
    # Metadata for LiDar visualization in Ouster
    json = []
    # RGB video frames
    frames = []

    # Event Loop
    while True:
        event, values = window.read()

        # End of Program
        if event in (None, 'Exit'):
            break
        
        # Open output folder from vehicle
        elif event in ('Open Folder'):
            folder = sg.popup_get_folder('Choose your folder', keep_on_top=True)
            files = np.asarray(os.listdir(folder))
            size = files.size
            pcap = files[size-1]
            json = files[size-2]
            frames = files[0:size-3]

            window = set_layout('folder selected', [frames.size])

        # Process images and pcap file from vehicle output
        elif event in ('Submit'):
            # Read images in

            # Do object detection

            # Process PCAP file

            # Pair images with LiDar scan
            
            window = set_layout('object detected')

        # Vision Results are displayed
        #elif event in ():
            
            
    return 0

if __name__ == '__main__':
    sg.theme('DarkAmber')
    main()