import PySimpleGUI as sg
from .gui_utils import set_layout

def handle_about_event():
    about_window, _ = set_layout('about')
    while True:
        event, _ = about_window.read()
        if event in (None, 'Close', sg.WIN_CLOSED):
            about_window.close()
            break

def handle_help_event():
    help_window, _ = set_layout('help')
    while True:
        event, values = help_window.read()
        if event in (None, 'Close', sg.WIN_CLOSED):
            help_window.close()
            break
