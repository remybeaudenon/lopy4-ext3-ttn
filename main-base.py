"""
    POLYTEC - ecoleiot.fr
    Project      : FullStack TP   
    Application  : LM335A Temperature sensor on HUA+LoRa Mutlitech gateway  
    Auth         : remybeaudenon@yahoo.com                 
    Date         : 01/2023 
"""
import time,sys,os

# application package 
from ws2812led import LED
from lorawan import LoRaWAN, ENUM_GATEWAY
from logger import  LOGGER

__version__ = "V0.2-0"
LOGGER.log('MAIN:main()','<<<--- START PROGRAM soft version:{} firmware:{} --->>>'.format(__version__,os.uname().release))

# --- Capteur Type 
class ENUM_TP:
    TC47    = True
    LM335A  = False

#  --- Functions   ---

#  --- Initialization objects   ---
led = LED()
#lorawan = LoRaWAN(ENUM_GATEWAY.HUA[0]) 
lorawan = LoRaWAN() 

# --- TP Sensor instanciation  ---  
if ENUM_TP.LM335A :
    from lm335a import LM335A 
    sensor1 = LM335A('sensor lm335A','P16', 10) # Pin  Sampling read 10 sec. 
elif ENUM_TP.TC47 :
    from tc74 import TC74
    sensor1 = TC74('P9','P10','sensor tc74')    # Pin  default Sampling read 10 sec. 

led.setState(LED.BLUE)  
lorawan.join(ENUM_GATEWAY.TTN) 

LOGGER.log('MAIN:main()','Loop Started !!!'  ) 

ping_activity   = 0 
ping_delay      = 3600  

sleep_delay = 10 

# ----- Loop Business functions ----- 
try :
    while True :

        """  Votre Code ici 
        


        """   
        led.setState(LED.GREEN) 
        time.sleep(sleep_delay)


except Exception as err:
    LOGGER.log('MAIN:main()','Exception  {}'.format(err)) 
    LOGGER.log('MAIN:main()','stack trace {}'.format(sys.print_exception(err)) ) 

finally :
    led.setState(LED.OFF)
    sensor1.__del__() 


