from time import time as now

from Plank.ArduinoSerialPortFinder import UNO_SN1
from Plank.Encoder import Encoder
from Plank.Input import Input
from Plank.Output import *
import Plank.Press
from Plank.Servo import Servo, SimpleServo

A0 = 54
A1 = 55


class Vice:
    IDLE = 0
    RELEASING = 1
    COMPRESSING = 2
    COMPRESSED = 3
    DECOMPRESSING = 4
    UNLOADING = 5
    RESETTING = 6

    inputs = [ ]

    state = 0
    releasingState = 0
    compressingState = 0
    # compressedState = 0
    decompressingState = 0
    unloadingState = 0
    resettingState = 0

    readyToRelease = False
    readyToUnload = False
    forceUnloading = False

    timer = 0

    conveyorSpeed = 50

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
        7,  # tylni zacisk
        3,  # boczny zacisk
    ]

    compressedDuration = 15

    decompressionStepsDuration = [
        3,  # zwolnienie bocznego zacisku
        .25,  # zwolnienie tylniego zacisku
        2,  # podniesienie zderzaka
    ]

    def __init__( self, bigBoy ):
        self.bigBoy = bigBoy

        self.glueDisable = Output( bigBoy.orange, 49, LOW )
        self.halfTurnMotorEnable = Output( bigBoy.yellow, 50 )
        self.slatPusherEnable = Output( bigBoy.orange, 22 )
        self.slatDamperDisable = Output( bigBoy.orange, 51 )
        self.boardLowererEnable = Output( bigBoy.orange, 47 )
        self.boardReleaseEnable = Output( bigBoy.orange, 50 )
        self.bumperEnable = Output( bigBoy.orange, 53 )
        self.rearViceEnable = Output( bigBoy.orange, 46 )
        self.sideViceEnable = Output( bigBoy.orange, 52 )
        self.bumperEngineForwardEnable = Output( bigBoy.yellow, 47 )
        self.bumperEngineBackwardEnable = Output( bigBoy.yellow, 46 )

        self.bumperServo = SimpleServo(
            self.bumperEngineForwardEnable, self.bumperEngineBackwardEnable, Encoder( UNO_SN1 )
        )
        self.bumperFrontLimit = Input(
            bigBoy.yellow, 2, name = 'Układarka, rozjazd - krańcówka przednia', pausable = False )
        self.bumperBackLimit = Input(
            bigBoy.yellow, 4, name = 'Układarka, rozjazd - krańcówka tylnia', pausable = False )

        self.inputs += [
            self.bumperFrontLimit,
            self.bumperBackLimit,
        ]

        def viceBumperFrontLimitRising( ):
            self.bumperEngineForwardEnable.set( HIGH )

        self.bumperFrontLimit.setCallback( viceBumperFrontLimitRising, RISING )

        def viceBumperBackLimitRising( ):
            self.bumperEngineBackwardEnable.set( HIGH )

        self.bumperBackLimit.setCallback( viceBumperBackLimitRising, RISING )

    def update( self ):
        running = self.bigBoy.viceRunning
        for input in self.inputs:
            input.update( not running )

        self.bumperServo.update( )

        if self.state == Vice.IDLE and running:
            self.handleIdle( )

        elif self.state == Vice.RELEASING:  # and running:
            self.handleReleasing( )

        elif self.state == Vice.COMPRESSING:  # and running:
            self.handleCompressing( )

        elif self.state == Vice.COMPRESSED and running:
            self.handleCompressed( )

        elif self.state == Vice.DECOMPRESSING and running:
            self.handleDecompressing( )

        elif self.state == Vice.UNLOADING and running or self.forceUnloading:
            self.handleUnloading( )

        elif self.state == Vice.RESETTING:
            self.handleResetting( )

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

                distance = self.bigBoy.slatLength + self.bigBoy.rowsGap
                if self.bigBoy.currentRow != 0:
                    self.bigBoy.conveyorServo.move( distance )
                elif self.readyToUnload:
                    distance = self.bigBoy.conveyorCorrection
                    self.bigBoy.conveyorServo.move( distance )

                self.decompressingState = 0
                if self.readyToUnload:
                    self.readyToUnload = False
                    self.state = Vice.UNLOADING
                else:
                    self.readyToUnload = False  # why even bother!?
                    self.state = Vice.IDLE

    def handleUnloading( self ):
        if self.unloadingState == 0:
            if self.bigBoy.conveyorServo.state == Servo.IDLE:
                # self.bigBoy.conveyorServo.move( self.bigBoy.conveyorCorrection )
                # self.timer = now( )
                self.unloadingState = 2

        # wait for the conveyor to stop
        elif self.unloadingState == 1:
            if self.bigBoy.conveyorServo.state == Servo.IDLE:
                if now( ) - self.timer > 2:
                    self.unloadingState = 2

        # pass the third step, the press controls when it starts
        elif self.unloadingState == 2:
            pass

        # start the conveyor
        elif self.unloadingState == 3:
            self.bigBoy.conveyorServo.engine.setForward( )
            self.bigBoy.conveyorServo.engine.start( )
            self.bigBoy.press.state = Plank.Press.Press.LOADING
           # the press is controlling state 3 -> 4 transition

        elif self.unloadingState == 4:
            self.bigBoy.conveyorServo.engine.stop( )
            self.unloadingState = 0
            self.forceUnloading = False
            self.readyToUnload = False
            self.state = Vice.IDLE

    def handleResetting( self ):
        if self.resettingState == 0:
            if self.bumperBackLimit.lastState == LOW:
                self.bumperEngineBackwardEnable.set( LOW )
                self.resettingState = 1
            else:
                self.resettingState = 2

        # move to starting point
        elif self.resettingState == 1:
            if self.bumperBackLimit.lastState == HIGH:
                self.bumperEngineBackwardEnable.set( HIGH )
                self.resettingState = 2

        elif self.resettingState == 2:
            self.bumperServo.move( self.bigBoy.slatLength )
            self.resettingState = 3

        elif self.resettingState == 3:
            if self.bumperServo.state == SimpleServo.IDLE:
                self.resettingState = 0
                self.state = Vice.IDLE
