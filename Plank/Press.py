from time import time as now

from Plank.LimitEngine import LimitEngine
# from Plank.BigBoy import BigBoy
from Plank.Engine import Engine
from Plank.Input import Input
from Plank.Output import *
from Plank.TemperatureSensor import TemperatureSensor


class Press:
    PRESS_CONVEYOR_CORRECTION = 700  # mm

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

    timer = 0
    compressedDuration = 120
    loosenDuration = .5
    depresurizzationDuration = 3
    targetTopPressure = 100
    targetSidePressure = 100

    def __init__( self, bigBoy ):
        self.bigBoy = bigBoy
        # IN
        self.pressTopHomeSensor = Input( bigBoy.yellow, 56, name = 'Prasa, góra - pozycja początkowa' )  # A2
        self.pressSideHomeSensor = Input( bigBoy.yellow, 57, name = 'Prasa, bok - pozycja początkowa' )  # A3
        self.pressTopPressureSensor = Input( bigBoy.yellow, 66, name = 'Ciśnienie prasy, góra' )  # A12
        self.pressSidePressureSensor = Input( bigBoy.yellow, 68, name = 'Ciśnienie prasy, bok' )  # A14

        # OUT
        self.pressTopMoveUp = Output( bigBoy.yellow, 23 )
        self.pressTopMoveDown = Output( bigBoy.yellow, 22 )
        self.pressSideMoveIn = Output( bigBoy.yellow, 24 )
        self.pressSideMoveOut = Output( bigBoy.yellow, 25 )
        self.pressPumpEnable = Output( bigBoy.yellow, 53 )
        self.pressPumpPrecisionEnable = Output( bigBoy.yellow, 52 )
        self.pressPumpVentEnable = Output( bigBoy.yellow, 51 )

        self.tempTop = TemperatureSensor( 0 )
        self.tempDown = TemperatureSensor( 1 )

        self.pressConveyorEngine = LimitEngine(
            Engine( bigBoy.yellow, pwmPin = 24, runPin = 28, dirPin = 29, dutyCycle = 50 ),
            minLimitSensor = Input( bigBoy.yellow, 55, name = 'Czujnik indukcyjny: prasa - początek' ),  # A1
            maxLimitSensor = Input( bigBoy.yellow, 54, name = 'Czujnik indukcyjny: prasa - koniec' ),  # A0
        )

        self.inputs += [
            self.pressTopHomeSensor,
            self.pressSideHomeSensor,
            self.pressTopPressureSensor,
            self.pressSidePressureSensor,
            self.pressConveyorEngine.minLimitSensor,
            self.pressConveyorEngine.maxLimitSensor,
        ]

    def update( self ):
        self.pressTopHomeSensor.update( )
        self.pressSideHomeSensor.update( )
        self.pressTopPressureSensor.update( )
        self.pressSidePressureSensor.update( )
        self.tempTop.update( )
        self.tempDown.update( )
        self.pressConveyorEngine.update( )

        if self.state == Press.IDLE:
            pass

        elif self.state == Press.LOADING:
            self.handleLoading( )

        elif self.state == Press.COMPRESSING:
            self.handleCompressing( )

        elif self.state == Press.COMPRESSED:
            self.handleCompressed( )

        elif self.state == Press.DECOMPRESSING:
            self.handleDecompressing( )

        elif self.state == Press.UNLOADING:
            self.handleUnloading( )

    def handleLoading( self ):
        if self.bigBoy.vice.readyToUnload and self.bigBoy.vice.unloadingState == 2:
            if self.pressConveyorEngine.minLimitSensor.lastState == HIGH:
                if self.pressTopHomeSensor.lastState == HIGH and self.pressSideHomeSensor.lastState == HIGH:
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
                self.state = Press.COMPRESSING
                self.timer = now( )

    def handleCompressing( self ):
        if self.compressingState == 0:
            if self.pressTopHomeSensor.lastState == HIGH:
                if self.pressTopPressureSensor.lastState > self.targetTopPressure:
                    pass  # todo błąd: za wysokie ciśnienie na blacie
                self.pressPumpEnable.set( LOW )
                self.pressTopMoveDown.set( LOW )
                self.compressingState = 1

        elif self.compressingState == 1:
            if self.pressTopPressureSensor.lastState > self.targetTopPressure / 2:
                self.pressTopMoveDown.set( HIGH )
                self.pressTopMoveUp.set( LOW )
                self.timer = now( )
                self.compressingState = 2

        elif self.compressingState == 2:
            if now( ) - self.timer >= self.loosenDuration:
                if self.pressSidePressureSensor.lastState > self.targetSidePressure:
                    pass  # todo błąd: za wysokie ciśnienie na bocznym ścisku
                self.pressTopMoveUp.set( HIGH )
                self.pressSideMoveIn.set( LOW )
                self.compressingState = 3

        elif self.compressingState == 3:
            if self.pressSidePressureSensor.lastState > self.targetSidePressure / 2:
                self.pressPumpPrecisionEnable.set( LOW )
                self.compressingState = 4

        elif self.compressingState == 4:
            if self.pressSidePressureSensor.lastState > self.targetSidePressure:
                self.pressSideMoveIn.set( HIGH )
                self.pressTopMoveDown.set( LOW )
                self.compressingState = 5

        elif self.compressingState == 5:
            if self.pressTopPressureSensor.lastState > self.targetTopPressure:
                self.pressTopMoveDown.set( HIGH )
                self.pressPumpEnable.set( HIGH )
                self.compressingState = 0
                self.state = Press.COMPRESSED
                self.timer = now( )

    def handleCompressed( self ):
        if now( ) - self.timer > self.compressedDuration:
            self.pressTopMoveDown.set( HIGH )
            self.pressSideMoveIn.set( HIGH )
            self.pressPumpEnable.set( HIGH )
            self.pressPumpPrecisionEnable.set( HIGH )
            self.timer = now( )
            self.state = Press.DECOMPRESSING
            return

        if self.pressTopPressureSensor.lastState == LOW:
            self.pressPumpEnable.set( LOW )
            self.pressTopMoveDown.set( LOW )
        elif self.pressTopPressureSensor.lastState == HIGH:
            self.pressPumpEnable.set( HIGH )
            self.pressTopMoveDown.set( HIGH )

        if self.pressSidePressureSensor.lastState == LOW:
            self.pressPumpEnable.set( LOW )
            self.pressSideMoveIn.set( LOW )
        elif self.pressSidePressureSensor.lastState == HIGH:
            self.pressPumpEnable.set( HIGH )
            self.pressSideMoveIn.set( HIGH )

    def handleDecompressing( self ):
        if self.decompressingState == 0:
            self.pressPumpVentEnable.set( LOW )
            self.timer = now( )
            self.decompressingState = 1

        elif self.decompressingState == 1:
            if now( ) - self.timer > self.depresurizzationDuration:
                self.pressPumpVentEnable.set( HIGH )
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
                    self.decompressingState = 3
                else:
                    pass  # todo błąd: możliwa awaria górnego ścisku

        elif self.decompressingState == 3:
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
                self.state = Press.IDLE


if __name__ == '__main__':
    pass
