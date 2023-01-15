from network import LoRa
from ws2812led import LED
from logger import  LOGGER

import socket
import time
import binascii,ubinascii


class LoRaWAN(LoRa) : 

    PAYLOAD_MAX_SIZE = 12 

    #-- HUA-RT Setup 
    APP_EUI = ubinascii.unhexlify('a2-6c-05-58-7f-96-cc-6a'.replace('-',''))
    APP_KEY = ubinascii.unhexlify('0a-3f-dd-ce-8e-29-f3-ba-a9-9a-d0-a4-65-87-ef-be'.replace('-',''))

    #-- TTN Polytech Gallile 
    #APP_EUI = ubinascii.unhexlify('45-43-4F-4C-45-49-4F-54'.replace('-',''))
    #APP_KEY = ubinascii.unhexlify('0a-3f-dd-ce-8e-29-f3-ba-a9-9a-d0-a4-65-87-ef-be'.replace('-',''))

    def __init__(self):

        self.socket = None 
        #uncomment to use LoRaWAN application provided dev_eui
        #dev_eui = ubinascii.unhexlify('----------------') # replace the dash by the DevEUI provided.
        self.dev_eui =  binascii.hexlify(super().mac()).upper()

        # DevEUI :  70-b3-d5-49-98-fa-f7-0f
        LOGGER.log('LoRaWAN:init()','DevEUI : {}'.format(self.dev_eui)) 
        # super().nvram_save() # if there is nothing to restore it will return a False

    def join(self) : 

        self.init(mode=LoRa.LORAWAN, tx_power=14, adr=False ,tx_retries=3, sf=12, \
                    region=LoRa.EU868,bandwidth=LoRa.BW_125KHZ,device_class=LoRa.CLASS_C)

        super().join(activation=LoRa.OTAA,auth=(LoRaWAN.APP_EUI,LoRaWAN.APP_KEY),timeout=0,dr=0)

        while not super().has_joined():
            time.sleep(5)
            LOGGER.log('LoRaWAN:join()','Not yet joined awaiting...')
        LOGGER.log('LoRaWAN:join()','CONNECTED !! to LoRa station ' ) 
        time.sleep(1)
        # create a LoRa socket
        self.socket = socket.socket(socket.AF_LORA, socket.SOCK_RAW)
        self.socket.settimeout(3)

        # set the LoRaWAN data rate
        self.socket.setsockopt(socket.SOL_LORA, socket.SO_DR, 0)

        # selecting non-confirmed type of messages
        self.socket.setsockopt(socket.SOL_LORA, socket.SO_CONFIRMED, False)

    def show(self) : 
        pass

    def send(self, telegram) : 

        if isinstance(telegram, bytearray) or isinstance(telegram, bytes) :
            if len(telegram) < LORAWAN.PAYLOAD_MAX_SIZE :
                LOGGER.log('LoRaWAN:send()','Push LoRa Payload:[{}] device eui:{} '.format(telegram,self.dev_eui )  ) 
                LED.getInstance().setState(LED.RED)
                self.socket.setblocking(True)
                lg = self.socket.send(telegram)
                self.socket.setblocking(False)

                LED.getInstance().setState(LED.INDIGO)
                time.sleep(60) #  LorA duty cycle 

            else : 
                LOGGER.log('LoRaWAN:send()','ERROR!! Payload size error : {}'.format(len(telegram)  ) ) 
        else :
            LOGGER.log('LoRaWAN:send()','ERROR!! Payload format not bytearray or bytes: {}'.format( telegram) ) 
