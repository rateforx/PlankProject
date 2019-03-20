from Plank.Engine import Engine
from Plank.ArduinoIO import *
from Plank.Input import Input
from Plank.Output import Output
from Plank.ArduinoSerialPortFinder import *
from Plank.Encoder import Encoder
import math

INPUT_POLLING_FREQUENCY = 1000

STACKER_LENGTH = 5260  # mm
STACKER_WIDTH = 1900  # mm
STACKER_GAP = 200  # mm

PRESS_LENGTH = 4500  # mm
PRESS_WIDTH = 1900  # mm


class Press:
    # INPUT Pins
    conveyorSensorPin = 13  # yellow
    counterSensorPin = 10  # yellow
    stackerSensorPin = 8  # yellow
    bigBoyDisabledSensorPin = 7  # yellow
    halfTurnMotorSensorPin = 12  # yellow
    # OUTPUT Pins
    glueDisablePin = 49  # orange
    slatPusherPin = 22  # orange
    halfTurnMotorEnablePin = 50  # yellow

    # PARAMS
    slatLength = 0
    slatWidth = 0
    slatHeight = 0
    slatsPerBoard = 0
    boardsPerSeries = 0
    seriesPerSet = 0
    slatsPerSet = 0

    """ 
    n1 boards in cycle
    n2 cycles in a series
    n3 series in a set
    
    set a set of n3 series takes n3 * n2 * n1 slats  
    """

    currentSlat = 0
    currentBoard = 0
    currentCycle = 0
    currentSeries = 0
    currentSlatInSet = 0

    boardLength = 0
    boardWidth = 0
    boardHeight = 0

    updateRate = 120
    automatic = True

    inputs = [ ]

    def __init__( self ):
        self.conveyorSensor = Input( yellow, self.conveyorSensorPin )
        self.counterSensor = Input( yellow, self.counterSensorPin )
        self.stackerSensor = Input( yellow, self.stackerSensorPin )
        self.halfTurnMotorSensor = Input( yellow, self.halfTurnMotorSensorPin )
        self.bigBoyDisabledSensor = Input( yellow, self.bigBoyDisabledSensorPin )

        self.inputs += [
            self.conveyorSensor,
            self.counterSensor,
            self.stackerSensor,
            self.halfTurnMotorSensor,
        ]

        self.glueDisable = Output( orange, self.glueDisablePin )
        self.slatPusherEnable = Output( orange, self.slatPusherPin )
        self.halfTurnMotorEnable = Output( yellow, self.halfTurnMotorEnablePin )

        self.conveyorEngine = Engine( yellow, pwmPin = 23, runPin = 26, dirPin = 27, dutyCycle = 50 )

        # callbacks

        def conveyorSensorCallback():
            self.slatPusherEnable.setState( LOW )
            # self.current

        self.conveyorSensor.setCallback(
            lambda: self.slatPusherEnable.setState( LOW )
            , RISING )

        self.counterSensor.setCallback(
            lambda: self.slatPusherEnable.setState( HIGH ), RISING
        )

        self.stackerSensor.setCallback(
            lambda: self.halfTurnMotorEnable.setState( LOW ), RISING
        )
        self.halfTurnMotorSensor.setCallback(
            lambda: self.halfTurnMotorEnable.setState( HIGH ), RISING
        )

    def nextSlat( self ):
        

    def setParams( self, length, width, height, slatsPerBoard ):
        self.slatLength = length
        self.slatWidth = width
        self.slatHeight = height
        self.slatsPerBoard = slatsPerBoard

        self.boardLength = length
        self.boardWidth = width * slatsPerBoard
        self.boardHeight = height

    def calculateParams( self ):
        if not self.slatLength or not self.slatWidth or not self.slatHeight or not self.slatsPerBoard:
            return

        self.boardsPerSeries = math.floor( PRESS_WIDTH / (self.slatWidth * self.slatsPerBoard) )
        self.seriesPerSet = math.floor( PRESS_LENGTH / (self.slatLength + STACKER_GAP) )
        self.slatsPerSet = self.slatsPerSet * self.boardsPerSeries * self.slatsPerBoard

    def runCycle( self ):
        """
            A cycle will glue and stack the slats to create one board.
            The number of iterations is the slatsPerBoard value.
            The first slat will be pushed without glue.
            """
        self.currentSlat = 0
        for i in range( self.slatsPerBoard ):
            self.currentBoard = i

            if i == 0:
                self.glueDisable.setState( LOW )  # disable glue
            else:
                self.glueDisable.setState( HIGH )  # enable glue

            while not self.conveyorSensor.getState( ) == HIGH:  # wait for slat
                pass

            self.slatPusherEnable.setState( LOW )  # push slat via glue

            while not self.counterSensor.getState( ) == HIGH:  # wait for slat to pass
                pass

            orange.write( self.slatPusherPin, HIGH )  # reset slat pusher

            while not yellow.read( self.stackerSensorPin ) == HIGH:  # wait for slat
                pass

            yellow.write( self.halfTurnMotorEnablePin, LOW )  # push slat over belt
            time.sleep( .5 )  # simulate passing time

            while not yellow.read( self.halfTurnMotorSensorPin ) == HIGH:  # wait for half a turn
                pass

            yellow.write( self.halfTurnMotorEnablePin, HIGH )  # stop pushing

            self.currentSlat += 1
            self.currentSlatInSet += 1

    def runSeries( self ):
        self.currentBoard = 0
        for i in range( self.boardsPerSeries ):
            self.runCycle( )
            self.currentBoard += 1

    def runSet( self ):
        self.currentSlatInSet = 0
        for i in range( self.seriesPerSet ):
            self.runSeries( )
            pneumatics.runCycle( )
            self.conveyorEngine.start( )
            time.sleep( 3 )
            self.conveyorEngine.stop( )

    def update( self ):
        for input in self.inputs:
            input.update( )

    def run( self ):
        while True:
            if self.automatic:
                self.update( )
            else:
                pass  # todo manual mode
            # time.sleep( 1 / self.updateRate )


class Pneumatics:
    breakerUpDown = 53

    # breaker

    def runCycle( self ):
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
    press = Press( )
    press.setParams( 1200, 300, 30, 3 )
    press.calculateParams( )
    press.run( )
