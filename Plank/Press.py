from threading import Thread
import RPi.GPIO
from MCP230XX import MCP23018 as MCP
from Plank.IO import Input, Output
from Plank.Engine import Engine
from Plank.ArduinoIO import *
from Plank.ArduinoSerialPortFinder import *
from Plank.Encoder import Encoder
from Plank.Button import Button
import math

INPUT_POLLING_FREQUENCY = 60

# ??? = 4860 # mm
STACKER_LENGTH = 5260  # mm
STACKER_WIDTH = 1900  # mm
STACKER_GAP = 200  # mm

PRESS_LENGTH = 4500  # mm
PRESS_WIDTH = 1900  # mm


class Feeder:
    # IN
    conveyorSensorPin = 13 # yellow
    glueCounterPin = 10 # yellow
    slatAtStackerSensorPin = 8 # yellow
    # glueSensorAPin = 10 # yellow
    # glueSensorBPin = -1 # yellow

    halfTurnSensorPin = 12 # yellow
    # OUT
    glueDisablePin = 49 # orange
    slatPusherPin = 22 # orange
    halfTurnMotorEnablePin = 50 # yellow

    slatLength = 0
    slatWidth = 0
    slatHeight = 0

    slatsPerBoard = 0
    boardsPerSeries = 0
    seriesPerCycle = 0

    def __init__( self ):
        yellow.setMode( self.conveyorSensorPin, INPUT )
        yellow.setMode( self.glueCounterPin, INPUT )
        yellow.setMode( self.slatAtStackerSensorPin, INPUT )
        yellow.setMode( self.halfTurnSensorPin, INPUT )

        orange.setMode( self.glueDisablePin, OUTPUT )
        orange.setMode( self.slatPusherPin, OUTPUT )
        yellow.setMode( self.halfTurnMotorEnablePin, OUTPUT )


    def setParams( self, length, width, height, slatsPerBoard ):
        self.slatLength = length
        self.slatWidth = width
        self.slatHeight = height
        self.slatsPerBoard = slatsPerBoard

    def calculateParams( self ):
        if not self.slatLength or not self.slatWidth or not self.slatHeight or not self.slatsPerBoard:
            return

        self.boardsPerSeries = math.floor( PRESS_WIDTH / ( self.slatWidth * self.slatsPerBoard ) )
        self.seriesPerCycle = math.floor( PRESS_LENGTH / ( self.slatLength + STACKER_GAP ) )

    """ 
    A cycle will glue and stack the slats to create one board.
    The number of iterations is the slatsPerBoard value.
    The first slat will be pushed without glue. 
    """
    def runCycle( self ):
        orange.write( self.glueDisablePin, LOW ) # disable glue
        orange.write( self.slatPusherPin, LOW ) # push the first slat

        while True:
            if yellow.read( self.slatAtStackerSensorPin ) == HIGH:
                orange.write( self.glueDisablePin, HIGH ) # enable glue
                break

        yellow.write( self.halfTurnMotorEnablePin, LOW )
        time.sleep( .5 ) # todo remove hotfix
        while True:
            if yellow.read( self.halfTurnSensorPin ) == HIGH:
                yellow.write( self.halfTurnMotorEnablePin, HIGH )
                break

        for i in range( self.slatsPerBoard ):
            if i == 1:
                orange.write( self.glueDisablePin, LOW )
            else:
                orange.write( self.glueDisablePin, HIGH )

            while not yellow.read( self.conveyorSensorPin ) == HIGH:
                pass
            orange.write( self.slatPusherPin, LOW )
            while not yellow.read( self.glueCounterPin ) == HIGH:
                pass
            orange.write( self.slatPusherPin, HIGH )

            while not yellow.read( self.slatAtStackerSensorPin ) == HIGH:
                pass
            







    def run( self ):
        pass


class Pneumatics:
    breakerUpDown = 53

    # breaker

    def start( self ):
        orange.write( 51, LOW )
        time.sleep( 2.5 )

        orange.write( 47, LOW )
        time.sleep( 3 )

        orange.write( 50, LOW )
        time.sleep( 2 )

        orange.write( 50, HIGH )
        time.sleep( 2 )

        orange.write( 47, HIGH )
        time.sleep( 3 )

        orange.write( 51, HIGH )
        time.sleep( 2.5 )

        orange.write( 53, LOW )
        time.sleep( 2 )

        orange.write( 46, LOW )
        time.sleep( 3 )

        orange.write( 52, LOW )
        time.sleep( 10 )

        orange.write( 52, HIGH )
        time.sleep( 5 )

        orange.write( 46, HIGH )
        time.sleep( 3 )

        orange.write( 53, HIGH )
        time.sleep( 2 )


class Stacker:

    def __init__( self ):
        self.inputs = [ ]
        self.outputs = [ ]

        self.conveyorEngine = Engine( yellow, pwmPin = 23, runPin = 26, dirPin = 27, dutyCycle = 50 )
        # self.encoder = Encoder( )


class LengthSled:
    encoder = Encoder( 'b' )

    def __init__( self, arduinoIO, forwardPin, backwardPin, maxLimitPin, minLimitPin ):
        self.arduinoIO = arduinoIO
        self.forwardPin = forwardPin
        self.backwardPin = backwardPin
        self.maxLimitPin = maxLimitPin
        self.minLimitPin = minLimitPin

        arduinoIO.write( forwardPin, HIGH )
        arduinoIO.write( backwardPin, HIGH )
        arduinoIO.setMode( forwardPin, OUTPUT )
        arduinoIO.setMode( backwardPin, OUTPUT )
        arduinoIO.setMode( maxLimitPin, INPUT )
        arduinoIO.setMode( minLimitPin, INPUT )

    def reset( self ):
        if self.arduinoIO.read( self.minLimitPin ) == HIGH:  # if sled at minimum position
            return
        else:
            self.arduinoIO.write( self.backwardPin, LOW )  # start engine
            while True:
                if self.arduinoIO.read( self.minLimitPin ) == HIGH:
                    self.arduinoIO.write( self.backwardPin, HIGH )  # stop engine
                    return

    def stretch( self ):
        if self.arduinoIO.read( self.maxLimitPin ) == HIGH:  # if sled at minimum position
            return
        else:
            self.arduinoIO.write( self.forwardPin, LOW )  # start engine
            while True:
                if self.arduinoIO.read( self.maxLimitPin ) == HIGH:
                    self.arduinoIO.write( self.forwardPin, HIGH )  # stop engine
                    return

    def stop( self ):
        self.arduinoIO.write( self.forwardPin, HIGH )
        self.arduinoIO.write( self.backwardPin, HIGH )

    def halt( self ):
        self.stop( )

    def set( self, distance ):
        if distance < 43:
            return

        self.reset( )
        zeroPosition = self.encoder.getCounter( )
        self.arduinoIO.write( self.forwardPin, LOW )
        while True:
            if distance >= self.encoder.getCounter( ) + zeroPosition \
                    or self.arduinoIO.read( self.maxLimitPin ) == HIGH:
                self.stop( )
                return


class Press:

    def __init__( self ):
        self.inputs = [ ]
        self.outputs = [ ]


class Controls:

    def __init__( self ):
        self.inputs = [ ]

        # self.autoManualFeederStackerSwitch = Input( , 7 )
        # self.inputs.append( self.autoManualFeederStackerSwitch )


if __name__ == "__main__":

    yellow = ArduinoIO( MEGA_SN0 )
    orange = ArduinoIO( MEGA_SN1 )

    for pin in range( 22, 30 ):
        yellow.write( pin, HIGH )  # default to disabled
        yellow.setMode( pin, OUTPUT )
        orange.write( pin, HIGH )
        orange.setMode( pin, OUTPUT )
    for pin in range( 46, 54 ):
        yellow.write( pin, HIGH )  # default to disabled
        yellow.setMode( pin, OUTPUT )
        orange.write( pin, HIGH )
        orange.setMode( pin, OUTPUT )

    lengthSled = LengthSled( yellow, 47, 46, 2, 4 )
    pneumatics = Pneumatics( )
    stacker = Stacker( )
    engine = stacker.conveyorEngine

    # distance = 2000
    # speed = 50
    # engine = stacker.conveyorEngine
    # engine.setSpeed( speed )
    # engine.start( )
    # while True:
    #     pos = stacker.encoder.getCounter( )
    #     print( pos )
    #     if pos > 0.8 * distance and engine.getDirection( ) == engine.CLOCKWISE:
    #         engine.setSpeed( speed / 4 )
    #     if pos > distance and engine.getDirection( ) == engine.CLOCKWISE:
    #         engine.stop( )
    #         engine.reverse( )
    #         engine.setSpeed( speed )
    #         time.sleep( 1 )
    #         engine.start( )
    #     if pos < - 0.8 * distance and engine.getDirection( ) == engine.ANTICLOCKWISE:
    #         engine.setSpeed( speed / 4 )
    #     if pos < - distance and engine.getDirection( ) == engine.ANTICLOCKWISE:
    #         engine.stop( )
    #         engine.reverse( )
    #         engine.setSpeed( speed )
    #         time.sleep( 1 )
    #         engine.start( )
