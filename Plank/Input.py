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

    verbose = False

    def __init__( self, arduinoIO: ArduinoIO, pin ):
        self.arduinoIO = arduinoIO
        self.pin = pin
        arduinoIO.setMode( pin, INPUT )
        self.lastState = arduinoIO.read( pin )

    def update( self ):
        state = self.arduinoIO.read( self.pin )

        if self.verbose:
            print( state )

        if state != self.lastState:

            self.lastState = state

            if state == FALLING:
                self.callbackFalling( )
            if state == RISING:
                self.callbackRising( )

        if state == LOW:
            self.callbackLow()
        if state == HIGH:
            self.callbackHigh()

    def getState( self ):
        return self.arduinoIO.read( self.pin )

    def setCallback( self, function, edge ):
        if edge == FALLING:
            self.callbackFalling = function
            self.callbackRising = self.__blank
        if edge == RISING:
            self.callbackFalling = self.__blank
            self.callbackRising = function
        if edge == BOTH:
            self.callbackFalling = function
            self.callbackRising = function

    def do( self, function, state ):
        if state == LOW:
            self.callbackLow = function
        if state == HIGH:
            self.callbackHigh = function

    def on( self, edge, function ):
        self.setCallback( function, edge )

    def removeCallback( self ):
        self.callbackFalling = self.__blank
        self.callbackRising = self.__blank
        self.callbackLow = self.__blank
        self.callbackHigh = self.__blank
