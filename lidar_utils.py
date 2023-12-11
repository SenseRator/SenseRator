import os
import time
import keyboard
import numpy as np
import open3d as o3d
import PySimpleGUI as sg
import open3d.visualization.gui as gui
import open3d.visualization.rendering as rendering
import windows
import convertCloud

vis = None
app = o3d.visualization.gui.Application.instance
app.initialize()

selected_path = ''
files = []
point_cloud = o3d.geometry.PointCloud()
point_cloud_name = "Scene"
rotation = None

sg.theme('DarkAmber')
selectLayout = [[sg.Text('Choose your folder')],
								[sg.Push(), sg.Radio('.pcd/.ply', 0, default=True), sg.Push(), sg.Radio('.pcap', 0), sg.Push()],
								[sg.InputText(key='-FILE-', change_submits=True), sg.FolderBrowse(target='-FILE-')],
								[sg.Text(key='-UPDATE-')],
								[sg.Button('Ok'), sg.Button('Cancel'), sg.Push()]]

# Pause animation setup
paused = False
def toggle():
	global paused
	paused = not paused



# ----- Helpers -----
# Unpack point clouds to seperate files
def unpackClouds(files, file_type='pcd'):
	global selected_path
	file = None
	json = None
	for f in files:
		if (f.endswith('.json')):
			json = f
		elif (f.endswith('.pcap')):
			file = f

	if (file == None or json == None):
		print('.pcap file and .json metadata required')
	elif (file_type == 'pcd'):
		convertCloud.pcap_to_pcd(f'{selected_path}\{file}', f'{selected_path}\{json}', pcd_dir=f'{selected_path}\PCD_Files')
		selected_path += '\PCD_Files'
	elif (file_type == 'ply'):
		convertCloud.pcap_to_ply(f'{selected_path}\{file}', f'{selected_path}\{json}', ply_dir=f'{selected_path}\PLY_Files')
		selected_path += '\PLY_Files'

	return os.listdir(selected_path)

# Change file directory 
def setup_streaming():
	window = sg.Window('Choose your folder', selectLayout)
	global selected_path
	global files

	while True:
		event, values = window.read()
		try:
			selected_path = values['-FILE-']

			if (event == '-FILE-'):
				n = len(os.listdir(selected_path))
				time = [int(n/600), int((n/10)%60)]
				window['-UPDATE-'].update('The selected folder has ' + str(n) + ' frames, totalling ' + '{}:{:02d}'.format(time[0],time[1]) + ' of video.')
			
			if (event == 'Ok'):
				window['-UPDATE-'].update('Loading...')
				window.Refresh()
				if (values[0]):
					files = os.listdir(selected_path)
				else:
					files = unpackClouds(os.listdir(selected_path))
				break
			
			if event in ('Cancel', sg.WIN_CLOSED):
				window.close()
				return [], ''
		except Exception as e:
			window['-UPDATE-'].update('Something went wrong with LIDAR.')
			print(e)

	window.close()
	return files

# Read next point cloud 
def update_point_clouds(file_path):
	point_cloud = o3d.io.read_point_cloud(file_path)
	point_cloud.rotate(rotation, center=(0,0,0))
	return point_cloud

# Update window
def run_one_tick():
	app = o3d.visualization.gui.Application.instance
	tick_return = app.run_one_tick()
	if tick_return:
		vis.post_redraw()
	return tick_return



# ----- The Meat -----
# Start window and read in files
def initWindow(folder=None, setting=None):
	global vis
	global files
	global rotation
	global selected_path

	# Create point cloud window
	vis = o3d.visualization.O3DVisualizer("Lidar Data", 1000, 700)
	vis.add_action("Custom Options", windows.options)
	# vis.add_action("Video Player", windows.mediaPlayer)
	# vis.add_action("Video Player 2.0", main.main)

	# Show & setup window
	app.add_window(vis)
	vis.add_geometry(point_cloud_name, point_cloud)
	vis.ground_plane = rendering.Scene.GroundPlane.XZ
	vis.show_ground = True
	if (folder != None):
		vis.show_settings = False
		
	# Rotate camera so its facing the correct direction
	vis.setup_camera(60.0, [0,0,0], [8,4,0], [1,1,0])

	# Rotate point cloud to be aligned with skybox
	rotation = point_cloud.get_rotation_matrix_from_xyz((-np.pi/2, 0, 0))

	# Import files to show
	if folder:
		selected_path = folder
		if setting:
			files = os.listdir(folder)
		else:
			files = unpackClouds(os.listdir(folder))
	else:
		files = setup_streaming()

# Read files all at once (only run if file ran independantly)
def readFiles():
	# Read each file and update frames
	try:
		for file in files:
			if file.endswith('.pcd') or file.endswith('.ply'):
				while paused:
					time.sleep(0.5)

				# Update point cloud
				vis.remove_geometry(point_cloud_name)
				point_cloud = update_point_clouds(f"{selected_path}\{file}")
				vis.add_geometry(point_cloud_name, point_cloud)
				
				run_one_tick()
				time.sleep(0.1)

	except Exception as e:
		print(e)

	vis.close()

# Read one file (to be run in tandem with images/video)
def readFile(i):
	if (i >= len(files)):
		return

	global vis
	file = files[i]

	# Read each file and update frames
	try:
		if file.endswith('.pcd') or file.endswith('.ply'):
			# Update point cloud
			vis.remove_geometry(point_cloud_name)
			point_cloud = update_point_clouds(f"{selected_path}\{file}")
			vis.add_geometry(point_cloud_name, point_cloud)
			
			run_one_tick()

	except Exception as e:
		print(e)

# Empty Open3D scene/window
def resetScene():
	selected_path = ''
	files = []
	vis.remove_geometry(point_cloud_name)



if __name__ == '__main__':
	sg.theme('DarkAmber')
	keyboard.add_hotkey('space', toggle)
	print("Tap [space] to pause")
	initWindow()
	readFiles()