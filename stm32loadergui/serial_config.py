from enum import Enum
import PySimpleGUI as sg

from .utils.serial_utils import serial_ports
from .loader import LoaderConfig

SYMBOL_TO_PARITY = {"E" : "Even", "O" : "Odd", "N" : "None"}
PARITY_TO_SYMBOL ={v: k for k, v in SYMBOL_TO_PARITY.items()}

class Id(Enum):
    OK = 2
    SERIALS = 4
    BRATES = 5
    DBITS = 6
    SBITS = 7
    PARITY = 8
    FCTRL = 9
    END = 12

def config_window(config: LoaderConfig, avoid=[]):
    BAUDRATES = [9600, 19200, 38400, 57600, 115200, 230400]

    csize = (16, 1)
    ports = serial_ports(avoid=avoid)

    if config.port != None and config.port in ports:
        defport = config.port
    elif ports:
        defport = ports[0]
    else:
        defport = None

    parity = SYMBOL_TO_PARITY[config.parity]

    layout = [
        [sg.Frame('Seriale',
                  [
                      [sg.Column([[sg.Text('Porta')],
                                  [sg.Text('Baudrate')],
                                  [sg.Text('Parity')],
                                  ]),

                       sg.Column([[sg.Combo(ports, key=Id.SERIALS, default_value=defport, size=csize)],
                                  [sg.Combo(BAUDRATES, key=Id.BRATES,
                                            default_value=config.baud, size=csize)],
                                  [sg.Combo(["None", "Even", "Odd"],
                                            key=Id.PARITY, default_value=parity, size=csize)],
                                  ])],
                  ]),],
        [ sg.Frame('Bootloader',
            [
                [sg.Column([[sg.Text('RTS<->DTR')],
                           [sg.Text('RTS attivo basso')],
                           [sg.Text('DTR attivo alto')],
                            ]),
                sg.Column([
                    [sg.Checkbox('')],
                    [sg.Checkbox('')],
                    [sg.Checkbox('')],
                ])]
            ])
        ],
        [sg.Button('Ok', key=Id.OK)],
         ]
    window = sg.Window('Configurazione', layout, finalize=True, keep_on_top=True)

    while True:
        event, values = window.read()
        if event in (None,):   # if user closes window or clicks cancel
            return config

        if event == Id.OK:
            window.close()
            return LoaderConfig(port=values[Id.SERIALS], baud=values[Id.BRATES],
                                parity=PARITY_TO_SYMBOL[values[Id.PARITY]])
            

