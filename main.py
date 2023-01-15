"""
    POLYTEC - ecoleiot.fr
    Project      : FullStack TP   
    Application  : LM335A Temperature sensor on HUA+LoRa Mutlitech gateway  
    Auth         : remybeaudenon@yahoo.com                 
    Date         : 01/2023 
"""
import time,sys,os
from ws2812led import LED
from lm335a import LM335A
from lorawan import LoRaWAN

from logger import  LOGGER

__version__ = "V0.1-2"

LOGGER.log('MAIN:main()','<<<--- START PROGRAM soft version:{} firmware:{} --->>>'.format(__version__,os.uname().release))

#  --- Functions   ---
def log(header , msg ) : 
    print('{:<32} - {} '.format(header,msg)  ) 

#  --- Initialization objects   ---
led = LED()
lorawan = LoRaWAN() 
sensor1 = LM335A('sensor1','P16', 10)         # Pin  Sampling read 10 sec. 

led.setState(LED.BLUE)  
lorawan.join() 
while not lorawan.has_joined() :
    time.sleep(5)

led.setState(LED.GREEN)   
LOGGER.log('MAIN:main()','Loop Started !!!'  ) 

delta_temp = 0.5 # ° 
temp_last = 0 
default_last = 0

ping_activity   = 0 
ping_delay      = 3600  

sleep_delay = 10 

# ----- Loop Business functions ----- 
try :
    while True :

        if not sensor1.isReady() : 
            time.sleep(sleep_delay)
            led.setState(LED.YELLOW) 
            continue
        # Application Logic 
        payload = sensor1.getPayload()
        temp_value = payload.get('temp')
        default = payload.get('default')

        # 'E'vent on default 
        if ( default ^ default_last ) :
            default_last = default
            LOGGER.log('MAIN:main()','New push default: {}'.format(default) ) 
            # Push data 
            lorawan.send(LM335A.getHexPayload(payload))
            ping_activity = 0 
        elif abs(temp_value - temp_last)  > delta_temp :
            temp_last = temp_value 
            LOGGER.log('MAIN:main()','Sensor new push value: {}'.format(temp_value) )
            # Push data  
            lorawan.send(LM335A.getHexPayload(payload))
            ping_activity = 0 
    
        elif ping_activity > ping_delay : 
            payload['event'] = 'P'
            LOGGER.log('MAIN:main()','Sensor new push "Ping activity" : {}'.format(payload) )
            # Push data  
            lorawan.send(LM335A.getHexPayload(payload))
            ping_activity = 0 
    
        else :
            LOGGER.log('MAIN:main()','Sensor temp. old:{} new:{}'.format(temp_last,temp_value) ) 
            ping_activity += sleep_delay
            time.sleep(sleep_delay)

        led.setState(LED.GREEN) 
except Exception as err:
    LOGGER.log('MAIN:main()','Exception  {}'.format(err)) 
    LOGGER.log('MAIN:main()','stack trace {}'.format(sys.print_exception(err)) ) 

finally :
    led.setState(LED.OFF)
    sensor1.__del__() 


