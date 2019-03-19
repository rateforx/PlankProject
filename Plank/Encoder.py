import time
from serial import Serial
from Plank.ArduinoSerialPortFinder import *

baudrate = 9600
timeout = 1


class Encoder:
    lastCount = None
    verbose = False
    readCounter = 0

    def __init__( self, encoderID, port = ArduinoSerialPortFinder.getArduinoPort( UNO_SN0 ) ):
        print( 'Connecting to Arduino serial: {}'.format( port ) )
        self.serial = Serial( port, baudrate, timeout = timeout )
        self.encoderID = encoderID

    def requestCounter( self ):
        self.serial.write( self.encoderID.encode( ) )
        time.sleep( .05 )

    def getCounter( self ):
        self.readCounter += 1

        try:
            self.requestCounter()
            value = int( self.serial.readline( ).decode( ).strip( "\r\n" ) )

        except ValueError:
            self.requestCounter()
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
        if  counter != lastCount:
            print( counter )
            lastCount = counter
        # print( counter )
        time.sleep( 1 / 60 )
