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
    analog = False

    def __init__( self, arduinoIO: ArduinoIO, pin, analog = False, name = '' ):
        self.arduinoIO = arduinoIO
        self.pin = pin
        self.analog = analog
        self.name = name
        arduinoIO.setMode( pin, INPUT )
        self.lastState = arduinoIO.read( pin ) if not analog else arduinoIO.analogRead( pin )

    def update( self, active = False ):
        state = self.arduinoIO.read( self.pin ) if not self.analog else self.arduinoIO.analogRead( self.pin )

        if self.verbose:
            if self.name != '':
                print( '{}: {}'.format( self.name, state ) )
            else:
                print( '_: {}'.format( state ) )

        if state != self.lastState:

            self.lastState = state

            if state == FALLING and active:
                self.callbackFalling( )
            if state == RISING and active:
                self.callbackRising( )

        if state == LOW and active:
            self.callbackLow()
        if state == HIGH and active:
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
