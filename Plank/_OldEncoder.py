class OldEncoder:

    def __init__( self, aPin, bPin ):
        self.aPin = aPin
        self.bPin = bPin

        GPIO.setup( aPin, GPIO.IN, GPIO.PUD_DOWN )
        GPIO.setup( bPin, GPIO.IN, GPIO.PUD_DOWN )

        self.verbose = False
        self.counter = 0
        self.aLastState = GPIO.input( aPin )
        # GPIO.add_event_detect( aPin, GPIO.BOTH, self.callback )

    def callback( self, channel ):
        aState = GPIO.input( self.aPin )
        if aState != self.aLastState:
            bState = GPIO.input( self.bPin )
            if aState != bState:
                self.counter += 1
            else:
                self.counter -= 1
        if self.verbose:
            print( self.counter )

    def resetCounter( self ):
        self.counter = 0
