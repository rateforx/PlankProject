import sys
import subprocess
import _thread
import logging

from flask import Flask, render_template, request
from flask.json import jsonify

from Plank.BigBoy import *


class Server:
    app = None  # type: Flask
    log = logging.getLogger( 'werkzeug' )
    log.setLevel( logging.ERROR )

    def __init__( self ):
        self.bigBoy = BigBoy( )
        self.app = Flask(
            import_name = 'Stolmat',
            template_folder = 'Plank/templates',
            static_folder = 'Plank/static',
        )
        self.app.config[ 'TEMPLATES_AUTO_RELOAD' ] = True

        @self.app.route( '/' )
        def index( ):
            data = {
                'totalArea': round( self.bigBoy.totalArea, 3 ),
                'totalHours': round( self.bigBoy.totalHours, 2 ),
            }
            return render_template( 'index.html', data = data )

        @self.app.route( '/inputs' )
        def inputs( ):
            data = { }
            inputs = [ ]
            inputs += self.bigBoy.inputs
            inputs += self.bigBoy.vice.inputs
            inputs += self.bigBoy.press.inputs
            inputs += self.bigBoy.controls
            data[ 'inputs' ] = inputs

            return render_template( 'inputs.html', data = data )

        @self.app.route( '/api/inputs' )
        def apiInputs( ):
            inputs = [ ]
            inputs += self.bigBoy.inputs
            inputs += self.bigBoy.vice.inputs
            inputs += self.bigBoy.press.inputs
            inputs += self.bigBoy.controls

            data = [ ]
            for input in inputs:
                data.append( {
                    'name': input.name,
                    'lastState': input.lastState,
                } )

            return jsonify( data )

        @self.app.route( '/api/states' )
        def apiStates( ):
            return jsonify( self.getStates( ) )

        @self.app.route( '/params', methods = [ 'GET', 'POST' ] )
        def params( ):
            data = { }
            if request.method == 'GET':
                data.update( self.getProductionParams( ))
                return render_template( 'params.html', data = data )

            elif request.method == 'POST':
                slatLength = 0
                slatWidth = 0
                slatsPerBoard = 0
                bumperReset = 0

                try:
                    slatLength = int( request.form[ 'slatLength' ] )
                    slatWidth = int( request.form[ 'slatWidth' ] )
                    slatsPerBoard = int( request.form[ 'slatsPerBoard' ] )
                    bumperReset = int( request.form[ 'action' ] )
                except ValueError:
                    data[ 'error' ] = 'Podano niewłaświwą wartość!'
                finally:
                    if slatWidth * slatsPerBoard > self.bigBoy.PRESS_WIDTH:
                        data[ 'error' ] = 'Za duża szerokość płyty dla parametrów: \n' \
                                          'Szerokość lamelki: {}\n' \
                                          'Lamelki / Płyta: {}\n' \
                                          'Szerokość płyty: {}\n' \
                                          'Maksymalna szerokość płyty to: {}' \
                            .format( slatWidth, slatsPerBoard, slatWidth * slatsPerBoard, self.bigBoy.PRESS_WIDTH )
                        data.update( self.getProductionParams( ) )
                        return render_template( 'params.html', data = data )

                    else:
                        self.bigBoy.setParams( slatLength, slatWidth, slatsPerBoard )
                        self.bigBoy.recalculateParams( )

                        if bumperReset:
                            self.bigBoy.vice.state = Vice.RESETTING

                        data[ 'success' ] = 'Ustawiono parametry.'
                        data.update( self.getProductionParams( ) )
                        return render_template( 'params.html', data = data )

        @self.app.route( '/states' )
        def states( ):
            return render_template( 'states.html', data = self.getStates( ) )

        @self.app.route( '/prefs', methods = [ 'GET', 'POST' ] )
        def prefs( ):
            data = { }
            if request.method == 'GET':
                data.update( self.getPrefs( ) )
                return render_template( 'prefs.html', data = data )
            elif request.method == 'POST':
                viceCompressedDuration = 0
                pressCompressedDuration = 0
                pressTopTargetPressure = 0
                pressSideTargetPressure = 0
                pumpTogglePressureThreshold = 0
                pressLoosenDuration = 0
                conveyorCorrection = 0

                try:
                    viceCompressedDuration = int( request.form[ 'viceCompressedDuration' ] )
                    pressCompressedDuration = int( request.form[ 'pressCompressedDuration' ] )
                    pressTopTargetPressure = int( request.form[ 'pressTopTargetPressure' ] )
                    pressSideTargetPressure = int( request.form[ 'pressSideTargetPressure' ] )
                    pumpTogglePressureThreshold = int( request.form[ 'pumpTogglePressureThreshold' ] )
                    pressLoosenDuration = int( request.form[ 'pressLoosenDuration' ] )
                    conveyorCorrection = int( request.form[ 'conveyorCorrection' ] )
                except ValueError:
                    data[ 'error' ] = 'Podano niewłaświwą wartość!'
                finally:
                    self.bigBoy.vice.compressedDuration = viceCompressedDuration
                    self.bigBoy.press.compressedDuration = pressCompressedDuration
                    self.bigBoy.press.topTargetPressure = pressTopTargetPressure
                    self.bigBoy.press.sideTargetPressure = pressSideTargetPressure
                    self.bigBoy.press.setPressureThreshold( pumpTogglePressureThreshold )
                    self.bigBoy.press.loosenDuration = pressLoosenDuration
                    self.bigBoy.conveyorCorrection = conveyorCorrection
                    data.update( self.getPrefs( ) )
                    return render_template( 'prefs.html', data = data )

    def getStates( self ):
        return {
            'viceState': self.bigBoy.vice.state,
            'pressState': self.bigBoy.press.state,
            'currentSlat': self.bigBoy.currentSlat,
            'slatsPerBoard': self.bigBoy.slatsPerBoard,
            'currentBoard': self.bigBoy.currentBoard,
            'boardsPerRow': self.bigBoy.boardsPerRow,
            'currentRow': self.bigBoy.currentRow,
            'rowsPerSet': self.bigBoy.rowsPerSet,
            'pressTempTop': self.bigBoy.press.tempTop.lastState,
            'pressTempBottom': self.bigBoy.press.tempBottom.lastState,
            'pressPressureTop': self.bigBoy.press.pressTopPressureSensor.lastState,
            'pressPressureSide': self.bigBoy.press.pressSidePressureSensor.lastState,
        }

    def getProductionParams( self ):
        return {
            'slatLength': self.bigBoy.slatLength,
            'slatWidth': self.bigBoy.slatWidth,
            'slatsPerBoard': self.bigBoy.slatsPerBoard,
            'boardsPerRow': self.bigBoy.boardsPerRow,
            'rowsPerSet': self.bigBoy.rowsPerSet,
            'slatsPerSet': self.bigBoy.slatsPerSet,
            'boardLength': self.bigBoy.boardLength,
            'boardWidth': self.bigBoy.boardWidth,
        }

    def getPrefs( self ):
        return {
            'viceCompressedDuration': self.bigBoy.vice.compressedDuration,
            'pressCompressedDuration': self.bigBoy.press.compressedDuration,
            'pressTopTargetPressure': self.bigBoy.press.topTargetPressure,
            'pressSideTargetPressure': self.bigBoy.press.sideTargetPressure,
            'pumpTogglePressureThreshold': self.bigBoy.press.pumpTogglePressureThreshold,
            'pressLoosenDuration': self.bigBoy.press.loosenDuration,
            'conveyorCorrection': self.bigBoy.conveyorCorrection,
            'viceConveyorSpeed': self.bigBoy.viceConveyorSpeed,
            'pressConveyorSpeed': self.bigBoy.pressConveyorSpeed,
        }

    def start( self ):
        _thread.start_new_thread( self.bigBoy.run, ( ) )
        subprocess.Popen( [
            'chromium-browser',
            '--profile-directory=Default',
            '--app-id=mleldakmoebeolhcnjndafbokokbkgcn',
            '--name=Stolmat',
            '--start-fullscreen',
        #     '--app=http://localhost:5000/'
        ] )
        self.app.run(
            host = '0.0.0.0',
            port = 5000,
        )


if __name__ == '__main__':
    sys.path.extend( [ '/home/pi/Desktop/BigBoy', '/home/pi/Desktop/BigBoy' ] )
    server = Server( )
    server.start( )