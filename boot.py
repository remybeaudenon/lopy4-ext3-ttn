from machine import UART
import gc
#from network import WLAN,Server
#from struct import unpack
import machine, os
gc.enable()
uart = UART(0, baudrate=115200)
os.dupterm(uart)
machine.main('main.py')