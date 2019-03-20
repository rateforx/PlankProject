import RPi.GPIO as GPIO
from Plank.ArduinoIO import *

GPIO.setmode( GPIO.BCM )

CLOCKWISE = 1
ANTICLOCKWISE = 0


class Engine:

    def __init__( self, arduinoIO, pwmPin, runPin, dirPin, dutyCycle = 100, frequency = 1500 ):

        self.__arduinoIO = arduinoIO
        self.__pwmPin = pwmPin
        self.__runPin = runPin
        self.__dirPin = dirPin
        self.__speed = dutyCycle
        self.__direction = CLOCKWISE

        GPIO.setup( pwmPin, GPIO.OUT )
        self.__pwm = GPIO.PWM( pwmPin, frequency )
        self.__pwm.start( dutyCycle )

        arduinoIO.setMode( runPin, OUTPUT )
        arduinoIO.write( runPin, HIGH )
        arduinoIO.setMode( dirPin, OUTPUT )
        arduinoIO.write( dirPin, HIGH )

    def start( self ):
        self.__arduinoIO.write( self.__runPin, LOW )
        self.__pwm.start( self.__speed )

    def slowStart( self, duration = 3 ):
        self.setSpeed( 0 )
        self.start( )
        for dutyCycle in range( 0, 101, 1 ):
            self.setSpeed( dutyCycle )
            time.sleep( duration / 100 )

    def stop( self ):
        self.__arduinoIO.write( self.__runPin, HIGH )
        # self.setSpeed( 0 )
        self.__pwm.stop( )

    def slowStop( self, duration = 3 ):
        for dutyCycle in range( self.__speed, -1, -1 ):
            self.setSpeed( dutyCycle )
            time.sleep( duration / 100 )

    def setSpeed( self, value ):
        """value [ 0 - 100 ]"""
        self.__speed = value
        self.__pwm.ChangeDutyCycle( value )

    def setForward( self ):
        self.__arduinoIO.write( self.__dirPin, CLOCKWISE )
        self.__direction = CLOCKWISE

    def setBackward( self ):
        self.__arduinoIO.write( self.__dirPin, ANTICLOCKWISE )
        self.__direction = ANTICLOCKWISE

    def setDirection( self, direction ):
        self.__arduinoIO.write( self.__dirPin, direction )
        self.__direction = direction

    def reverse( self ):
        self.__arduinoIO.write( self.__dirPin, int( not self.__direction ) )
        self.__direction = int( not self.__direction )

    def getDirection( self ):
        return self.__direction


if __name__ == "__main__":
    pass
