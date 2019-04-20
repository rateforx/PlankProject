from Plank.ArduinoSerialPortFinder import ArduinoSerialPortFinder
from serial import Serial
import time

baudrate = 115200
timeout = .25

OUTPUT = 0
INPUT = 1
INPUT_PULLUP = 2

LOW = 0
HIGH = 1

FALLING = 0
RISING = 1
BOTH = 2


class __ArduinoIO:

    def __init__( self, serialNumber ):
        self.port = ArduinoSerialPortFinder.getArduinoPort( serialNumber )
        self.serial = Serial( self.port, baudrate, timeout = timeout )
        time.sleep( 1 )

    def setMode( self, pin, mode ):
        self.serial.write( 'm({},{})'.format( pin, mode ).encode( ) )

    def write( self, pin, value ):
        self.serial.write( 'w({},{})'.format( pin, value ).encode( ) )

    def read( self, pin ) -> int:
        self.serial.write( 'r({})'.format( pin ).encode( ) )
        data = self.serial.readline( ).decode( ).strip( '\r\n' )
        value = None
        try:
            value = int( float( data ) )
        except ValueError:
            value = None
        finally:
            return value

    def analogRead( self, pin ):
        self.serial.write( 'a({})'.format( pin ).encode( ) )
        return float( self.serial.readline( ).decode( ).strip( "\r\n" ) )

    def _blink( self, pin, value, duration = 1 ):
        self.write( pin, value )
        time.sleep( duration )
        self.write( pin, int( not value ) )


if __name__ == '__main__':
    pass
    # arduinoIO = ArduinoIO( ArduinoSerialPortFinder.ARDUINO_MEGA_SERIAL_NUMBER )
