from Plank.Engine import *
from Plank.Encoder import Encoder


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

    # def then( self, function ):
    #     self.thenCallback = function
