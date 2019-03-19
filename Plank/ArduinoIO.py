from Plank.ArduinoSerialPortFinder import ArduinoSerialPortFinder
from serial import Serial
import time

baudrate = 9600
timeout = 1

OUTPUT = 0
INPUT = 1
INPUT_PULLUP = 2

LOW = 0
HIGH = 1


class ArduinoIO:

    def __init__( self, serialNumber ):
        self.port = ArduinoSerialPortFinder.getArduinoPort( serialNumber )
        self.serial = Serial( self.port, baudrate, timeout = timeout )
        self.read( 0 )
        self.read( 0 )
        time.sleep( 3 )


    def setMode( self, pin, mode ):
        self.serial.write( 'm({},{})'.format( pin, mode ).encode( ) )

    def write( self, pin, value ):
        self.serial.write( 'w({},{})'.format( pin, value ).encode( ) )

    def read( self, pin ) -> int:
        self.serial.write( 'r({})'.format( pin ).encode( ) )
        time.sleep( .05 )
        return int( self.serial.readline( ).decode( ).strip( "\r\n" ) )

    def _blink( self, pin, value, duration = 1 ):
        self.write( pin, value )
        time.sleep( duration )
        self.write( pin, int( not value ) )


if __name__ == '__main__':
    arduinoIO = ArduinoIO( ArduinoSerialPortFinder.ARDUINO_MEGA_SERIAL_NUMBER )
