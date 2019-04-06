import os
import sys

from PyQt5.QtWidgets import QCheckBox, QLCDNumber

# import Plank.Server

sys.path.extend( [ '/home/pi/Desktop/BigBoy', '/home/pi/Desktop/BigBoy' ] )

import math

from Plank.Encoder import *
from Plank.Press import *
from Plank.Servo import *
from Plank.Vice import *

A0 = 54
A1 = 55
A2 = 56
A3 = 57
A4 = 58
A5 = 59
A6 = 60
A7 = 61
A8 = 62
A9 = 63
A10 = 64
A11 = 65
A12 = 66
A13 = 67
A14 = 68
A15 = 69


class BigBoy:
    STACKER_LENGTH = 5260  # mm
    STACKER_WIDTH = 1900  # mm
    STACKER_GAP = 200  # mm

    PRESS_LENGTH = 4500  # mm
    PRESS_WIDTH = 1900  # mm
    PRESS_CONVEYOR_CORRECTION = 700  # mm

    AUTOMATIC = 0
    MANUAL = 1

    conveyorServo = ...  # type: Servo
    # PARAMS
    slatLength = 0
    slatWidth = 0
    slatHeight = 0
    slatsPerBoard = 0
    boardsPerRow = 0
    rowsPerSet = 0
    slatsPerSet = 0

    currentSlat = 0
    currentBoard = 0
    currentRow = 0
    currentSlatInSet = 0

    boardLength = 0
    boardWidth = 0
    boardHeight = 0

    updateRate = 60

    pressControls = MANUAL
    viceControls = MANUAL
    pressRunning = False
    viceRunning = False

    speed = 50

    inputs = [ ]
    controls = [ ]

    conveyorSensorDetectTime = -1
    slatState = 0

    vice = None
    press = None

    gui = None
    step = 0

    yellow = None
    orange = None

    def __init__( self ):
        self.yellow = ArduinoIO( MEGA_SN0 )
        self.orange = ArduinoIO( MEGA_SN1 )

        # self.gui = GUI( )

        self.conveyorSensor = Input( self.yellow, 14, name = 'Czujnik popychacza' )
        self.retractSensor = Input( self.yellow, 10, name = 'Czujnik cofania popychacza' )
        self.stackerSensor = Input( self.yellow, 8, name = 'Czujnik układarki' )
        self.halfTurnMotorSensor = Input( self.yellow, 12, name = 'Czujnik półobrotu' )

        # noinspection SpellCheckingInspection
        self.inputs += [
            self.conveyorSensor,
            self.retractSensor,
            self.stackerSensor,
            self.halfTurnMotorSensor,
        ]

        self.viceAMSwitch = Input( self.yellow, A11, name = 'Układarka przełącznik - automat / manual' )
        self.viceStartButton = Input( self.yellow, A9, name = 'Układarka przycisk - start' )
        self.viceStopButton = Input( self.yellow, A6, name = 'Układarka przycisk - stop' )
        self.viceConveyorForwardSwitch = Input( self.yellow, A10, name = 'Układarka przełącznik - taśma przód' )
        self.viceConveyorBackwardSwitch = Input( self.yellow, A8, name = 'Układarka przełącznik - taśma tył' )

        self.pressAMSwitch = Input( self.yellow, A7, name = 'Prasa przełącznik - automat / manual' )
        self.pressStartButton = Input( self.yellow, A5, name = 'Prasa przycisk - start' )
        self.pressStopButton = Input( self.yellow, A4, name = 'Prasa przycisk - stop' )
        self.pressConveyorForwardSwitch = Input( self.yellow, 20, name = 'Prasa przełącznik - taśma przód' )
        self.pressConveyorBackwardSwitch = Input( self.yellow, 21, name = 'Prasa przełącznik - taśma tył' )
        self.pressTopMoveUpSwitch = Input( self.orange, 15, name = 'Prasa przełącznik - górny docisk w górę' )
        self.pressTopMoveDownSwitch = Input( self.orange, 2, name = 'Prasa przełącznik - górny docisk w dół' )
        self.pressSideMoveInSwitch = Input( self.orange, 14, name = 'Prasa przełącznik - boczny docisk do wewnątrz' )
        self.pressSideMoveOutSwitch = Input( self.orange, 16, name = 'Prasa przełącznik - boczny docisk do zewnątrz' )

        self.controls += [
            self.viceAMSwitch,
            self.viceStartButton,
            self.viceStopButton,
            self.viceConveyorForwardSwitch,
            self.viceConveyorBackwardSwitch,
            self.pressAMSwitch,
            self.pressStartButton,
            self.pressStopButton,
            self.pressConveyorForwardSwitch,
            self.pressConveyorBackwardSwitch,
            self.pressTopMoveUpSwitch,
            self.pressTopMoveDownSwitch,
            self.pressSideMoveInSwitch,
            self.pressSideMoveOutSwitch,
        ]

        self.glueDisable = Output( self.orange, 49, LOW )
        self.halfTurnMotorEnable = Output( self.yellow, 50 )
        self.slatPusherEnable = Output( self.orange, 22 )

        self.conveyorServo = Servo(
            # engine = Engine( self.yellow, pwmPin = 23, runPin = 26, dirPin = 27, dutyCycle = 50 ),
            engine = Engine( self.yellow, pwmPin = 23, runPin = 26, dirPin = 27, dutyCycle = 50 ),
            encoder = Encoder( UNO_SN0 )
        )

        self.vice = Vice( self )
        self.press = Press( self )

        # input CALLBACKS

        def conveyorSensorCallback( ):
            if self.slatState == 0:
                if self.vice.state != Vice.RELEASING:
                    self.slatPusherEnable.set( LOW )
                    self.slatState = 1

        self.conveyorSensor.do( conveyorSensorCallback, HIGH )

        def counterSensorCallback( ):
            if self.slatState == 1:
                self.slatPusherEnable.set( HIGH )
                self.slatState = 2

        self.retractSensor.do( counterSensorCallback, HIGH )

        def stackerSensorCallback( ):
            if self.slatState == 2:
                self.halfTurnMotorEnable.set( LOW )
                self.slatState = 3

        self.stackerSensor.do( stackerSensorCallback, HIGH )

        def halfTurnMotorSensorCallbackLow( ):
            if self.slatState == 3:
                self.slatState = 4

        self.halfTurnMotorSensor.do( halfTurnMotorSensorCallbackLow, LOW )

        def halfTurnMotorSensorCallbackHigh( ):
            if self.slatState == 4:
                self.halfTurnMotorEnable.set( HIGH )
                self.slatState = 0
                self.currentSlat += 1
                self.next( )

        self.halfTurnMotorSensor.do( halfTurnMotorSensorCallbackHigh, HIGH )

        # controls CALLBACKS
        # VICE Controls

        def viceAMSwitchFalling( ):
            self.viceControls = BigBoy.AUTOMATIC
            self.viceRunning = False

        def viceAMSwitchRising( ):
            self.viceControls = BigBoy.MANUAL
            self.viceRunning = False

        self.viceAMSwitch.setCallback( viceAMSwitchFalling, FALLING )
        self.viceAMSwitch.setCallback( viceAMSwitchRising, RISING )

        def viceStartButtonRising( ):
            if self.viceControls == bigBoy.AUTOMATIC:
                self.viceRunning = True

        def viceStopButtonRising( ):
            self.viceRunning = False

        self.viceStartButton.setCallback( viceStartButtonRising, RISING )
        self.viceStopButton.setCallback( viceStopButtonRising, RISING )

        def viceConveyorForwardSwitchRising( ):
            if self.viceControls == BigBoy.MANUAL:
                self.conveyorServo.engine.setForward( )
                self.conveyorServo.engine.start( )

        def viceConveyorForwardSwitchFalling( ):
            if self.viceControls == BigBoy.MANUAL:
                self.conveyorServo.engine.stop( )

        self.viceConveyorForwardSwitch.setCallback( viceConveyorForwardSwitchRising, RISING )
        self.viceConveyorForwardSwitch.setCallback( viceConveyorForwardSwitchFalling, FALLING )

        def viceConveyorBackwardSwitchRising( ):
            if self.viceControls == BigBoy.MANUAL:
                self.conveyorServo.engine.setBackward( )
                self.conveyorServo.engine.start( )

        def viceConveyorBackwardSwitchFalling( ):
            if self.viceControls == BigBoy.MANUAL:
                self.conveyorServo.engine.stop( )

        self.viceConveyorBackwardSwitch.setCallback( viceConveyorBackwardSwitchRising, RISING )
        self.viceConveyorBackwardSwitch.setCallback( viceConveyorBackwardSwitchFalling, FALLING )

        # PRESS Controls

        def pressAMSwitchFalling( ):
            self.pressControls = BigBoy.AUTOMATIC
            self.pressRunning = False

        def pressAMSwitchRising( ):
            self.pressControls = BigBoy.MANUAL
            self.pressRunning = False

        self.pressAMSwitch.setCallback( pressAMSwitchFalling, FALLING )
        self.pressAMSwitch.setCallback( pressAMSwitchRising, RISING )

        def pressStartButtonRising( ):
            if self.pressControls == bigBoy.AUTOMATIC:
                self.pressRunning = True

        def pressStopButtonRising( ):
            self.pressRunning = False

        self.pressStartButton.setCallback( pressStartButtonRising, RISING )
        self.pressStopButton.setCallback( pressStopButtonRising, RISING )

        def pressConveyorForwardSwitchRising( ):
            if self.pressControls == BigBoy.MANUAL:
                self.press.pressConveyorEngine.engine.setForward( )
                self.press.pressConveyorEngine.engine.start( )

        def pressConveyorForwardSwitchFalling( ):
            if self.pressControls == BigBoy.MANUAL:
                self.press.pressConveyorEngine.engine.stop( )

        self.pressConveyorForwardSwitch.setCallback( pressConveyorForwardSwitchRising, RISING )
        self.pressConveyorForwardSwitch.setCallback( pressConveyorForwardSwitchFalling, FALLING )

        def pressConveyorBackwardSwitchRising( ):
            if self.pressControls == BigBoy.MANUAL:
                self.press.pressConveyorEngine.engine.setBackward( )
                self.press.pressConveyorEngine.engine.start( )

        def pressConveyorBackwardSwitchFalling( ):
            if self.pressControls == BigBoy.MANUAL:
                self.press.pressConveyorEngine.engine.stop( )

        self.pressConveyorBackwardSwitch.setCallback( pressConveyorBackwardSwitchRising, RISING )
        self.pressConveyorBackwardSwitch.setCallback( pressConveyorBackwardSwitchFalling, FALLING )

        def pressTopMoveDownSwitchRising( ):
            if self.pressControls == BigBoy.MANUAL:
                self.press.pressTopMoveDown.set( LOW )

        def pressTopMoveDownSwitchFalling( ):
            if self.pressControls == BigBoy.MANUAL:
                self.press.pressTopMoveDown.set( HIGH )

        def pressTopMoveUpSwitchRising( ):
            if self.pressControls == BigBoy.MANUAL:
                self.press.pressTopMoveUp.set( LOW )

        def pressTopMoveUpSwitchFalling( ):
            if self.pressControls == BigBoy.MANUAL:
                self.press.pressTopMoveUp.set( HIGH )

        self.pressTopMoveDownSwitch.setCallback( pressTopMoveDownSwitchRising, RISING )
        self.pressTopMoveDownSwitch.setCallback( pressTopMoveDownSwitchFalling, FALLING )
        self.pressTopMoveUpSwitch.setCallback( pressTopMoveUpSwitchRising, RISING )
        self.pressTopMoveUpSwitch.setCallback( pressTopMoveUpSwitchFalling, FALLING )

        def pressSideMoveInSwitchRising( ):
            if self.pressControls == BigBoy.MANUAL:
                self.press.pressSideMoveIn.set( LOW )

        def pressSideMoveInSwitchFalling( ):
            if self.pressControls == BigBoy.MANUAL:
                self.press.pressSideMoveIn.set( HIGH )

        def pressSideMoveOutSwitchRising( ):
            if self.pressControls == BigBoy.MANUAL:
                self.press.pressSideMoveOut.set( LOW )

        def pressSideMoveOutSwitchFalling( ):
            if self.pressControls == BigBoy.MANUAL:
                self.press.pressSideMoveOut.set( HIGH )

        self.pressSideMoveInSwitch.setCallback( pressSideMoveInSwitchRising, RISING )
        self.pressSideMoveInSwitch.setCallback( pressSideMoveInSwitchFalling, FALLING )
        self.pressSideMoveOutSwitch.setCallback( pressSideMoveOutSwitchRising, RISING )
        self.pressSideMoveOutSwitch.setCallback( pressSideMoveOutSwitchFalling, FALLING )

    def next( self ):
        self.slatCheck( )

    def slatCheck( self ):
        if self.currentSlat == 0:
            self.glueDisable.set( HIGH )

        elif 0 < self.currentSlat < self.slatsPerBoard:
            self.glueDisable.set( HIGH )

        elif self.currentSlat == self.slatsPerBoard:
            self.glueDisable.set( LOW )
            self.currentBoard += 1
            self.currentSlat = 0
            self.boardCheck( )

    def boardCheck( self ):
        if self.currentBoard == 0:
            pass

        elif 0 < self.currentBoard < self.boardsPerRow:
            pass

        elif self.currentBoard == self.boardsPerRow:
            self.currentRow += 1
            self.currentBoard = 0
            self.rowCheck( )

    def rowCheck( self ):
        if self.currentRow == 0:
            self.vice.readyToRelease = True

        elif 0 < self.currentRow < self.rowsPerSet:
            self.vice.readyToRelease = True

        elif self.currentRow == self.rowsPerSet:
            self.vice.readyToRelease = True
            self.currentRow = 0
            self.vice.readyToUnload = True
            if self.vice.state == Vice.IDLE:
                self.vice.state = Vice.RELEASING
                if self.press.state == Press.IDLE:
                    self.press.state = Press.LOADING
                    self.currentRow = 0
                    self.vice.readyToUnload = True
                else:
                    pass  # todo błąd: prasa nie gotowa, zwolnij prasę
            else:
                pass  # todo błąd: układarka nie gotowa, zwolnij taśmę pod układarką

    def setParams( self, length, width, height, slatsPerBoard ):
        self.slatLength = length
        self.slatWidth = width
        self.slatHeight = height
        self.slatsPerBoard = slatsPerBoard

        self.boardLength = length
        self.boardWidth = width * slatsPerBoard
        self.boardHeight = height

    def recalculateParams( self ):
        if not self.slatLength or not self.slatWidth or not self.slatHeight or not self.slatsPerBoard:
            return

        self.boardsPerRow = math.floor( BigBoy.PRESS_WIDTH / (self.slatWidth * self.slatsPerBoard) )
        self.rowsPerSet = math.floor( BigBoy.PRESS_LENGTH / (self.slatLength + BigBoy.STACKER_GAP) )
        self.slatsPerSet = self.slatsPerSet * self.boardsPerRow * self.slatsPerBoard

    def update( self ):
        self.step += 1
        self.conveyorServo.update( )
        self.vice.update( )
        self.press.update( )
        for input in self.inputs:
            input.update( )
        for input in self.controls:
            input.update( )

    def updateGUI( self ):
        self.gui.ui.conveyorSensor.setChecked( self.conveyorSensor.lastState == 1 )
        self.gui.ui.counterSensor.setChecked( self.retractSensor.lastState == 1 )
        self.gui.ui.stackerSensor.setChecked( self.stackerSensor.lastState == 1 )
        self.gui.ui.halfTurnMotorSensor.setChecked( self.halfTurnMotorSensor.lastState == 1 )

        conveyorSensorCheckbox = self.gui.window.findChild( QCheckBox, 'conveyorSensor' )  # type: QCheckBox
        conveyorSensorCheckbox.setChecked( self.conveyorSensor.lastState == 1 )

        self.gui.ui.temp1.display( self.press.tempTop.lastState )
        self.gui.ui.temp0.display( self.press.tempDown.lastState )

        tempTop = self.gui.window.findChild( QLCDNumber, 'temp0' )  # type: QLCDNumber
        tempTop.display( self.press.tempTop.lastState )
        tempDown = self.gui.window.findChild( QLCDNumber, 'temp1' )  # type: QLCDNumber
        tempDown.display( self.press.tempDown.lastState )

        self.gui.window.update( )
        self.gui.app.processEvents( )

    def run( self ):
        self.update( )

    def printStates( self ):
        _ = os.system( 'clear' )
        print( '======================================' )
        print( 'iteration: {}'.format( self.step ) )
        print( 'slateState: {}'.format( self.slatState ) )
        print( 'currentSlat: {} of {}'.format( self.currentSlat, self.slatsPerBoard ) )
        print( 'currentBoard: {} of {}'.format( self.currentBoard, self.boardsPerRow ) )
        print( 'currentRow: {} of {}'.format( self.currentRow, self.rowsPerSet ) )
        print( 'viceState: {}'.format( self.vice.state ) )
        print( 'viceCompressionState: {}'.format( self.vice.compressingState ) )
        print( 'viceDecompressionState: {}'.format( self.vice.decompressingState ) )
        print( 'pressState: {}'.format( self.press.state ) )
        print( 'pressCompressionState: {}'.format( self.press.compressingState ) )
        print( 'pressDecompressionState: {}'.format( self.press.decompressingState ) )
        print( 'pressLoadingState: {}'.format( self.press.loadingState ) )
        print( 'tempTop: {}'.format( self.press.tempTop.lastState ) )
        print( 'tempDown: {}'.format( self.press.tempDown.lastState ) )


if __name__ == "__main__":
    bigBoy = BigBoy( )
    bigBoy.setParams( 2000, 450, 30, 2 )
    bigBoy.recalculateParams( )
    bigBoy.conveyorServo.engine.setSpeed( 50 )
    print( 'Press running...' )