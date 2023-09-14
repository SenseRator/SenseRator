import copy
import matplotlib.pyplot as plt
import numpy as np
import keyboard
import open3d as o3d
import PySimpleGUI as sui

print("Use SimpleGUI with point cloud window")

app = o3d.visualization.gui.Application.instance
app.initialize()

# sample_ply_data = o3d.data.PLYPointCloud()
# pcd = o3d.io.read_point_cloud(sample_ply_data.path)

point_cloud = o3d.io.read_point_cloud("Hotel.ply")

layout = [[sui.Text("Hello, world"), sui.Text(size=(15,1), key='-TEXT-')],
          [sui.Text("This is a text box"), sui.InputText()],
					[sui.Submit(), sui.Cancel()]]

def simpleui(vis):
	window = sui.Window("More Options", layout)

	while True:
		event, values = window.read()
		print(event, values)
		print('Something happend', values[0])
		if event == sui.WIN_CLOSED or event == 'Cancel':
			break
		if event == 'Submit':
			window['-TEXT-'].update(values[0])

	window.close()

vis = o3d.visualization.O3DVisualizer("O3DVis", 700, 500)
vis.add_action("More Options", simpleui)
vis.add_geometry("Hotel", point_cloud)
vis.reset_camera_to_default()

app.add_window(vis)
app.run()

# main_vis = o3d.visualization.Visualizer()
# main_vis.create_window("main_vis", 700, 500)
# main_vis.add_geometry(point_cloud)
# main_vis.run()
# main_vis.destroy_window()