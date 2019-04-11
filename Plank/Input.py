from Plank.ArduinoIO import *

class Input:

    def __blank( self ):
        pass

    pin = -1
    lastState = None
    callbackRising = __blank
    callbackFalling = __blank
    callbackLow = __blank
    callbackHigh = __blank
    thresholdRising = None
    thresholdFalling = None
    callbackRisingActivated = False
    callbackFallingActivated = False

    verbose = False
    analog = False

    def __init__( self, arduinoIO: ArduinoIO, pin, analog = False, name = '' ):
        self.arduinoIO = arduinoIO
        self.pin = pin
        self.analog = analog
        self.name = name
        arduinoIO.setMode( pin, INPUT )
        self.lastState = self.getState()

    def update( self ):
        state = self.getState()

        if self.verbose:
            if self.name != '':
                print( '{}: {}'.format( self.name, state ) )
            else:
                print( '_: {}'.format( state ) )

        if state != self.lastState:

            change = RISING if state > self.lastState else FALLING
            self.lastState = state

            if not self.analog:
                if state == FALLING:
                    self.callbackFalling( )
                if state == RISING:
                    self.callbackRising( )

            else:
                if change == RISING and self.thresholdRising is not None and state > self.thresholdRising:
                    if not self.callbackRisingActivated:
                        self.callbackRising( )

                    self.callbackRisingActivated = True
                    self.callbackFallingActivated = False

                elif change == FALLING and self.thresholdFalling is not None and state < self.thresholdFalling:
                    if not self.callbackFallingActivated:
                        self.callbackFalling( )

                    self.callbackFallingActivated = True
                    self.callbackRisingActivated = False

        if state == LOW:
            self.callbackLow()
        if state == HIGH:
            self.callbackHigh()

    def getState( self ):
        if not self.analog:
            return self.arduinoIO.read( self.pin )
        else:
            return self.arduinoIO.analogRead( self.pin )

    def setCallback( self, function, edge ):
        if edge == FALLING:
            self.callbackFalling = function
        if edge == RISING:
            self.callbackRising = function
        if edge == BOTH:
            self.callbackFalling = function
            self.callbackRising = function

    def setThreshold( self, value, edge, callback ):
        if edge == RISING:
            self.callbackRising = callback
            self.thresholdRising = value
        elif edge == FALLING:
            self.callbackFalling = callback
            self.thresholdFalling = value

    def setThresholdValue( self, value, edge ):
        if edge == RISING:
            self.thresholdRising = value
        elif edge == FALLING:
            self.thresholdFalling = value

    def do( self, function, state ):
        if state == LOW:
            self.callbackLow = function
        if state == HIGH:
            self.callbackHigh = function

    def on( self, edge, function ):
        self.setCallback( function, edge )

    def removeCallbacks( self ):
        self.callbackFalling = self.__blank
        self.callbackRising = self.__blank
        self.callbackLow = self.__blank
        self.callbackHigh = self.__blank
