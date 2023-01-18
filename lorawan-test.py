# >exec(open('lorawan-test.py').read())

from network import LoRa
import socket
import time
import binascii,ubinascii

# Initialise LoRa in LORAWAN mode.
# Please pick the region that matches where you are using the device:
# Asia = LoRa.AS923
# Australia = LoRa.AU915
# Europe = LoRa.EU868
# United States = LoRa.US915
lora = LoRa(mode=LoRa.LORAWAN, region=LoRa.EU868,adr=True)

# create an OTAA authentication parameters, change them to the provided credentials
#-- HUA-RT Setup 
#app_eui = ubinascii.unhexlify('a2-6c-05-58-7f-96-cc-6a'.replace('-',''))
#app_key = ubinascii.unhexlify('0a-3f-dd-ce-8e-29-f3-ba-a9-9a-d0-a4-65-87-ef-be'.replace('-',''))

#-- TTN Polytech Gallile 
app_eui = ubinascii.unhexlify('45-43-4F-4C-45-49-4F-54'.replace('-',''))
app_key = ubinascii.unhexlify('0a-3f-dd-ce-8e-29-f3-ba-a9-9a-d0-a4-65-87-ef-be'.replace('-',''))

dev_eui =  binascii.hexlify(lora.mac())

print(('dev_EUI : {}'.format(dev_eui)))

#uncomment to use LoRaWAN application provided dev_eui
#dev_eui = ubinascii.unhexlify('70B3D549938EA1EE')

# join a network using OTAA (Over the Air Activation)
#uncomment below to use LoRaWAN application provided dev_eui
lora.join(activation=LoRa.OTAA, auth=(app_eui, app_key), timeout=0)

# wait until the module has joined the network
while not lora.has_joined():
    print('Not yet joined...')
    time.sleep()

print('Joined')
# create a LoRa socket
s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)

# set the LoRaWAN data rate
s.setsockopt(socket.SOL_LORA, socket.SO_DR, 0)

count = 10
idx = 0 
while idx < count  : 
    # make the socket blocking
    # (waits for the data to be sent and for the 2 receive windows to expire)
    s.setblocking(True)

    # send some data
    print('send data..[123]  idx:{}/{}'.format(idx,count))
    rc = s.send(b'123')
    print('sent {} bytes'.format(rc))

    # make the socket non-blocking
    # (because if there's no data received it will block forever...)
    s.setblocking(False)

    print("OK") 
    idx +=1 
    time.sleep(60)

# get any data received (if any...)
data = s.recv(64)
print(data)