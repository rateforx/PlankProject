from Plank.ArduinoIO import *

class Input:

    def __blank( self ):
        pass

    pin = -1
    lastState = None
    callbackRising = __blank
    callbackFalling = __blank

    def __init__( self, arduinoIO: ArduinoIO, pin ):
        self.arduinoIO = arduinoIO
        self.pin = pin
        arduinoIO.setMode( pin, INPUT )
        self.lastState = arduinoIO.read( pin )

    def update( self ):
        state = self.arduinoIO.read( self.pin )
        if state != self.lastState:

            self.lastState = state

            if state == FALLING:
                self.callbackFalling( )
            if state == RISING:
                self.callbackRising( )

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

    def on( self, edge, function ):
        self.setCallback( function, edge )

    def removeCallback( self ):
        self.callbackFalling = self.__blank
        self.callbackRising = self.__blank
