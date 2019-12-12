from time import time as now

from Plank.LimitEngine import LimitEngine
from Plank.Engine import Engine
from Plank.Input import Input
from Plank.Output import *
# from Plank.TemperatureSensor import TemperatureSensor

AUTOMATIC = 0
MANUAL = 1

A0 = 54
A1 = 55
A2 = 56
A3 = 57
A12 = 66
A14 = 68


class Press:
    IDLE = 0
    LOADING = 1
    COMPRESSING = 2
    COMPRESSED = 3
    DECOMPRESSING = 4
    UNLOADING = 5

    inputs = [ ]

    state = 0
    loadingState = 0
    compressingState = 0
    # compressedState = 0
    decompressingState = 0
    unloadingState = 0

    forceLoading = False
    timer = 0
    pressureUpdateTimer = 0
    PRESSURE_UPDATE_RATE = 1

    compressedDuration = 120
    loosenDuration = 500  # ms
    depressurizationDuration = 3
    shakeDuration = 1
    pumpTogglePressureThreshold = 35
    pumpToggleDuration = 1
    topTargetPressure = 50
    sideTargetPressure = 50

    hysteresis = 5

    def __init__( self, bigBoy ):
        self.bigBoy = bigBoy

        self.pressTopHomeSensor = Input(
            bigBoy.yellow, A2, name = 'Prasa, góra - pozycja początkowa', pausable = False )
        self.pressSideHomeSensor = Input(
            bigBoy.yellow, A3, name = 'Prasa, bok - pozycja początkowa', pausable = False )
        self.pressTopPressureSensor = Input(
            bigBoy.yellow, A14, analog = True, name = 'Ciśnienie prasy, góra', pausable = False )
        self.pressSidePressureSensor = Input(
            bigBoy.yellow, A12, analog = True, name = 'Ciśnienie prasy, bok', pausable = False )

        self.pressTopMoveUp = Output( bigBoy.yellow, 23 )
        self.pressTopMoveDown = Output( bigBoy.yellow, 22 )
        self.pressSideMoveIn = Output( bigBoy.yellow, 25 )
        self.pressSideMoveOut = Output( bigBoy.yellow, 24 )
        self.pressPumpEnable = Output( bigBoy.yellow, 53 )
        self.pressPumpPrecisionEnable = Output( bigBoy.yellow, 52 )

        # self.tempTop = TemperatureSensor( 0 )
        # self.tempBottom = TemperatureSensor( 1 )

        self.pressConveyorEngine = LimitEngine(
            Engine( bigBoy.yellow, pwmPin = 24, runPin = 28, dirPin = 29, dutyCycle = 50 ),
            minLimitSensor = Input(
                bigBoy.yellow, A1, name = 'Czujnik indukcyjny: prasa - początek', pausable = False ),
            maxLimitSensor = Input(
                bigBoy.yellow, A0, name = 'Czujnik indukcyjny: prasa - koniec', pausable = False ),
        )

        def SAFKOSTOP( ):
            self.pressConveyorEngine.engine.stop( )
            self.pressConveyorEngine.state = self.pressConveyorEngine.IDLE

        self.pressConveyorEngine.minLimitSensor.setCallback( SAFKOSTOP, RISING )
        self.pressConveyorEngine.maxLimitSensor.setCallback( SAFKOSTOP, RISING )

        self.conveyorOscillationSensorLeft = Input(
            bigBoy.orange, 4, name = 'Prasa - Oscylacja czujnik lewo', pausable = False )
        self.conveyorOscillationSensorRight = Input(
            bigBoy.orange, 2, name = 'Prasa - Oscylacja czujnik prawo', pausable = False )
        self.conveyorOscillationEnable = Output(
            bigBoy.orange, 28 )

        self.partymakerEnable = Output( bigBoy.orange, 29 )

        self.inputs += [
            self.pressTopHomeSensor,
            self.pressSideHomeSensor,
            self.pressConveyorEngine.minLimitSensor,
            self.pressConveyorEngine.maxLimitSensor,
        ]

        def pressTopHomeSensorRising( ):
            self.pressTopMoveUp.set( HIGH )
            if LOW not in [
                self.pressSideMoveOut.lastState,
                self.pressSideMoveIn.lastState
            ]:
                self.pressPumpEnable.set( HIGH )

        self.pressTopHomeSensor.setCallback( pressTopHomeSensorRising, RISING )

        def pressSideHomeSensorRising( ):
            self.pressSideMoveOut.set( HIGH )
            if LOW not in [
                self.pressTopMoveUp.lastState,
                self.pressTopMoveDown.lastState,
            ]:
                self.pressPumpEnable.set( HIGH )

        self.pressSideHomeSensor.setCallback( pressSideHomeSensorRising, RISING )

        # def conveyorOscillationSensorLeftHigh( ):
        #     self.conveyorOscillationEnable.set( LOW )

        # def conveyorOscillationSensorRightHigh( ):
        #     self.conveyorOscillationEnable.set( HIGH )

        def conveyorOscillationSensorRightRising( ):
            self.conveyorOscillationEnable.set( HIGH )

        def conveyorOscillationSensorRightFalling( ):
            self.conveyorOscillationEnable.set( LOW )

        self.conveyorOscillationSensorRight.setCallback( conveyorOscillationSensorRightRising, RISING )
        self.conveyorOscillationSensorRight.setCallback( conveyorOscillationSensorRightFalling, FALLING )

        # self.conveyorOscillationSensorLeft.setCallback( conveyorOscillationSensorLeftRising, RISING )
        # self.conveyorOscillationSensorLeft.do( conveyorOscillationSensorLeftHigh, HIGH )
        # self.conveyorOscillationSensorRight.setCallback( conveyorOscillationSensorRightRising, RISING )
        # self.conveyorOscillationSensorRight.do( conveyorOscillationSensorRightHigh, HIGH )

        def pressureSensorThresholdRising( ):
            if self.bigBoy.pressControls == AUTOMATIC:
                return
            if LOW in [
                self.pressTopMoveDown.lastState,
                self.pressSideMoveIn.lastState,
            ]:
                self.pressPumpPrecisionEnable.set( LOW )

        def pressureSensorThresholdFalling( ):
            if self.bigBoy.pressControls == AUTOMATIC:
                return
            self.pressPumpPrecisionEnable.set( HIGH )

        self.pressTopPressureSensor.setThreshold(
            self.pumpTogglePressureThreshold, RISING, pressureSensorThresholdRising
        )
        self.pressTopPressureSensor.setThreshold(
            self.pumpTogglePressureThreshold - self.hysteresis, FALLING, pressureSensorThresholdFalling
        )
        self.pressSidePressureSensor.setThreshold(
            self.pumpTogglePressureThreshold, RISING, pressureSensorThresholdRising
        )
        self.pressSidePressureSensor.setThreshold(
            self.pumpTogglePressureThreshold - self.hysteresis, FALLING, pressureSensorThresholdFalling
        )

    def update( self ):
        running = self.bigBoy.pressRunning
        for input in self.inputs:
            input.update( not running )

        if now( ) - self.pressureUpdateTimer > self.PRESSURE_UPDATE_RATE / 5:
            self.pressureUpdateTimer = now( )
            if self.state in [
                Press.COMPRESSING,
                Press.COMPRESSED,
                # Press.DECOMPRESSING,
            ] or HIGH in [
                self.bigBoy.pressSideMoveInSwitch.lastState,
                self.bigBoy.pressTopMoveDownSwitch.lastState,
            ]:
                self.pressTopPressureSensor.getState( )
                self.pressSidePressureSensor.getState( )

        if now( ) - self.pressureUpdateTimer > self.PRESSURE_UPDATE_RATE:
            self.pressureUpdateTimer = now( )
            self.pressTopPressureSensor.getState( )
            self.pressSidePressureSensor.getState( )

        self.pressConveyorEngine.update( )

        if self.state == Press.IDLE and running:
            self.handleIdle( )

        elif self.state == Press.LOADING and running or self.forceLoading:
            self.handleLoading( )

        elif self.state == Press.COMPRESSING and running:
            self.handleCompressing( )

        elif self.state == Press.COMPRESSED and running:
            self.handleCompressed( )

        elif self.state == Press.DECOMPRESSING and running:
            self.handleDecompressing( )

        elif self.state == Press.UNLOADING and running:
            self.handleUnloading( )

    def handleIdle( self ):
        pass

    def handleLoading( self ):
        if self.loadingState == 0:
            if self.bigBoy.vice.unloadingState == 2:
                if self.pressConveyorEngine.minLimitSensor.lastState == HIGH:
                    if LOW not in [
                        self.pressTopHomeSensor.lastState,
                        self.pressSideHomeSensor.lastState,
                    ]:
                        self.bigBoy.vice.unloadingState = 3
                        self.pressConveyorEngine.run(
                            LimitEngine.FORWARD,
                            self.pressConveyorEngine.maxLimitSensor
                        )
                        self.loadingState = 1
                    else:
                        pass  # todo błąd: zaciski prasy nie są w pozycji początkowej

        elif self.loadingState == 1:
            if self.pressConveyorEngine.state == LimitEngine.IDLE:
                self.bigBoy.vice.unloadingState = 4
                self.loadingState = 0
                self.forceLoading = False
                self.state = Press.COMPRESSING
                self.timer = now( )

    def handleCompressing( self ):
        # if self.pressTopPressureSensor.lastState > self.pumpTogglePressureThreshold \
        #         and self.pressSideMoveIn.lastState == HIGH:
        #     self.pressPumpPrecisionEnable.set( LOW )

        # if self.pressSidePressureSensor.lastState > self.pumpTogglePressureThreshold \
        #         and self.pressTopMoveDown.lastState == HIGH:
        #     self.pressPumpPrecisionEnable.set( LOW )

        # turn the pump on and start pressing down
        if self.compressingState == 0:
            if self.pressTopHomeSensor.lastState == HIGH:
                self.pressPumpPrecisionEnable.set( HIGH )
                self.pressTopMoveDown.set( LOW )
                self.pressPumpEnable.set( LOW )
                self.compressingState = 1

        # when pressure reached stop pressing down and start pressing from the side
        elif self.compressingState == 1:
            if self.pressTopPressureSensor.lastState >= self.pumpTogglePressureThreshold:
                self.pressTopMoveDown.set( HIGH )
                self.timer = now( )
                self.compressingState = 1.25

        elif self.compressingState == 1.25:
            if now( ) - self.timer >= self.pumpToggleDuration:
                self.pressPumpPrecisionEnable.set( LOW )
                self.timer = now( )
                self.compressingState = 1.5

        elif self.compressingState == 1.5:
            if now( ) - self.timer >= self.pumpToggleDuration:
                self.pressTopMoveDown.set( LOW )
                self.compressingState = 1.75

        elif self.compressingState == 1.75:
            if self.pressTopPressureSensor.lastState >= self.topTargetPressure:
                self.pressTopMoveDown.set( HIGH )
                self.pressTopMoveUp.set( LOW )
                self.pressPumpEnable.set( LOW )
                self.pressPumpPrecisionEnable.set( HIGH )
                self.timer = now( )
                self.compressingState = 2

        elif self.compressingState == 2:
            if now( ) - self.timer >= self.loosenDuration / 1000:
                self.pressTopMoveUp.set( HIGH )
                self.pressSideMoveIn.set( LOW )
                self.pressPumpEnable.set( LOW )
                self.compressingState = 2.25

        elif self.compressingState == 2.25:
            if self.pressSidePressureSensor.lastState >= self.pumpTogglePressureThreshold:
                self.pressSideMoveIn.set( HIGH )
                self.timer = now( )
                self.compressingState = 2.5

        elif self.compressingState == 2.5:
            if now( ) - self.timer >= self.pumpToggleDuration:
                self.pressPumpPrecisionEnable.set( LOW )
                self.timer = now( )
                self.compressingState = 2.75

        elif self.compressingState == 2.75:
            if now( ) - self.timer >= self.pumpToggleDuration:
                self.pressSideMoveIn.set( LOW )
                self.compressingState = 3

        elif self.compressingState == 3:
            if self.pressSidePressureSensor.lastState > self.sideTargetPressure:
                self.pressSideMoveIn.set( HIGH )
                self.pressTopMoveDown.set( LOW )
                self.compressingState = 4

        elif self.compressingState == 4:
            if self.pressTopPressureSensor.lastState > self.topTargetPressure:
                self.pressTopMoveDown.set( HIGH )
                # self.pressPumpEnable.set( HIGH ) # leave pump enabled for entire compression
                self.compressingState = 0
                self.state = Press.COMPRESSED
                self.timer = now( )

    def handleCompressed( self ):
        if now( ) - self.timer > self.compressedDuration:
            self.pressTopMoveDown.set( HIGH )
            self.pressSideMoveIn.set( HIGH )
            self.pressPumpEnable.set( HIGH )
            self.timer = now( )
            self.state = Press.DECOMPRESSING
            return

        if self.pressTopPressureSensor.lastState < self.topTargetPressure - self.hysteresis:
            self.pressPumpEnable.set( LOW )
            self.pressTopMoveDown.set( LOW )
        elif self.pressTopPressureSensor.lastState >= self.topTargetPressure:
            # self.pressPumpEnable.set( HIGH )
            self.pressTopMoveDown.set( HIGH )

        if self.pressSidePressureSensor.lastState < self.sideTargetPressure - self.hysteresis:
            self.pressPumpEnable.set( LOW )
            self.pressSideMoveIn.set( LOW )
        elif self.pressSidePressureSensor.lastState >= self.sideTargetPressure:
            # self.pressPumpEnable.set( HIGH )
            self.pressSideMoveIn.set( HIGH )

    def handleDecompressing( self ):
        # depressurisation
        if self.decompressingState == 0:
            # self.pressPumpEnable.set( HIGH )
            self.pressTopMoveUp.set( LOW )
            self.pressSideMoveIn.set( LOW )
            self.timer = now( )
            self.decompressingState = 1

        elif self.decompressingState == 1:
            if now( ) - self.timer > self.depressurizationDuration:
                self.pressTopMoveUp.set( HIGH )
                self.pressSideMoveIn.set( HIGH )
                self.pressPumpPrecisionEnable.set( HIGH )
                self.pressPumpEnable.set( LOW )
                if self.pressSideHomeSensor.lastState == LOW:
                    self.pressSideMoveOut.set( LOW )
                    self.decompressingState = 2
                else:
                    pass  # todo błąd: możliwa awaria bocznego ścisku

        elif self.decompressingState == 2:
            if self.pressSideHomeSensor.lastState == HIGH:
                self.pressSideMoveOut.set( HIGH )
                if self.pressTopHomeSensor.lastState == LOW:
                    self.pressTopMoveUp.set( LOW )
                    self.pressPumpEnable.set( LOW )
                    self.decompressingState = 3
                else:
                    pass  # todo błąd: możliwa awaria górnego ścisku

        elif self.decompressingState == 3:
            self.timer = now( )
            self.partymakerEnable.set( LOW )
            self.decompressingState = 4

        elif self.decompressingState == 4:
            if now( ) - self.timer > self.shakeDuration:
                self.timer = now( )
                self.partymakerEnable.set( HIGH )
                self.decompressingState = 5

        elif self.decompressingState == 5:
            if now( ) - self.timer > self.shakeDuration:
                self.timer = now( )
                self.partymakerEnable.set( LOW )
                self.decompressingState = 6

        elif self.decompressingState == 6:
            if now( ) - self.timer > self.shakeDuration:
                self.timer = now( )
                self.partymakerEnable.set( HIGH )
                self.decompressingState = 7

        elif self.decompressingState == 7:
            if now( ) - self.timer > self.shakeDuration:
                self.timer = now( )
                self.partymakerEnable.set( LOW )
                self.decompressingState = 8

        elif self.decompressingState == 8:
            if now( ) - self.timer > self.shakeDuration:
                self.timer = now( )
                self.partymakerEnable.set( HIGH )
                self.decompressingState = 9

        elif self.decompressingState == 9:
            if now( ) - self.timer > self.shakeDuration:
                self.timer = now( )
                self.partymakerEnable.set( LOW )
                self.decompressingState = 10

        elif self.decompressingState == 10:
            if now( ) - self.timer > self.shakeDuration:
                self.timer = now( )
                self.partymakerEnable.set( HIGH )
                self.decompressingState = 11

        elif self.decompressingState == 11:
            if now( ) - self.timer > self.shakeDuration:
                self.timer = now( )
                self.partymakerEnable.set( LOW )
                self.decompressingState = 12

        elif self.decompressingState == 12:
            if now( ) - self.timer > self.shakeDuration:
                self.timer = now( )
                self.partymakerEnable.set( HIGH )
                self.decompressingState = 13

        elif self.decompressingState == 13:
            if self.pressTopHomeSensor.lastState == HIGH:
                self.pressTopMoveUp.set( HIGH )
                self.pressPumpEnable.set( HIGH )
                self.decompressingState = 0
                self.state = Press.UNLOADING

    def handleUnloading( self ):
        if self.unloadingState == 0:
            if self.pressConveyorEngine.state == LimitEngine.IDLE:
                self.pressConveyorEngine.run(
                    LimitEngine.FORWARD,
                    self.pressConveyorEngine.minLimitSensor
                )
                self.unloadingState = 1
            else:
                pass  # todo błąd: błąd taśmy prasy

        elif self.unloadingState == 1:
            if self.pressConveyorEngine.state == LimitEngine.IDLE:
                self.pressConveyorEngine.stop( )  # just in case :V
                self.unloadingState = 0
                self.bigBoy.sumTotalArea( )
                self.bigBoy.sumTotalHours( )
                self.state = Press.IDLE

    def setPressureThreshold( self, value ):
        self.pumpTogglePressureThreshold = value  # not really nesessary prop
        self.pressTopPressureSensor.thresholdRising = value
        self.pressTopPressureSensor.thresholdFalling = value
        self.pressSidePressureSensor.thresholdRising = value
        self.pressSidePressureSensor.thresholdFalling = value


if __name__ == '__main__':
    pass
