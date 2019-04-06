from time import time as now

# from Plank.BigBoy import BigBoy
from Plank.Input import Input
from Plank.Output import *
import Plank.Press
from Plank.Servo import Servo


class Vice:
    ROWS_GAP = 50

    IDLE = 0
    RELEASING = 1
    COMPRESSING = 2
    COMPRESSED = 3
    DECOMPRESSING = 4
    UNLOADING = 5

    inputs = [ ]

    state = 0
    releasingState = 0
    compressingState = 0
    # compressedState = 0
    decompressingState = 0
    unloadingState = 0

    readyToRelease = False
    readyToUnload = False

    timer = 0

    releaseStepsDuration = [
        1.5,  # odchylenie amortyzatora
        1.5,  # opuszczanie
        1.5,  # zwolnienie L
        .25,  # podnoszenie
        2.25,  # zaciśnięcie L
        2,  # powrót amortyzatora
    ]

    compressionStepsDuration = [
        2,  # opuszczenie zderzaka
        3,  # tylni zacisk
        3,  # boczny zacisk
    ]

    compressedDuration = 15

    decompressionStepsDuration = [
        5,  # zwolnienie bocznego zacisku
        .25,  # zwolnienie tylniego zacisku
        2,  # podniesienie zderzaka
    ]

    def __init__( self, bigBoy ):
        self.bigBoy = bigBoy
        # OUT
        self.slatDamperDisable = Output( bigBoy.orange, 51 )
        self.boardLowererEnable = Output( bigBoy.orange, 47 )
        self.boardReleaseEnable = Output( bigBoy.orange, 50 )
        self.bumperEnable = Output( bigBoy.orange, 53 )
        self.rearViceEnable = Output( bigBoy.orange, 46 )
        self.sideViceEnable = Output( bigBoy.orange, 52 )
        # IN
        self.rearViceDisabledSensor = Input( bigBoy.yellow, 7, name = 'Układarka, tylni ścisk - pozycja początkowa' )

        self.inputs += [
            # self.rearViceDisabledSensor,
        ]

    def update( self ):
        for input in self.inputs:
            input.update( )

        if self.state == Vice.IDLE:
            self.handleIdle( )

        elif self.state == Vice.RELEASING:
            self.handleReleasing( )

        elif self.state == Vice.COMPRESSING:
            self.handleCompressing( )

        elif self.state == Vice.COMPRESSED:
            self.handleCompressed( )

        elif self.state == Vice.DECOMPRESSING:
            self.handleDecompressing( )

        elif self.state == Vice.UNLOADING:
            self.handleUnloading( )

    def handleIdle( self ):
        if self.readyToRelease:
            self.readyToRelease = False
            self.state = Vice.RELEASING

    def handleReleasing( self ):
        if self.releasingState == 0:
            if self.bigBoy.conveyorServo.state == Servo.IDLE:
                self.slatDamperDisable.set( LOW )
                self.releasingState = 1
                self.timer = now( )

        elif self.releasingState == 1:
            if now( ) - self.timer > self.releaseStepsDuration[ self.releasingState - 1 ]:
                self.boardLowererEnable.set( LOW )
                self.releasingState = 2
                self.timer = now( )

        elif self.releasingState == 2:
            if now( ) - self.timer > self.releaseStepsDuration[ self.releasingState - 1 ]:
                self.boardReleaseEnable.set( LOW )
                self.releasingState = 3
                self.timer = now( )

        elif self.releasingState == 3:
            if now( ) - self.timer > self.releaseStepsDuration[ self.releasingState - 1 ]:
                self.boardLowererEnable.set( HIGH )
                self.releasingState = 4
                self.timer = now( )

        elif self.releasingState == 4:
            if now( ) - self.timer > self.releaseStepsDuration[ self.releasingState - 1 ]:
                self.boardReleaseEnable.set( HIGH )
                self.releasingState = 5
                self.timer = now( )

        elif self.releasingState == 5:
            if now( ) - self.timer > self.releaseStepsDuration[ self.releasingState - 1 ]:
                self.slatDamperDisable.set( HIGH )
                self.releasingState = 6
                self.timer = now( )

        elif self.releasingState == 6:
            if now( ) - self.timer > self.releaseStepsDuration[ self.releasingState - 1 ]:
                self.bumperEnable.set( LOW )
                self.releasingState = 0
                self.timer = now( )
                self.state = Vice.COMPRESSING

    def handleCompressing( self ):
        if self.compressingState == 0:
            if now( ) - self.timer > self.compressionStepsDuration[ self.compressingState - 1 ]:
                self.rearViceEnable.set( LOW )
                self.compressingState = 1
                self.timer = now( )

        elif self.compressingState == 1:
            if now( ) - self.timer > self.compressionStepsDuration[ self.compressingState - 1 ]:
                self.sideViceEnable.set( LOW )
                self.compressingState = 2
                self.timer = now( )

        elif self.compressingState == 2:
            if now( ) - self.timer > self.compressionStepsDuration[ self.compressingState - 1 ]:
                self.compressingState = 0
                self.timer = now( )
                self.state = Vice.COMPRESSED

    def handleCompressed( self ):
        if now( ) - self.timer > self.compressedDuration:
            self.timer = now( )
            self.state = Vice.DECOMPRESSING

    def handleDecompressing( self ):
        if self.decompressingState == 0:
            self.sideViceEnable.set( HIGH )
            self.decompressingState = 1
            self.timer = now( )

        elif self.decompressingState == 1:
            if now( ) - self.timer > self.decompressionStepsDuration[ self.decompressingState - 1 ]:
                self.rearViceEnable.set( HIGH )
                self.decompressingState = 2
                self.timer = now( )

        elif self.decompressingState == 2:
            if now( ) - self.timer > self.decompressionStepsDuration[ self.decompressingState - 1 ]:
                self.bumperEnable.set( HIGH )
                self.decompressingState = 3
                self.timer = now( )

        elif self.decompressingState == 3:
            if now( ) - self.timer > self.decompressionStepsDuration[ self.decompressingState - 1 ]:
                if self.bigBoy.currentRow != 0:
                    self.bigBoy.conveyorServo.move( self.bigBoy.slatLength + Vice.ROWS_GAP )
                self.decompressingState = 0
                if self.readyToUnload:
                    self.state = Vice.UNLOADING
                else:
                    self.state = Vice.IDLE

    def handleUnloading( self ):
        #  move the vice conveyor back a little to match the press conveyor
        if self.unloadingState == 0:
            if self.bigBoy.conveyorServo.state == Servo.IDLE:
                self.bigBoy.conveyorServo.move( - self.bigBoy.press.PRESS_CONVEYOR_CORRECTION )
                self.unloadingState = 1

        # wait for the conveyor to stop
        elif self.unloadingState == 1:
            if self.bigBoy.conveyorServo.state == Servo.IDLE:
                self.unloadingState = 2

        # pass the third step, the press controls when it starts
        elif self.unloadingState == 2:
            pass

        # start the conveyor
        elif self.unloadingState == 3:
            #     if self.bigBoy.press.state == Press.IDLE:
            #         if self.bigBoy.conveyorServo.state == Servo.IDLE:
            self.bigBoy.conveyorServo.engine.setForward( )
            self.bigBoy.conveyorServo.engine.start( )
            self.bigBoy.press.state = Plank.Press.Press.LOADING
            # self.unloadingState = 4

        # the press is controling state 3 -> 4 transition
        elif self.unloadingState == 4:
            self.bigBoy.conveyorServo.engine.stop( )
            self.unloadingState = 0
            self.state = Vice.IDLE
            self.readyToUnload = False
