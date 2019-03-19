from serial import Serial
from Plank.ArduinoSerialPortFinder import getArduinoPort

port = getArduinoPort()
baudrate = 9600

serial = Serial( port, baudrate )

print( 'Started serial communication with Arduino at: {}'.format( port ) )

while True:
    try:
        print( int( serial.readline() ) )
    except KeyboardInterrupt:
        serial.close()
