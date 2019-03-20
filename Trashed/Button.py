from Plank.ArduinoIO import *


class Button:

    def __blank( self ):
        pass

    lowFunction = __blank
    highFunction = __blank

    lastState = None

    def __init__( self, arduinoIO, pin ):
        self.arduinoIO = arduinoIO
        self.pin = pin
        arduinoIO.setMode( pin, INPUT )

        self.lastState = self.getState()

    def getState( self ):
        return int( self.arduinoIO.read( self.pin ) )

    def update( self ):
        currentState = self.getState()
        if self.lastState != currentState:
            self.lastState = currentState
            if currentState == LOW:
                self.lowFunction()
            elif currentState == HIGH:
                self.highFunction()

    def onLow( self, function ):
        self.lowFunction = function

    def onHigh( self, function ):
        self.highFunction = function