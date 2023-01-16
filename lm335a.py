"""
# -- LM335A  -40° to +100°  10mV/°K  range 3-14 mV 
#reverse voltage mV 5mv a 25°  
# current of 400uA to 5 mA.  working voltage 2.95V to 3.01V 
# the ADC of ESP is not very good. It is nonlinear and noisy. 
# It might be advisable instead of a single value to take the average of several values.

adc = machine.ADC()             # create an ADC object
adc_pin = adc.channel(pin='P16',attn=machine.ADC.ATTN_11DB)   # create an analog pin on P16

"""
from machine import ADC, Timer
from struct import pack
from logger import  LOGGER

class LM335A : 
    """ LM335A Temperatrue Sensor Class  """
    class StackData : 
        SIZE = 10 
        def __init__(self):
            self.buffer = []    
            LOGGER.log('LM335A:StackData:init()','buffer: {}'.format(self.buffer))

        def push(self,value):
            if not isinstance(value, float) :
                LOGGER.log('LM335A:StackData:push()','bad value format {}'.format(value)  )
            else : 
                if len(self.buffer) >= LM335A.StackData.SIZE : 
                    self.buffer.pop(0)       
                self.buffer.append(value)
                LOGGER.log('LM335A:StackData:push()','value:{} buffer:{}'.format(value, self.buffer))

        def getAvgValue(self):
            items = len(self.buffer) 
            if items > 0 :
                return round(sum(self.buffer) / items , 1 )      
            else :
                return 0.0 

        def isReady(self) :
            return (len(self.buffer) >= LM335A.StackData.SIZE )

    DELTA_TEMP = 0.5 # ° 

    def __init__(self, name, pin , sampling_point = 10 ):

        self.name = name
        self.value = 0.0
        self.default = 0

        self.value_last = self.value
        self.default_last = self.default

        self.adc =  ADC() 
        self.sensor = self.adc.channel(pin=pin,attn=ADC.ATTN_11DB)  
        self.stack = LM335A.StackData()

        self.__alarm = Timer.Alarm(self._top_handler, sampling_point , periodic=True)
        LOGGER.log('LM335A:init()','Pin:{}  sampling:{} Sec. '.format(pin,sampling_point) )

    def _top_handler(self, alarm) : 
        self.read()

    def __del__(self) :
        self.__alarm.cancel()

    def isReady(self) : 
        return self.stack.isReady() 

    def read(self) : 

        adc_value  = self.sensor()
        voltageIn = int((adc_value * 3300) / 4096) 
        temperatureK = voltageIn / 10
        temperatureC = temperatureK - 270          # 273 
        temperatureF = (temperatureC * 1.8) + 32
        self.value = round(temperatureC , 1)
        
        self.default = 0x0 
        self.default = self.default | ( voltageIn == 0  ) 
        self.default = self.default | ( temperatureC > 35.0 ) << 1 
        self.default = self.default | ( temperatureC <  5.0 ) << 2  

        if (self.default == 0 ) : 
            self.stack.push(self.value)
        else : 
            LOGGER.log('LM335A:read()','ERROR: default:{}'.format(self.default) )

    def process(self) : 

        if not self.isReady() :
            return None 
        
        # 'E'vent on default 
        if ( self.default ^ self.default_last ) :
            self.default_last = self.default
            LOGGER.log('LM335A:process()','New default: {}'.format(self.default) ) 
            return self.getPayload()
        elif abs(self.value - self.value_last)  > LM335A.DELTA_TEMP :
            self.value_last = self.value 
            LOGGER.log('LM335A:process()','Sensor new Temp. value: {}'.format(self.value) )
            return self.getPayload()
        else : 
            return None

    def getPayload(self, event = 'E') : 
        return { 'event': event ,'temp': self.stack.getAvgValue() ,'default' : self.default }

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