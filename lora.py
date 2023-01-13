from network import LoRa
from ws2812led import LED
from logger import  LOGGER

import socket
import time
import binascii,ubinascii

class LORAWAN : 

    PAYLOAD_MAX_SIZE = 12 
    
    #-- HUA-RT Setup 
    APP_EUI = ubinascii.unhexlify('a2-6c-05-58-7f-96-cc-6a'.replace('-',''))
    APP_KEY = ubinascii.unhexlify('0a-3f-dd-ce-8e-29-f3-ba-a9-9a-d0-a4-65-87-ef-be'.replace('-',''))

    def __init__(self):

        self.lora = LoRa(mode=LoRa.LORAWAN, tx_power=14, adr=False ,tx_retries=3, sf=12, \
                    region=LoRa.EU868,bandwidth=LoRa.BW_125KHZ,device_class=LoRa.CLASS_C)

        self.socket = None 
        #uncomment to use LoRaWAN application provided dev_eui
        #dev_eui = ubinascii.unhexlify('----------------') # replace the dash by the DevEUI provided.
        self.dev_eui =  binascii.hexlify(self.lora.mac()).upper()

        # DevEUI :  b'70B3D5499050BFC1'
        LOGGER.log('LORAWAN:init()','DevEUI : {}'.format(self.dev_eui)) 
        self.lora.nvram_save() # if there is nothing to restore it will return a False

    def join(self) : 

        self.lora.join(activation=LoRa.OTAA,  auth=(self.dev_eui, LORAWAN.APP_EUI , LORAWAN.APP_KEY), timeout=0, dr=0)
        while not self.lora.has_joined():
            time.sleep(5)
            LOGGER.log('LORAWAN:join()','Not yet joined awaiting...')
        LOGGER.log('LORAWAN:join()','CONNECTED !! to LoRa station ' ) 

        # create a LoRa socket
        self.socket = socket.socket(socket.AF_LORA, socket.SOCK_RAW)
        self.socket.settimeout(3)

        # set the LoRaWAN data rate
        self.socket.setsockopt(socket.SOL_LORA, socket.SO_DR, 0)

        # selecting non-confirmed type of messages
        self.socket.setsockopt(socket.SOL_LORA, socket.SO_CONFIRMED, False)

        # make the socket blocking
        self.socket.setblocking(True)

    def show(self) : 
        pass

    def has_joined(self) : 
        return self.lora.has_joined()

    def send(self, telegram) : 

        if isinstance(telegram, bytearray) or isinstance(telegram, bytes) :
            if len(telegram) < LORAWAN.PAYLOAD_MAX_SIZE :
                LOGGER.log('LORAWAN:send()','Push LoRa Payload:[{}] device eui:{} '.format(telegram,self.dev_eui )  ) 
                LED.getInstance().setState(LED.RED)
                self.socket.send(telegram)
                LED.getInstance().setState(LED.INDIGO)
                time.sleep(60) #  LorA duty cycle 

            else : 
                LOGGER.log('LORAWAN:send()','ERROR!! Payload size error : {}'.format(len(telegram)  ) ) 
        else :
            LOGGER.log('LORAWAN:send()','ERROR!! Payload format not bytearray or bytes: {}'.format( telegram) ) 







