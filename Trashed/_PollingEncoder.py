from RPi import GPIO
from threading import Thread
import time

GPIO.setmode( GPIO.BCM )

POLLING = 1
INTERRUPTS = 2

class PollingEncoder( Thread ):

    def __init__( self, aPin, bPin, frequency = 1000 ):
        Thread.__init__( self )
        self.aPin = aPin
        self.bPin = bPin

        GPIO.setup( aPin, GPIO.IN, GPIO.PUD_DOWN )
        GPIO.setup( bPin, GPIO.IN, GPIO.PUD_DOWN )

        self.verbose = False
        self.counter = 0
        self.frequency = frequency

        self.aLastState = GPIO.input( self.aPin )

    def update( self ):
        aState = GPIO.input( self.aPin )
        bState = GPIO.input( self.bPin )

        if aState != self.aLastState:
            if aState != bState:
                self.counter += 1
            else:
                self.counter -= 1

            if self.verbose:
                print( self.counter )

        self.aLastState = aState

    def run( self ):
        while True:
            self.update()
            time.sleep( 1 / self.frequency )

    def resetCounter( self ):
        self.counter = 0