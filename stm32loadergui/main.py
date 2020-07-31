import PySimpleGUI as sg

from .ids import Id
from .serial_config import config_window
from .loader import *


def stm32loadergui_main():
    layout = [
        [ sg.Button("Configurazione", key=Id.CONFIG)],
        [
        sg.Input("", size=(48, 1), key=Id.BINARY_PATH),
        sg.FileBrowse("Open",
                      file_types=(('binary files', "*.bin"), ),
                      size=(16, 1),
                      key=Id.BINARY_SELECT),
    ],
        [sg.Text("", size=(64,2), key=Id.STATUS)]
    ]
    w = sg.Window("stm32loader GUI", layout)

    config = LoaderConfig()

    while True:
        event, value = w.read()

        if event == Id.CONFIG:
            config_window(config)
        elif event in [None, "exit"]:
            break

    w.close()
