from Plank.Engine import *
from Plank.Encoder import Encoder

class Servo:
    engine = None
    encoder = None

    zero = 0
    lastState = 0
    target = 0

    def __init__( self, engine: Engine, encoder: Encoder ):
        self.engine = engine
        self.encoder = encoder

        self.zero = encoder.getCounter()
        self.lastState = self.zero
        self.target = self.zero

    def update( self ):
        state = self.encoder.getCounter()
        if self.lastState != state:
            self.lastState = state
            if self.engine.getDirection() == CLOCKWISE:
                if state >= self.target:
                    self.engine.stop()
            if self.engine.getDirection() == ANTICLOCKWISE:
                if state <= self.target:
                    self.engine.stop()



    def calibrate( self ):
        pass

    def setSpeed( self, value ):
        self.engine.setSpeed( value )

    def move( self, distance: int, direction ):
        self.zero = self.encoder.getCounter()
        self.target = self.zero + distance
        self.engine.setDirection( direction )
        self.engine.start()



