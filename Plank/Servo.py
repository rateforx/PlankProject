from Plank.Engine import *
from Plank.Encoder import Encoder


class Servo:
    engine = None
    encoder = None

    def __blank( self ):
        pass

    thenCallback = __blank

    def __init__( self, engine: Engine, encoder: Encoder ):
        self.engine = engine
        self.encoder = encoder

    def update( self ):
        if self.encoder.serial.inWaiting( ):
            data = self.encoder.serial.readline( ).decode( ).strip( "\r\n" )
            if data == "STOP":
                self.engine.stop( )
                self.thenCallback( )
                self.thenCallback = self.__blank

    def notUpdate( self ):
        state = self.encoder.getCounter( )
        if self.lastState != state:
            self.lastState = state
            if self.engine.getDirection( ) == CLOCKWISE:
                if state >= self.target:
                    self.engine.stop( )
                    self.thenCallback( )
            if self.engine.getDirection( ) == ANTICLOCKWISE:
                if state <= self.target:
                    self.engine.stop( )
                    self.thenCallback( )

    def calibrate( self ):
        pass

    def move( self, distance: int ):
        # todo przeliczanie na cm
        self.encoder.serial.write( 'm({});'.format( distance ).encode( ) )
        self.engine.setDirection( CLOCKWISE if distance > 0 else ANTICLOCKWISE )
        self.engine.start( )

    def notMove( self, distance: int ):
        self.encoder.serial.flush( )
        self.engine.setDirection( CLOCKWISE if distance > 0 else ANTICLOCKWISE )
        self.engine.start( )
        self.zero = self.encoder.getCounter( )
        self.target = self.zero + distance

    def then( self, function ):
        self.thenCallback = function
