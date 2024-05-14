import time
import keyboard
import numpy as np
import open3d as o3d
import PySimpleGUI as sg
import open3d.visualization.rendering as rendering
import json
from ouster import client, pcap

from utils.file_utils import list_directory_contents, check_path_exists, join_paths, make_directory

# Initialize application
vis = None
app = o3d.visualization.gui.Application.instance
app.initialize()

selected_path = ''
files = []
point_cloud = o3d.geometry.PointCloud()
point_cloud_name = "Scene"
rotation = None

sg.theme('DarkAmber')
selectLayout = [
    [sg.Text('Choose your folder')],
    [sg.Push(), sg.Radio('.pcd/.ply', 0, default=True), sg.Push(), sg.Radio('.pcap', 0), sg.Push()],
    [sg.InputText(key='-FILE-', change_submits=True), sg.FolderBrowse(target='-FILE-')],
    [sg.Text(key='-UPDATE-')],
    [sg.Button('Ok'), sg.Button('Cancel'), sg.Push()]
]

# Pause animation setup
paused = False


def toggle():
    global paused
    paused = not paused


# ----- Helpers -----
def unpackClouds(files, file_type='pcd'):
    global selected_path
    file = None
    json_file = None
    for f in files:
        if f.endswith('.json'):
            json_file = f
        elif f.endswith('.pcap'):
            file = f

    if file is None or json_file is None:
        print('.pcap file and .json metadata required')
    elif file_type == 'pcd':
        pcap_to_pcd(f'{selected_path}/{file}', f'{selected_path}/{json_file}', pcd_dir=f'{selected_path}/PCD_Files')
        selected_path += '/PCD_Files'
    elif file_type == 'ply':
        pcap_to_ply(f'{selected_path}/{file}', f'{selected_path}/{json_file}', ply_dir=f'{selected_path}/PLY_Files')
        selected_path += '/PLY_Files'

    return list_directory_contents(selected_path)


def setup_streaming():
    window = sg.Window('Choose your folder', selectLayout)
    global selected_path
    global files

    while True:
        event, values = window.read()
        try:
            selected_path = values['-FILE-']

            if event == '-FILE-':
                n = len(list_directory_contents(selected_path))
                duration = [int(n / 600), int((n / 10) % 60)]
                window['-UPDATE-'].update(
                    f'The selected folder has {n} frames, totaling {duration[0]}:{duration[1]:02d} of video.')

            if event == 'Ok':
                window['-UPDATE-'].update('Loading...')
                window.Refresh()
                if values[0]:
                    files = list_directory_contents(selected_path)
                else:
                    files = unpackClouds(list_directory_contents(selected_path))
                break

            if event in ('Cancel', sg.WIN_CLOSED):
                window.close()
                return [], ''
        except Exception as e:
            window['-UPDATE-'].update('Something went wrong with LIDAR.')
            print(e)

    window.close()
    return files


def update_point_clouds(file_path):
    point_cloud = o3d.io.read_point_cloud(file_path)
    point_cloud.rotate(rotation, center=(0, 0, 0))
    return point_cloud


def run_one_tick():
    app = o3d.visualization.gui.Application.instance
    tick_return = app.run_one_tick()
    if tick_return:
        vis.post_redraw()
    return tick_return


# Lidar Data Conversion Functions
def pcap_to_pcd(source, metadata, num=0, pcd_dir=".", pcd_base="pcd_out", pcd_ext="pcd"):
    metadata = client.SensorInfo(json.dumps(json.load(open(metadata, 'r'))))
    source = pcap.Pcap(source, metadata)

    if metadata.format.udp_profile_lidar == client.UDPProfileLidar.PROFILE_LIDAR_RNG19_RFL8_SIG16_NIR16_DUAL:
        print(
            "Note: You've selected to convert a dual returns pcap. Second returns are ignored in this conversion for clarity.")

    from itertools import islice
    try:
        import open3d as o3d
    except ModuleNotFoundError:
        print("This example requires open3d. Try running `pip3 install open3d` first.")
        exit(1)

    if not check_path_exists(pcd_dir):
        make_directory(pcd_dir)

    xyzlut = client.XYZLut(metadata)
    scans = iter(client.Scans(source))
    if num:
        scans = islice(scans, num)

    for idx, scan in enumerate(scans):
        xyz = xyzlut(scan.field(client.ChanField.RANGE))
        pcd = o3d.geometry.PointCloud()
        pcd.points = o3d.utility.Vector3dVector(xyz.reshape(-1, 3))
        pcd_path = join_paths(pcd_dir, f'{pcd_base}_{idx:06d}.{pcd_ext}')
        print(f'write frame #{idx} to file: {pcd_path}')
        o3d.io.write_point_cloud(pcd_path, pcd)


def pcap_to_ply(source, metadata, num=0, ply_dir=".", ply_base="ply_out", ply_ext="ply"):
    pcap_to_pcd(source, metadata, num=num, pcd_dir=ply_dir, pcd_base=ply_base, pcd_ext=ply_ext)


# ----- The Meat -----
def initWindow(folder=None, setting=None):
    global vis
    global files
    global rotation
    global selected_path

    vis = o3d.visualization.O3DVisualizer("Lidar Data", 1000, 700)
    vis.add_action("Custom Options", gui_media_visualization.options)
    # vis.add_action("Video Player", windows.mediaPlayer)
    # vis.add_action("Video Player 2.0", main.main)

    app.add_window(vis)
    vis.add_geometry(point_cloud_name, point_cloud)
    vis.ground_plane = rendering.Scene.GroundPlane.XZ
    vis.show_ground = True
    if folder is not None:
        vis.show_settings = False

    vis.setup_camera(60.0, [0, 0, 0], [8, 4, 0], [1, 1, 0])
    rotation = point_cloud.get_rotation_matrix_from_xyz((-np.pi / 2, 0, 0))

    if folder:
        selected_path = folder
        if setting:
            files = list_directory_contents(folder)
        else:
            files = unpackClouds(list_directory_contents(folder))
    else:
        files = setup_streaming()


def readFiles():
    try:
        for file in files:
            if file.endswith('.pcd') or file.endswith('.ply'):
                while paused:
                    time.sleep(0.5)

                vis.remove_geometry(point_cloud_name)
                point_cloud = update_point_clouds(f"{selected_path}/{file}")
                vis.add_geometry(point_cloud_name, point_cloud)

                run_one_tick()
                time.sleep(0.1)
    except Exception as e:
        print(e)
    vis.close()


def readFile(i):
    if i >= len(files):
        return

    global vis
    file = files[i]

    try:
        if file.endswith('.pcd') or file.endswith('.ply'):
            vis.remove_geometry(point_cloud_name)
            point_cloud = update_point_clouds(f"{selected_path}/{file}")
            vis.add_geometry(point_cloud_name, point_cloud)

            run_one_tick()
    except Exception as e:
        print(e)


def resetScene():
    global selected_path
    global files
    selected_path = ''
    files = []
    vis.remove_geometry(point_cloud_name)


if __name__ == '__main__':
    sg.theme('DarkAmber')
    keyboard.add_hotkey('space', toggle)
    print("Tap [space] to pause")
    initWindow()
    readFiles()
