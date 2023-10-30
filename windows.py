import os
from PIL import Image
from io import BytesIO
import PySimpleGUI as sui
from multiprocessing import Process

import convertImage

raw_path = 'Data\\raw_images'
abs_path = ''
frames = []
resize = (789,592) # 4:3 ratio

def ImageButton(title, key):
	return sui.Button(title, border_width=0, key=key)

optionsLayout = [[sui.Text("This is a settings menu")],
					[sui.Text("Movement Mode"), sui.Combo(['Fly', 'Model', 'Sun', 'Editing'], 'Fly', enable_events=True), sui.Button('Reset Camera', enable_events=True)],
					[sui.Text("Show Skybox"), sui.Checkbox('', True, s=(3,3), enable_events=True)],
					[sui.Text("Point Size"), sui.Slider((1,10), 3, 1, orientation='h', enable_events=True)],
					[sui.Text("Shader"), sui.Combo(['Standard', 'Unlit', 'Normals', 'Depth'], 'Standard', enable_events=True)],
					[sui.Text("Lighting ???")],
					[sui.Text(key='-UPDATE-')],
					[sui.Submit(), sui.Cancel()]]

mediaLayout = [[sui.Text('Media File Player')],
							 [sui.Graph(canvas_size=resize, 
							 						graph_bottom_left=(0,0),
													graph_top_right=resize, 
													background_color='black', key='-VIDEO-')],
							 [ImageButton('Restart', key='-RESTART-'), 
							  ImageButton('Pause', key='-PAUSE-'),
								ImageButton('Play', key='-PLAY-'),
								ImageButton('Exit', key='-EXIT-')]]

# Options window
def options(vis):
	# Initialize window
	window = sui.Window("More Options", optionsLayout, finalize=True)

	while True:
		event, values = window.read()
		# print(event, values)

		try:
			if event == sui.WIN_CLOSED or event == 'Cancel':
				break
			elif event == 'Submit':
				window['-UPDATE-'].update('Saved')
			# Reset camera to original position
			elif event == 'Reset Camera':
				vis.reset_camera_to_default()
				window['-UPDATE-'].update('Reset camera')
			# Update movement mode
			elif event == 0:
				if values[0] == 'Fly': vis.mouse_mode = gui.SceneWidget.Controls.FLY
				elif values[0] == 'Model': vis.mouse_mode = gui.SceneWidget.Controls.ROTATE_MODEL
				elif values[0] == 'Sun': vis.mouse_mode = gui.SceneWidget.Controls.ROTATE_SUN
				elif values[0] == 'Editing': vis.mouse_mode = gui.SceneWidget.Controls.PICK_POINTS
				else: vis.mouse_mode = gui.SceneWidget.Controls.FLY
				window['-UPDATE-'].update('Updated mouse_mode')
			# Update skybox visibility
			elif event == 1:
				vis.show_skybox(values[1])
				window['-UPDATE-'].update('Updated show_skybox()')
			# Update point size
			elif event == 2:
				vis.point_size = int(values[2])
				window['-UPDATE-'].update('Updated point_size')
			# Update scene shader
			elif event == 3:
				if values[3] == 'Standard': vis.scene_shader = vis.STANDARD
				elif values[3] == 'Unlit': vis.scene_shader = vis.UNLIT
				elif values[3] == 'Normals': vis.scene_shader = vis.NORMALS
				elif values[3] == 'Depth': vis.scene_shader = vis.DEPTH
				else: vis.scene_shader = vis.STANDARD
				window['-UPDATE-'].update('Updated scene_shader')
		except Exception as e:
			print(e)

	window.close()

# Video player window
def mediaPlayer(vis = None):
	# Initialize window and setup file path
	window = sui.Window("Video Player", mediaLayout, finalize=True, element_justification='center');
	# print('CURRENT PATH ', os.getcwd())
	if ('pcd_files' in os.getcwd() or 'ply_files' in os.getcwd()):
		temp = os.getcwd()[-9:]
		os.chdir('..\\raw_images')
		frames = os.listdir()
		abs_path = os.getcwd()
		os.chdir(f'..\{temp}')
	else:
		os.chdir(raw_path)
		frames = os.listdir()
		abs_path = os.getcwd()
		os.chdir('..\..')

	paused = True

	while True:
		try:
			# Set screen to black on reset
			print('Black screen')
			window['-VIDEO-'].erase()

			# Go through files in the folder
			for file in frames:
				while paused:
					# When timeout runs out it automatically continues without reading
					event, values = window.read(timeout=100)

					# Read events while paused
					if event == sui.WIN_CLOSED or event == '-EXIT-':
						print("Paused exit")
						window.close()
						return
					if event == '-PLAY-':
						print("Paused play")
						paused = False
					if event == '-RESTART-':
						print("Paused restart")
						raise Exception('RestartVideo')

				event, values = window.read(timeout=50)

				# Make sure file is correct format and process into usable image/graph
				if file.endswith(".raw"):
					image = convertImage.grayscale(f'{abs_path}\{file}', resize)
					# print(file)
					window['-VIDEO-'].draw_image(data=array_to_data(image), location=(0,resize[1]))
					window.Refresh()

				# Read events while playing
				try:
					if event == sui.WIN_CLOSED or event == '-EXIT-':
						print("Play exit")
						window.close()
						return
					if event == '-PAUSE-':
						print("Play pause")
						paused = True
					if event == '-RESTART-':
						print("Play restart")
						raise Exception('RestartVideo')
				# Catch errors and use for restarting
				except Exception as e:
					if str(e) == 'RestartVideo':
						print('Inner restart')
						paused = True
						break
					else:
						print(e)

		# Catch errors and use for restarting (from pause)
		except Exception as e:
			if str(e) == 'RestartVideo':
				print('Outer restart')
				paused = True
				pass
			else:
				print(e)

	window.close()

# Convert numpy array to image data
def array_to_data(array):
	im = Image.fromarray(array)
	with BytesIO() as output:
		im.save(output, format='PNG')
		data = output.getvalue()
	return data

# Grab video frames (Not used, just for reference)
def video(window, frames=[], abs_path=''):
	for file in frames:
		if file.endswith(".raw"):
			image = convertImage.grayscale(f'{abs_path}\{file}', resize)
			# print(file)
			window['-VIDEO-'].draw_image(data=array_to_data(image), location=(0,resize[1]))
			window.Refresh()
			# time.sleep(0.1)
