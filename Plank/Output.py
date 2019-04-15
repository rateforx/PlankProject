from Plank.ArduinoIO import *

class Output:
    pin = -1
    arduinoIO = None
    lastState = None

    def __init__( self, arduinoIO: ArduinoIO, pin, initialValue = HIGH ):
        arduinoIO.write( pin, initialValue )
        arduinoIO.setMode( pin, OUTPUT )
        self.arduinoIO = arduinoIO
        self.pin = pin
        self.lastState = initialValue

    def set( self, value ):
        self.arduinoIO.write( self.pin, value )
        self.lastState = value
