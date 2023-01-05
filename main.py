from network import LoRa
import socket
import time
from struct import pack
import struct
import ubinascii
import binascii
import pycom

def connect_to_ttn(lora_object):
    """Receives a lora object and tries to join"""
    # join a network using OTAA (Over the Air Activation),
    # choose dr = 0 if the gateway is not close to your device, try different dr if needed
    lora_object.join(activation=LoRa.OTAA, auth=(dev_eui, app_eui, app_key), timeout=0, dr=0)
    # wait until the module has joined the network
    pycom.rgbled(0x7f7f00) #yellow
    while not lora_object.has_joined():
        time.sleep(2.5)
        print('Not yet joined...')
        lora.nvram_erase()
        

def getHexPayload( json) :
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


pycom.heartbeat(False)


#-- HUA-RT Setup 
app_eui = ubinascii.unhexlify('a2-6c-05-58-7f-96-cc-6a'.replace('-',''))
app_key = ubinascii.unhexlify('0a-3f-dd-ce-8e-29-f3-ba-a9-9a-d0-a4-65-87-ef-be'.replace('-',''))

#-- TTN-KL setup  
#app_eui = ubinascii.unhexlify('45-43-4F-4C-45-49-4F-54'.replace('-',''))
#app_key = ubinascii.unhexlify('63-96-54-A5-3C-CC-7B-75-5A-8D-53-27-54-C8-42-22'.replace('-',''))

pycom.rgbled(0xff0000) #red
time.sleep(1)

lora = LoRa(mode=LoRa.LORAWAN, region=LoRa.EU868, device_class=LoRa.CLASS_C)

#uncomment to use LoRaWAN application provided dev_eui
#dev_eui = ubinascii.unhexlify('----------------') # replace the dash by the DevEUI provided to TTN
dev_eui =  binascii.hexlify(lora.mac()).upper()

# DevEUI :  b'70B3D5499050BFC1'
print('DevEUI : ', dev_eui)
lora.nvram_restore() #if there is nothing to restore it will return a False

connect_to_ttn(lora)

print("CONNECTED!!")
pycom.rgbled(0x00ff00) #green

print('LoRa stats : {} '.format(lora.stats() ) ) 

# create a LoRa socket
s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)

# set the LoRaWAN data rate
s.setsockopt(socket.SOL_LORA, socket.SO_DR, 0)

# make the socket blocking
s.setblocking(True)

for i in range (5):

    payload = { 'event': 'E' ,'temp': 18.5 ,'default' : 0x00  }
    pkt = getHexPayload(payload)
    print('Sending:', pkt)
    s.send(pkt)
    time.sleep(4)
    # without downlink transmission first
    #rx, port = s.recvfrom(256)
    #if rx:
    #    print('Received: {}, on port: {}'.format(rx, port))
    print('LoRa stats : {} '.format(lora.stats() ) ) 

    time.sleep(26)

