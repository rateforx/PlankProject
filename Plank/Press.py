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
    boardsPerSet = 0
    setsPerSeries = 0
    slatsPerSet = 0

    """ 
    n1 boards in cycle
    n2 cycles in a series
    n3 series in a set
    
    set a set of n3 series takes n3 * n2 * n1 slats  
    """

    currentSlat = 0
    currentBoard = 0
    # currentCycle = 0
    currentSet = 0
    currentSlatInSet = 0

    boardLength = 0
    boardWidth = 0
    boardHeight = 0

    updateRate = 60
    automatic = True
    running = True

    inputs = [ ]

    slatState = 0

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

        def conveyorSensorCallback( ):
            if self.slatState == 0:
                self.slatPusherEnable.setState( LOW )
                self.next( )
                self.slatState = 1

        self.conveyorSensor.do( conveyorSensorCallback, HIGH )

        def counterSensorCallback( ):
            if self.slatState == 1:
                self.slatPusherEnable.setState( HIGH )
                self.slatState = 2

        self.counterSensor.do( counterSensorCallback, HIGH )

        def stackerSensorCallback( ):
            if self.slatState == 2:
                self.halfTurnMotorEnable.setState( LOW )
                self.slatState = 3

        self.stackerSensor.do( stackerSensorCallback, HIGH )

        # def halfTurnMotorSensorCallbackLow( ):
        #     if self.slatState == 3:
        #         self.slatState = 4

        # self.halfTurnMotorSensor.do( halfTurnMotorSensorCallbackLow, LOW )

        def halfTurnMotorSensorCallbackHigh( ):
            if self.slatState == 3:
                self.halfTurnMotorEnable.setState( HIGH )
                self.slatState = 2

        self.halfTurnMotorSensor.do( halfTurnMotorSensorCallbackHigh, HIGH )
        self.halfTurnMotorSensor.setCallback( halfTurnMotorSensorCallbackHigh, BOTH )

    def next( self ):
        self.currentSlat += 1

        # if last slat in board
        if self.currentSlat == self.slatsPerBoard:
            self.currentBoard += 1
            "OSTATNIA LAMELKA"
            self.currentSlat = 0
            self.glueDisable.setState( HIGH )

            "KAŻDY BLAT"
            # if last board in series
            if self.currentBoard == self.boardsPerSet:
                self.currentSet += 1
                "OSTATNI BLAT"
                self.currentBoard = 0

                # todo każdy set -> opuścić set na taśmę, ścisnąć, podnieść, odjechać kawałek

                "KAŻDY SET"
                # if last series in set
                if self.currentSet == self.setsPerSeries:
                    "OSTATNI SET"
                    self.currentSet = 0

                    # todo ostatni set -> wjazd do prasy

                else:
                    "NIEOSTATNI SET"
                    pass

            elif self.currentBoard == self.boardsPerSet - 1:
                "PRZEDOSTATNI BLAT"


            else:
                "NIEOSTATNI BLAT"
                pass

        elif self.currentSlat == 1:
            "PIERWSZA LAMELKA"

            self.glueDisable.setState( LOW )

        else:
            "NIEOSTATNIA I NIEPIERWSZA LAMELKA"
            self.glueDisable.setState( HIGH )

        print( 'Current slat: {}'.format( self.currentSlat ) )
        print( 'Current board: {}'.format( self.currentBoard ) )
        print( 'Current set: {}'.format( self.currentSet ) )

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

        self.boardsPerSet = math.floor( PRESS_WIDTH / (self.slatWidth * self.slatsPerBoard) )
        self.setsPerSeries = math.floor( PRESS_LENGTH / (self.slatLength + STACKER_GAP) )
        self.slatsPerSet = self.slatsPerSet * self.boardsPerSet * self.slatsPerBoard

    def runBoard( self ):
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

            self.slatPusherEnable.setState( HIGH )

            while not self.stackerSensor.getState( ) == HIGH:  # wait for slat
                pass

            self.halfTurnMotorEnable.setState( LOW )  # push slat over belt
            time.sleep( .5 )  # simulate passing time

            while not self.halfTurnMotorSensor.getState( ) == HIGH:  # wait for half a turn
                pass

            self.halfTurnMotorEnable.setState( HIGH )  # stop pushing

            self.currentSlat += 1
            self.currentSlatInSet += 1

    def runSet( self ):
        self.currentBoard = 0
        for i in range( self.boardsPerSet ):
            self.runBoard( )
            self.currentBoard += 1

    def runSeries( self ):
        self.currentSlatInSet = 0
        for i in range( self.setsPerSeries ):
            self.runSet( )
            pneumatics.runCycle( )
            self.conveyorEngine.start( )
            time.sleep( 3 )
            self.conveyorEngine.stop( )

    def update( self ):
        for input in self.inputs:
            input.update( )

    def run( self ):
        while self.running:
            if self.automatic:
                self.update( )
            else:
                pass  # todo manual mode
            time.sleep( 1 / self.updateRate )


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
    print( 'Press running...' )
    press.run( )
