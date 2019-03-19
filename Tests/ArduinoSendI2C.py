import smbus
from time import sleep

bus = smbus.SMBus( 1 )
sleep( 1 )
arduinoAddress = 0x42


def read( ):
    b = [ 0 ] * 4
    sign   = bus.read_byte( arduinoAddress ) # 0 -> +, 1 -> -
    b[ 0 ] = bus.read_byte( arduinoAddress )
    b[ 1 ] = bus.read_byte( arduinoAddress )
    b[ 2 ] = bus.read_byte( arduinoAddress )
    b[ 3 ] = bus.read_byte( arduinoAddress )

    print( sign, b )

    data = ( b[ 3 ] << 24 ) | ( b[ 2 ] << 16 ) | ( b[ 1 ] << 8 ) | b[ 0 ]
    if sign == 1:
        data = - data

    # print(sign, '{}{:b}'.format( b, b ), data)
    if data > pow( 2, 31 ):
        data = data - pow( 2, 32 )
    # if data == -0:
    #     data = 0
    return data

lastCount = 0

while True:
    count = read()
    if lastCount != count:
        print( '{}\t{:b}'.format( count, count ) )
        lastCount = count
    sleep( 1 / 60 )
