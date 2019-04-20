from typing import Dict

from Plank.Input import *
from Plank.ArduinoSerialPortFinder import ArduinoSerialPortFinder
from serial import Serial
import time

baudrate = 115200
timeout = .5

OUTPUT = 0
INPUT = 1
INPUT_PULLUP = 2
INPUT_ANALOG = 3

LOW = 0
HIGH = 1

FALLING = 0
RISING = 1
BOTH = 2


class ArduinoIO:
    #inputs = { }  # type: Dict[int, Input]

    # outputs = { }  # type: Dict[int, Output]

    memory = ''

    def __init__( self, serialNumber, name = '' ):
        self.inputs = { }  # type: Dict[int, Input]
        self.port = ArduinoSerialPortFinder.getArduinoPort( serialNumber )
        self.serial = Serial( self.port, baudrate, timeout = timeout, xonxoff = True )
        time.sleep( 1 )
        self.name = name

    def setMode( self, pin, mode, io: Input = None ):
        self.serial.write( 'm({},{})'.format( pin, mode ).encode( ) )
        if mode in [ INPUT, INPUT_PULLUP, INPUT_ANALOG ]:
            self.inputs[ pin ] = io
        # elif mode == OUTPUT:
        #     self.outputs[ pin ] = io

    def write( self, pin, value ):
        self.serial.write( 'w({},{})'.format( pin, value ).encode( ) )
        # self.outputs[ pin ] = value

    def extractData( self, line: str ):
        # pin:value;
        parts = line.split( ';', 1 )[ 0 ].split( ':', 1 )
        pin = -1
        value = 0
        try:
            pin = int( parts[ 0 ] )
            value = int( parts[ 1 ] )
        except ValueError:
            print( 'Serial read failed for "{}"'.format( line ) )
        finally:
            return pin, value

    def readChunk( self ):
        data = self.serial.read_all( )
        lines = data.decode( ).split( '\r\n' )
        lines[ 0 ] = self.memory + lines[ 0 ]
        self.memory = ''
        lastLine = lines[ -1 ]
        if len( lastLine ):  # if string not empty
            if not lastLine[ -1 ] == ';':  # if last char is not terminated
                self.memory = lastLine  # save data part for later
        lines.pop( -1 )
        return lines

    def readLine( self ):
        return self.serial.read_until( ).decode( )

    def update( self ):
        while self.serial.inWaiting( ):
            # lines = self.readChunk( )
            # for line in lines:  # type: str
            #     if line == '':
            #         continue
            #     print( line )
            #     pin, value = self.extractData( line )
            #     print( '[{}] \t{}'.format( pin, value ) )
            #     try:
            #         self.inputs[ pin ].set( value )
            #     except KeyError:
            #         pass
            #         print( line )
            line = self.readLine()
            print( line )
            pin, value = self.extractData( line )
            if pin != -1:
                self.inputs[ pin ].set( value )
                print( '[{}] \t{}'.format( pin, value ) )

    def start( self ):
        self.serial.write( 's'.encode( ) )

    def stop( self ):
        self.serial.write( 'p'.encode( ) )
