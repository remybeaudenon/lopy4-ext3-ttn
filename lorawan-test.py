# >exec(open('lorawan-test.py').read())

from network import LoRa
import socket
import time
import binascii,ubinascii

# Initialise LoRa in LORAWAN mode.
lora = LoRa(mode=LoRa.LORAWAN, region=LoRa.EU868,adr=True)

# create an OTAA authentication parameters, change them to the provided credentials
#-- TTN Polytech Gallile 
app_eui = ubinascii.unhexlify('45-43-4F-4C-45-49-4F-54'.replace('-',''))
app_key = ubinascii.unhexlify('0a-3f-dd-ce-8e-29-f3-ba-a9-9a-d0-a4-65-87-ef-be'.replace('-',''))

dev_eui =  binascii.hexlify(lora.mac())
# uncomment to use LoRaWAN application provided dev_eui
# dev_eui = ubinascii.unhexlify('70B3D549938EA1EE')
print(('dev_EUI : {}'.format(dev_eui)))

# join a network using OTAA (Over the Air Activation)
lora.join(activation=LoRa.OTAA, auth=(app_eui, app_key), timeout=0)

# wait until the module has joined the network
while not lora.has_joined():
    print('Not yet joined...')
    time.sleep(3)

print('Joined')
# create a LoRa socket
s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)

# set the LoRaWAN data rate
s.setsockopt(socket.SOL_LORA, socket.SO_DR, 0)

count = 5
idx = 0 
while idx < count  : 
    # make the socket blocking
    # (waits for the data to be sent and for the 2 receive windows to expire)
    s.setblocking(True)

    # send some data
    #print('send data..[123]  idx:{}/{}'.format(idx,count))
    #rc = s.send(b'123')

    payload = bytearray(0)
    payload.extend( bytearray( b'\x01\x45\x03\x00\x02\x36\x01')) #  
    rc = s.send(payload)
    print('sent {} {} bytes'.format(payload, rc))
   
    # make the socket non-blocking
    # (because if there's no data received it will block forever...)
    s.setblocking(False)

    print("Sent !") 
    idx +=1 
    time.sleep(60)

# get any data received (if any...)
data = s.recv(64)
print(data)