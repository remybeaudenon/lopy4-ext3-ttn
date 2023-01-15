import pycom
from time import sleep_ms
from logger import  LOGGER

class LED : 
    """RGB Led object functions """   # __doc__ value
    RED  = 0xFF0000
    ORANGE = 0xFFA500
    YELLOW  = 0xFFFF00
    GREEN   = 0x00FF00
    BLUE   = 0x0000FF
    INDIGO = 0x040013
    PURPLE = 0x170016
    CYAN   = 0x00FFFF
    MAGENTA= 0xFF00FF
    WHITE  = 0xFFFFFF
    BLACK   = 0x000000
    PINK   = 0x9E044F

    OFF = 0x000000
    state = OFF
    __instance = None

    def __init__(self) : 
        pycom.heartbeat(False)
        LED.__instance = self
        LOGGER.log('LED:init()','Init instance')

    @classmethod
    def getInstance(cls):
        if (cls.__instance == None ) :
            cls.__instance = LED()
        return cls.__instance

    def setState(self,state):
        LED.state = state
        pycom.rgbled(LED.state)

    def pulse(self,color,duration = 250):
        pycom.rgbled(color)
        sleep_ms(duration)
        pycom.rgbled(LED.state)

