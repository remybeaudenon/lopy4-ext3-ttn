from network import LoRa
import binascii
lora = LoRa()
dev_eui =  binascii.hexlify(lora.mac())
print('dev_EUI : {}'.format(dev_eui))
