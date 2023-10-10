import copy
import matplotlib.pyplot as plt
import numpy as np
# import keyboard
import open3d as o3d
import open3d.visualization.gui as gui
import PySimpleGUI as sui

print("Use SimpleGUI with point cloud window")

app = o3d.visualization.gui.Application.instance
app.initialize()

# Import sample cloud
# sample_ply_data = o3d.data.PLYPointCloud()
# pcd = o3d.io.read_point_cloud(sample_ply_data.path)

# Import test cloud
point_cloud = o3d.io.read_point_cloud("Hotel.ply")

# For SimpleUI
layout = [[sui.Text("This is a settings menu")],
					[sui.Text("Movement Mode"), sui.Combo(['Fly', 'Model', 'Sun', 'Editing'], 'Fly', enable_events=True), sui.Button('Reset Camera', enable_events=True)],
					[sui.Text("Show Skybox"), sui.Checkbox('', True, s=(3,3), enable_events=True)],
					[sui.Text("Point Size"), sui.Slider((1,10), 3, 1, orientation='h', enable_events=True)],
					[sui.Text("Shader"), sui.Combo(['Standard', 'Unlit', 'Normals', 'Depth'], 'Standard', enable_events=True)],
					[sui.Text("Lighting ???")],
					[sui.Text(key='-UPDATE-')],
					[sui.Submit(), sui.Cancel()]]

# --- Events --- ALL THIS WORKS!!!
# 0: mouse_mode = out
# 1: vis.show_skybox(out)
# 2: point_size = out
# 3: scene_shader = out
# Reset Camera: vis.reset_camera_to_default()

# --- Automated actions ---
# Add/clear 3d label
# Add/get/remove/update geometry
# Animation stuff

# --- User actions ---
# Export current image
# Mouse mode (movement)
# Show skybox
# Point size
# Scene shader
# Lighting?
# Selecting (if time)

# For video: https://www.pysimplegui.org/en/latest/Demos/#demo_media_playerpy
# For lidar: http://www.open3d.org/docs/latest/python_api/open3d.visualization.O3DVisualizer.html

# Show test options window
def simpleui(vis):
	window = sui.Window("More Options", layout)

	while True:
		event, values = window.read()
		print(event, values)
		try:
			if event == sui.WIN_CLOSED or event == 'Cancel':
				break
			elif event == 'Submit':
				window['-UPDATE-'].update('Saved')
			elif event == 'Reset Camera':
				vis.reset_camera_to_default()
				window['-UPDATE-'].update('Reset camera')
			elif event == 0:
				if values[0] == 'Fly': vis.mouse_mode = gui.SceneWidget.Controls.FLY
				elif values[0] == 'Model': vis.mouse_mode = gui.SceneWidget.Controls.ROTATE_MODEL
				elif values[0] == 'Sun': vis.mouse_mode = gui.SceneWidget.Controls.ROTATE_SUN
				elif values[0] == 'Editing': vis.mouse_mode = gui.SceneWidget.Controls.PICK_POINTS
				else: vis.mouse_mode = gui.SceneWidget.Controls.FLY
				window['-UPDATE-'].update('Updated mouse_mode')
			elif event == 1:
				vis.show_skybox(values[1])
				window['-UPDATE-'].update('Updated show_skybox()')
			elif event == 2:
				vis.point_size = int(values[2])
				window['-UPDATE-'].update('Updated point_size')
			elif event == 3:
				if values[3] == 'Standard': vis.scene_shader = vis.STANDARD
				elif values[3] == 'Unlit': vis.scene_shader = vis.UNLIT
				elif values[3] == 'Normals': vis.scene_shader = vis.NORMALS
				elif values[3] == 'Depth': vis.scene_shader = vis.DEPTH
				else: vis.scene_shader = vis.STANDARD
				window['-UPDATE-'].update('Updated scene_shader')
		except:
			print('Something went wrong')

	window.close()

# Create point cloud window
vis = o3d.visualization.O3DVisualizer("O3DVis", 1000, 700)
vis.add_action("Custom Options", simpleui)
vis.add_geometry("Hotel", point_cloud)
vis.reset_camera_to_default()

# Show window
app.add_window(vis)
app.run()

# Normal visualizer (no skybox or menu)
# main_vis = o3d.visualization.Visualizer()
# main_vis.create_window("main_vis", 700, 500)
# main_vis.add_geometry(point_cloud)
# main_vis.run()
# main_vis.destroy_window()