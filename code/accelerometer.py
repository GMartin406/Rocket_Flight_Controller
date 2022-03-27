import machine
import utime
import ustruct
import sys

LIS3DH_ADDR = 0x53

REG_DEVID = 0x00
REG_POWER_CTL = 0x2D
REG_DATAX0 = 0x32

DEVID = 0xE5
SENSITIVITY_2G = 1.0/256
EARTH_GRAVITY_MS2 = 9.80665


########################################################################
i2c = machine.I2C(0, scl=machine.Pin(17), sda=machine.Pin(16), freq=400000)
########################################################################


def reg_write(i2c, addr, reg, data):

    msg = bytearray()
    msg.append(data)
    i2c.writeto_mem(addr, reg, data)

def reg_read(i2c, addr, reg, nbytes=1):
    
    if nbytes < 1:
        return bytearray()
    
    data = i2c.readfrom_mem(addr, reg, nbytes)
    
    return data

########################################################################

#Main

#Read the device ID to make sure we can communicate with LIS3DH
data = reg_read(i2c, LIS3DH_ADDR, REG_DEVID)
if(data != bytearray((DEVID,))):
    print("ERROR: Could not find LIS3DH")

#Read Power Control Register
data = reg_read(i2c, LIS3DH_ADDR, REG_POWER_CTL)
print(data)

#Tell LIS3DH to start measuring by setting Measure bit to High
data = int.from_bytes(data, "big") | (1 << 3)
reg_write(i2c, LIS3DH_ADDR, REG_POWER_CTL, data)

#Test: read Power Control Register back to make sure Measure bit is High
data = reg_read(i2c, LIS3DH_ADDR, REG_POWER_CTL)
print(data)

#Wait before reading data
utime.sleep(2.0)

#Run forever
while True:
    #Read X, Y, Z axis data
    data = reg_read(i2c, LIS3DH_ADDR, REG_DATAX0, 6)

    #convert 2 bytes into 16-bit integer(signed)
    acc_x = ustruct.unpack_from("<h", data, 0)[0]
    acc_y = ustruct.unpack_from("<h", data, 2)[0]
    acc_z = ustruct.unpack_from("<h", data, 4)[0]

    #convert measurement into g's
    acc_x = acc_x * SENSITIVITY_2G * EARTH_GRAVITY_MS2
    acc_y = acc_y * SENSITIVITY_2G * EARTH_GRAVITY_MS2
    acc_z = acc_z * SENSITIVITY_2G * EARTH_GRAVITY_MS2

    print("X:", "{:.2f}".format(acc_x), \
        "| Y:", "{:.2f}".format(acc_y), \
        "| Z:", "{:.2f}".format(acc_z))

    utime.sleep(0.1)