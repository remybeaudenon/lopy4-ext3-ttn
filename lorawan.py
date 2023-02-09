from network import LoRa
from ws2812led import LED
from logger import  Logger

import socket
import time
import binascii,ubinascii

class ENUM_GATEWAY : 
    HUA = ('HUA','a2-6c-05-58-7f-96-cc-6a','0a-3f-dd-ce-8e-29-f3-ba-a9-9a-d0-a4-65-87-ef-be') # EUI, KEY 
    TTN = ('TTN','45-43-4F-4C-45-49-4F-54','0a-3f-dd-ce-8e-29-f3-ba-a9-9a-d0-a4-65-87-ef-be') # 
    CGA = ('CGA','3a-35-82-19-8f-0d-95-4d','81-d8-0e-e8-26-50-ad-29-82-b1-0e-37-db-ac-d6-6e') # 

_GTW_NAME       = 0
_GTW_APP_EUI    = 1
_GTW_APP_KEY    = 2


class LoRaWAN(LoRa) : 
    """ Dedicated LoRaWan instance for HUA+Multitech Hub  """
    PAYLOAD_MAX_SIZE = 12 
    def __init__(self):

        self.socket = None

        self.logger = Logger.getInstance()    

        # Init LoRa Mode & Region 
        LoRa(mode=LoRa.LORAWAN, region=LoRa.EU868,adr=True)

        #uncomment to use LoRaWAN application provided dev_eui
        #dev_eui = ubinascii.unhexlify('----------------') # replace the dash by the DevEUI provided.
        self.dev_eui =  binascii.hexlify(super().mac()).upper()

        self.simulation = False
        # DevEUI :  70-b3-d5-49-98-fa-f7-0f
        self.logger.log('LoRaWAN:init()','DevEUI : {}'.format(self.dev_eui))

    def join(self,gateway) : 

        gateway_code,gateway_app_eui,gateway_app_key = gateway  
        self.init(mode=LoRa.LORAWAN, tx_power=14, adr=False ,tx_retries=3, sf=12, \
                    region=LoRa.EU868,bandwidth=LoRa.BW_125KHZ,device_class=LoRa.CLASS_C)

        app_eui = ubinascii.unhexlify(gateway_app_eui.replace('-',''))
        app_key = ubinascii.unhexlify(gateway_app_key.replace('-',''))

        super().join(activation=LoRa.OTAA,auth=(app_eui,app_key),timeout=0,dr=0)

        try_index = 3
        while not super().has_joined() and try_index > 0 :
            time.sleep(5)
            self.logger.log('LoRaWAN:join()','Not yet joined awaiting..{} gateway try:{}'.format(gateway_code,try_index))
            try_index -=1
        time.sleep(3)

        if  try_index == 0 : 
            self.logger.log('LoRaWAN:join()','Error Gateway Join() MODE SIMULATION activated!!! ') 
            self.setSimulation(True)
            LED.getInstance().pulse(LED.RED,3000)

        else :
            self.logger.log('LoRaWAN:join()','CONNECTED !! to LoRa station ' ) 
            # create a LoRa socket
            time.sleep(1)
            self.socket = socket.socket(socket.AF_LORA, socket.SOCK_RAW)
            self.socket.settimeout(3)
            # set the LoRaWAN data rate
            self.socket.setsockopt(socket.SOL_LORA, socket.SO_DR, 0)
            # selecting non-confirmed type of messages
            self.socket.setsockopt(socket.SOL_LORA, socket.SO_CONFIRMED, False)

    def show(self) : 
        pass

    def setSimulation(self,state) : 
        self.logger.log('LoRaWAN:setSimulation()','MODE SIMULATION activé !!! ') 
        self.simulation = state    

    def isInSimulation(self) : 
        return  (self.simulation == True )     

    def send(self, telegram) : 

        if isinstance(telegram, bytearray) or isinstance(telegram, bytes) :

            if self.simulation : 
                self.logger.log('LoRaWAN:send()','Push  SIMULATION LoRa Payload:[{}] device eui:{} '.format(telegram,self.dev_eui )  ) 
                LED.getInstance().setState(LED.CYAN)
                time.sleep(2)  
                # LoRa Duty cycle applied 
                LED.getInstance().setState(LED.INDIGO)
                time.sleep(30)  
                LED.getInstance().setState(LED.OFF)

            elif len(telegram) < LoRaWAN.PAYLOAD_MAX_SIZE :
                self.logger.log('LoRaWAN:send()','Push LoRa Payload:[{}] device eui:{} '.format(telegram,self.dev_eui )  ) 
                LED.getInstance().setState(LED.CYAN)
                self.socket.setblocking(True)
                lg = self.socket.send(telegram)
                self.socket.setblocking(False)

                # LoRa Duty cycle applied 
                LED.getInstance().setState(LED.INDIGO)
                time.sleep(60) 
                LED.getInstance().setState(LED.OFF)
 

            else : 
                self.logger.log('LoRaWAN:send()','ERROR!! Payload size error : {}'.format(len(telegram)  ) ) 
        else :
            self.logger.log('LoRaWAN:send()','ERROR!! Payload format not bytearray or bytes: {}'.format( telegram) ) 
