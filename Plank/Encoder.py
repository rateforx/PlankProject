import time
from serial import Serial
from Plank.ArduinoSerialPortFinder import *

baudrate = 115200
timeout = 5


class Encoder:
    lastCount = None
    verbose = False
    readCounter = 0

    def __init__( self, arduinoSN ):
        port = ArduinoSerialPortFinder.getArduinoPort( arduinoSN )
        print( 'Connecting to Arduino serial: {}'.format( port ) )
        self.serial = Serial( port, baudrate, timeout = timeout )
        time.sleep( .25 )
        # self.getCounter( )

    # def requestCounter( self ):
    #     self.serial.write( 'r'.encode( ) )

    def getCounter( self ):
        # self.serial.write( 'r'.encode( ) )
        # value = int( self.serial.readline( ).decode( ).strip( "\r\n" ) )

        self.readCounter += 1

        try:
            self.serial.flush( )
            self.serial.write( 'r'.encode( ) )
            value = int( self.serial.readline( ).decode( ).strip( "\r\n" ) )

        except ValueError:
            self.serial.flush( )
            self.serial.write( 'r'.encode( ) )
            value = self.getCounter( )  # if nothing sent, retry

        if self.verbose:
            print( "{}: {}".format( self.readCounter, value ) )

        return value

    # def start( self ):
    #     while True:
    #         print( int( self.serial.readline( ) ) )


if __name__ == "__main__":

    encoder = Encoder( 'b' )
    lastCount = -0

    while True:
        counter = encoder.getCounter( )
        if counter != lastCount:
            print( counter )
            lastCount = counter
        # print( counter )
        time.sleep( 1 / 60 )
