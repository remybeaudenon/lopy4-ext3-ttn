
"""
# -- TC74  -40°C to +125°C Temp Range   
# -- low power - 200µA Operating
# Communication with the TC74 is accomplished via a 2-wire 
# SMBus/I2C™ compatible serial port
# Temperature resolution is 1°C
# TC74A0-3.3VCT ==> Slave Address 0x48  
"""
import time
from tc74 import TC74

tc74 = TC74(sda ='P9',scl='P10',name = 'sensor tc74') 

idx = 1200000
while idx > 0 :
    print ('payload :{}'.format(tc74.getPayload())) 
    idx -=1
    time.sleep(10) 


