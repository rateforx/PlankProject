from Plank.Engine import *
from Plank.Encoder import Encoder
from Plank.Output import Output
from math import pi as PI


class Servo:
    IDLE = 0
    MOVING = 1

    engine = None
    encoder = None

    def __blank( self ):
        pass

    thenCallback = __blank

    state = IDLE

    def __init__( self, engine: Engine, encoder: Encoder ):
        self.engine = engine
        self.encoder = encoder

    def update( self ):
        if self.encoder.serial.inWaiting( ):
            data = self.encoder.serial.readline( ).decode( ).strip( "\r\n" )
            if data == "STOP":
                self.engine.stop( )
                self.state = self.IDLE
                # self.thenCallback( )
                # self.thenCallback = self.__blank

    def move( self, distance: int ):
        value = distance * 1000 / 430  # 1000 impulses for full encoder rotation / 430mm fi
        self.encoder.serial.write( 'm({});'.format( value ).encode( ) )
        self.engine.setDirection( CLOCKWISE if distance > 0 else ANTICLOCKWISE )
        self.engine.start( )
        self.state = self.MOVING


class SimpleServo:
    RADIUS = 43.5
    MINIMAL_DISTANCE = 430
    ONE_TURN_TRAVEL_DISTANCE = 273

    IDLE = 0
    MOVING = 1
    # RESETTING = 2

    state = IDLE
    forwardEnable = None  # type: Output
    backwardEnable = None  # type: Output
    encoder = None  # type: Encoder

    def __init__( self, forwardOutput, backwardOutput, encoder ):
        self.forwardEnable = forwardOutput
        self.backwardEnable = backwardOutput
        self.encoder = encoder

    def update( self ):
        if self.encoder.serial.inWaiting( ):
            data = self.encoder.serial.readline( ).decode( ).strip( '\r\n' )
            if data == 'STOP':
                self.forwardEnable.set( HIGH )
                self.backwardEnable.set( HIGH )
                self.state = SimpleServo.IDLE

    def move( self, distance: int ):
        value = ( distance - self.MINIMAL_DISTANCE ) * 1000 / self.ONE_TURN_TRAVEL_DISTANCE
        self.encoder.serial.write( 'm({})'.format( value ).encode( ) )

        self.forwardEnable.set( LOW ) if distance > 0 else self.backwardEnable.set( LOW )
        self.state = SimpleServo.MOVING
