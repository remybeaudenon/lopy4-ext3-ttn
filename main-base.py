"""
    POLYTEC - ecoleiot.fr
    Project      : FullStack TP   
    Application  : LM335A Temperature sensor on HUA+LoRa Mutlitech gateway  
    Auth         : remybeaudenon@yahoo.com                 
    Date         : 01/2023 
"""

# -- Import section 
from logger import  LOGGER
from lorawan import LoRaWAN
import time

__version__ = "V0.1-2"
LOGGER.log('MAIN:main()','<<<--- START PROGRAM soft version:{} firmware:{} --->>>'.format(__version__,os.uname().release))

#  --- Functions   ---

#  --- Initialization objects   ---
lorawan = LoRaWAN() 

lorawan.join() 
while not lorawan.has_joined():
   pass

LOGGER.log('MAIN:main()','Loop Started !!!'  ) 

# -- Application process variables  

# ----- Loop Business functions ----- 
try :
    while True :
        # --- Process function ---  

        LOGGER.log('MAIN:process()',"C'est dans l'effort que l'on trouve la satisfaction !!!"  ) 
        time.sleep(5)

        # --------------------------
except Exception as err:
    LOGGER.log('MAIN:main()','Exception  {}'.format(err)) 

finally :
    LOGGER.log('MAIN:main()','<<<--- END PROGRAM --->>>')


