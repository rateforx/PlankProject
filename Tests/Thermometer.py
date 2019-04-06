from w1thermsensor import W1ThermSensor
import time

temp0 = W1ThermSensor( sensor_id = '00000a01a45b' )
temp1 = W1ThermSensor( sensor_id = '00000a02e5e8' )

while True:
    print( 'Temp0: {}'.format( temp0.get_temperature()) )
    print( 'Temp1: {}'.format( temp1.get_temperature()) )