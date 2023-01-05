from machine import UART
#from network import WLAN,Server
#from struct import unpack

import machine, os
uart = UART(0, baudrate=115200)
os.dupterm(uart)
machine.main('main.py')