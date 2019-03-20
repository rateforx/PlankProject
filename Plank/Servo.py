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
        self.lastState = self.encoder.getCounter()

    def calibrate( self ):
        pass

    def move( self, distance: int, direction ):
        self.zero = self.encoder.getCounter()
        self.target = self.zero + distance
        self.engine.setDirection( direction )



