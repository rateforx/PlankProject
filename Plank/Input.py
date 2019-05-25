from Plank.ArduinoIO import *

OUTPUT = 0
INPUT = 1
INPUT_PULLUP = 2
INPUT_ANALOG = 3

LOW = 0
HIGH = 1

FALLING = 0
RISING = 1
BOTH = 2


class Input:

    def __blank( self ):
        pass

    def __init__( self, arduinoIO, pin, name, pausable, analog = False ):
        self.callbackRising = self.__blank
        self.callbackFalling = self.__blank
        self.callbackLow = self.__blank
        self.callbackHigh = self.__blank
        self.thresholdRising = None
        self.thresholdFalling = None
        self.callbackRisingActivated = False
        self.callbackFallingActivated = False
        self.lastState = -1
        self.arduinoIO = arduinoIO
        self.pin = pin
        self.analog = analog
        self.verbose = False
        self.name = name
        self.pausable = pausable
        self.paused = True

        mode = INPUT_ANALOG if analog else INPUT
        arduinoIO.setMode( pin, mode, self )

    def getState( self ):
        if self.analog:
            self.arduinoIO.serial.write( 'a({})'.format( self.pin ).encode( ) )

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

    def update( self, paused ):
        self.paused = paused

        if not self.pausable or not self.paused:
            if self.lastState == LOW:
                self.callbackLow( )
            if self.lastState == HIGH:
                self.callbackHigh( )

    def set( self, value ):
        change = RISING if value > self.lastState else FALLING
        self.lastState = value
        if self.verbose:
            print( '{}: {}'.format( self.name, value) )

        if not self.pausable or not self.paused:

            if not self.analog:
                if value == LOW:
                    self.callbackFalling( )
                if value == HIGH:
                    self.callbackRising( )

            else:
                if change == RISING and self.thresholdRising is not None and value > self.thresholdRising:
                    if not self.callbackRisingActivated:
                        self.callbackRising( )

                    self.callbackRisingActivated = True
                    self.callbackFallingActivated = False

                elif change == FALLING and self.thresholdFalling is not None and value < self.thresholdFalling:
                    if not self.callbackFallingActivated:
                        self.callbackFalling( )

                    self.callbackFallingActivated = True
                    self.callbackRisingActivated = False
