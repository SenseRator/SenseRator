import os
import time
import keyboard
import open3d as o3d
import PySimpleGUI as sui
import open3d.visualization.gui as gui
import open3d.visualization.rendering as rendering

import convertCloud
import windows

app = o3d.visualization.gui.Application.instance
app.initialize()

# File paths
absolute_path = os.getcwd()
pcd_path = 'Data\pcd_files'
ply_path = 'Data\ply_files'
raw_path = 'Data\\raw_images'

# Pause animation setup
paused = False
def toggle():
	global paused
	paused = not paused
keyboard.add_hotkey('space', toggle) 
# keyboard.add_hotkey('a', print, args=('AAAAAAAAAAAAAAAAAA', ':)')) 

point_cloud = o3d.geometry.PointCloud()
point_cloud_name = "Scene"

# ----- Open3D -----

def unpackPCD():
	# Unpack point clouds to seperate files
	try:
		convertCloud.pcap_to_pcd("Data\car_lidar_test.pcap", "Data\car_lidar_metadata.json", pcd_dir=f"{pcd_path}\.")
	except Exception as e:
		print(e)

def unpackPLY():
	# Unpack point clouds to seperate files
	try:
		convertCloud.pcap_to_ply("Data\car_lidar_test.pcap", "Data\car_lidar_metadata.json", ply_dir=f"{ply_path}\.")
	except Exception as e:
		print(e)

# Change file directory 
def setup_streaming():
	print(os.getcwd())
	os.chdir(f'{absolute_path}\{pcd_path}')

# Read next point cloud 
def update_point_clouds(file_path):
	point_cloud = o3d.io.read_point_cloud(file_path)
	return point_cloud

def run_one_tick():
	app = o3d.visualization.gui.Application.instance
	tick_return = app.run_one_tick()
	if tick_return:
		vis.post_redraw()
	return tick_return

# ----- The Meat -----

# Create point cloud window
vis = o3d.visualization.O3DVisualizer("O3DVis", 1000, 700)
vis.add_action("Custom Options", windows.options)
vis.add_action("Video Player", windows.mediaPlayer)

# Show & setup window
app.add_window(vis)
vis.add_geometry(point_cloud_name, point_cloud)
# TODO: Rotate skybox or point cloud so they are aligned (Or just ignore skybox idk)
vis.ground_plane = rendering.Scene.GroundPlane.XY
vis.show_ground = True
# Rotate camera so its facing the correct direction
vis.setup_camera(60.0, [0,0,0], [-10,0,0], [0,0,1])

# Read each file and update frames
try:
	setup_streaming()

	for file in os.listdir():
		if file.endswith(".pcd"):
			while paused:
				time.sleep(0.5)

			# Update point cloud
			vis.remove_geometry(point_cloud_name)
			point_cloud = update_point_clouds(f"{os.getcwd()}\{file}")
			vis.add_geometry(point_cloud_name, point_cloud)
			
			run_one_tick()
			time.sleep(0.1)

except Exception as e:
	print(e)

vis.close()