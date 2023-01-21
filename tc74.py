"""
# -- TC74  -40°C to +125°C Temp Range   
# -- low power - 200µA Operating
# Communication with the TC74 is accomplished via a 2-wire 
# SMBus/I2C™ compatible serial port
# Temperature resolution is 1°C
# TC74A0-3.3VCT ==> Slave Address 0x48  
# from tc74 import TC74
# >>> tc74 = TC74(TC74.VARIANT.A0)
# >>> tc74.init(scl= 'P10', sda= 'P9')
# >>> tc74.read_temp(tc74.UNIT.Celsius)
# 17
"""

import utime
from machine import Timer,I2C, Pin

from struct import pack
from logger import  LOGGER

#region Commands
_CFG_REG = 0x01
_TEMP_REG = 0x00
_PWRSAVE = 0x80
_NOPWRSAVE = 0x00
_NEGATIVE = 0x80
#endregion

#region Address constants
class ENUM_VARIANT:
    A0 = 0x48
    A1 = 0x49
    A2 = 0x4A
    A3 = 0x4B
    A4 = 0x4C
    A5 = 0x4D
    A6 = 0x4E
    A7 = 0x4F
#endregion

#region Units
class ENUM_UNIT:
    Celsius = 0
    Fahrenheit = 1
#endregion
class TC74 : 
    """ TC74  I2C Temperatrue Sensor Class  """
    class StackData : 
        SIZE = 3
        def __init__(self):
            self.buffer = []    
            LOGGER.log('TC74:StackData:init()','buffer: {}'.format(self.buffer))

        def push(self,value):
            if not isinstance(value, float) :
                LOGGER.log('TC74:StackData:push()','bad value format {}'.format(value)  )
            else : 
                if len(self.buffer) >= TC74.StackData.SIZE : 
                    self.buffer.pop(0)       
                self.buffer.append(value)
                LOGGER.log('TC74:StackData:push()','value:{} buffer:{}'.format(value, self.buffer))

        def getAvgValue(self):
            items = len(self.buffer) 
            if items > 0 :
                return round(sum(self.buffer) / items , 1 )      
            else :
                return 0.0 

        def isReady(self) :
            return (len(self.buffer) >= TC74.StackData.SIZE )

    DELTA_TEMP      = 0.5 # ° 
    I2C_FREQUENCE   = 400000
    VARIANT         = ENUM_VARIANT
    UNIT            = ENUM_UNIT

    def __init__(self, sda , scl, name='tc74', variant = VARIANT.A0,sampling_point = 10):
        self.name = name
        self.value = 0.0
        self.default = 0

        self.value_last = self.value
        self.default_last = self.default

        self.variant = variant
        self.i2c = I2C(I2C.MASTER, pins = (sda,scl) , baudrate = TC74.I2C_FREQUENCE) # pins (P9=SDA, P10=SCL) 
        
        self.stack = TC74.StackData()
        self.__alarm = Timer.Alarm(self._top_handler, sampling_point , periodic=True)
        LOGGER.log('TC74:init()','name:{} variant:{} sampling:{} '.format(name,hex(variant), sampling_point) )

    def _top_handler(self, alarm) : 

        if not self.is_data_ready() : 
            self.disable_standby()
        self.read()

    def __del__(self) :
        self.__alarm.cancel()

    def isReady(self) : 
        return self.stack.isReady() 

    def read(self) : 

        """ Read temperature value from TEMPERATURE register """
        if self.i2c is None:
            raise TypeError("i2c is not defined did you call the init method?")

        try :    
            data = self.i2c.readfrom_mem(self.variant,_TEMP_REG, 1)
            value  = self._extract_value_from_buffer(int(data[0]), ENUM_UNIT.Celsius)
            self.value = float(value)
            self.default = 0x0 
        except(OSError) as err : 
            self.default = 0x08    

        self.default = self.default | ( self.value > 35.0 ) << 1 
        self.default = self.default | ( self.value <  5.0 ) << 2  

        if (self.default == 0 ) : 
            self.stack.push(self.value)
        else : 
            LOGGER.log('TC74:read()','ERROR: default:{}'.format(self.default) )

    def _extract_value_from_buffer(self, temp, unit):
        # --- Two's complement conversion ---
        if temp & _NEGATIVE:
            temp = -1 * ((temp ^ 255) + 1)
        # --- --------------------- ---

        if unit == self.UNIT.Celsius:
            return temp
        elif unit == self.UNIT.Fahrenheit:
            return (temp * 9.0) / 5.0 + 32
        else:
            raise NotImplementedError("This unit is not implemented.")

    def enable_standby(self):
        """Put the device in low power. In this mode A/D converter is
        halted and temperature data registers are frozen"""
        self.i2c.writeto(self.variant, bytearray([_CFG_REG]) + bytearray([_PWRSAVE]))

    def disable_standby(self):
        """Disable the low power mode. A/D converter will be resumed"""
        self.i2c.writeto(self.variant, bytearray([_CFG_REG]) + bytearray([_NOPWRSAVE]))
        utime.sleep_ms(250)

    def is_data_ready(self):
        """ Check if chip is  data ready  """
        try:
            data = self.i2c.readfrom_mem(self.variant,_CFG_REG, 1)
            return (data[0] == 0x40 )
        except(OSError) as err:
            return 0 

    def is_standby(self):
        """ Check if chip is in standby mode """
        data = self.i2c.readfrom_mem(self.variant,_CFG_REG, 1)

        if data[0] == 0x40:
            return 0
        elif data[0] == 0x80:
            return 1
        else:
            return -1
    
    def process(self) : 

        if not self.isReady() :
            return None 
        
        # 'E'vent on default 
        if ( self.default ^ self.default_last ) :
            self.default_last = self.default
            LOGGER.log('TC74:process()','New default: {}'.format(self.default) ) 
            return self.getPayload()
        elif abs(self.stack.getAvgValue() - self.value_last)  >= TC74.DELTA_TEMP :
            self.value_last = self.value 
            LOGGER.log('TC74:process()','Sensor new Temp. value: {}'.format(self.value) )
            return self.getPayload()
        else : 
            return None

    def getPayload(self, event = 'E') : 
        return { 'event': event ,'temp': self.stack.getAvgValue() ,'name':self.name ,'default' : self.default }

    @staticmethod
    def getHexPayload(json) :
        payload = bytearray(0)
        if 'event' in json :  
            payload.extend( bytearray( b'\x01' +  pack('s',json.get('event')) ))
        if 'default' in json :  
            error_code = json.get('default')
            payload.extend( bytearray( b'\x03' +  pack('B', error_code )))
        if error_code == 0  and 'temp' in json : 
            temp = int( json.get('temp') * 10 )
            payload.extend( bytearray( b'\x02' +  pack('<H',temp) ))  # little-endian 
        return payload 
