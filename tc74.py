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


class TC74_OLD:
    VARIANT = ENUM_VARIANT
    UNIT = ENUM_UNIT

    def __init__(self, variant):
        self.variant = variant
        self.i2c = None

    def init(self, scl= 'P10', sda= 'P9', freq = 400000):
        from machine import I2C, Pin

        self.i2c = I2C(0, pins =(sda , scl ))
        self.i2c.init(I2C.MASTER, baudrate = freq )

        self.disable_standby()

    def read_temp(self, unit=UNIT.Celsius):
        """ Read temperature value from TEMPERATURE register """
        if self.i2c is None:
            raise TypeError("i2c is not defined did you call the init method?")


        """
        err_count = 0
        while err_count < 3:
            try:
                self.i2c.writeto(self.variant, bytearray([_TEMP_REG]))
            except OSError:
                if err_count > 2:
                    raise OSError("Cannot write to I2C-bus.")
                err_count += 1
            break

        utime.sleep_ms(1)

        data = bytearray(1)
        self.i2c.readfrom_into(self.variant, data)
        """
        data = self.i2c.readfrom_mem(self.variant,_TEMP_REG, 1)
        return self._extract_value_from_buffer(int(data[0]), unit)


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
        data = self.i2c.readfrom_mem(self.variant,_CFG_REG, 1)
        return (data[0] == 0x40 )


    def is_standby(self):
        """ Check if chip is in standby mode """
        data = self.i2c.readfrom_mem(self.variant,_CFG_REG, 1)

        if data[0] == 0x40:
            return 0
        elif data[0] == 0x80:
            return 1
        else:
            return -1


