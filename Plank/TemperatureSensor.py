from w1thermsensor import W1ThermSensor
from w1thermsensor.errors import SensorNotReadyError
import _thread

sensorIds = [
    '00000a01a45b',
    '00000a02e5e8',
]

LOW = 0
HIGH = 1

MAX_THREADS = 1


class TemperatureSensor:
    def __init__( self, id ):
        self.threadExists = False
        self.running = False
        self.verbose = False
        self.id = sensorIds[ id ]
        self.sensor = W1ThermSensor( sensor_id = sensorIds[ id ] )
        self.lastState = -1

    def update( self ):
        while self.running:
            try:
                value = self.getTemperature( )
                self.lastState = value
            except SensorNotReadyError:
                print( 'Temperature sensor error cought, continuing...' )

    def getTemperature( self ):
        value = self.sensor.get_temperature( )
        if self.verbose:
            print( '{} temp: {}'.format( self.id, value ) )
        return value

    def start( self ):
        if not self.threadExists:
            _thread.start_new_thread( self.update, ( ) )
            self.threadExists = True
            self.running = True

    def pause( self ):
        self.running = False

    def resume( self ):
        self.running = True


if __name__ == '__main__':
    t0 = TemperatureSensor( 0 )
    t1 = TemperatureSensor( 1 )

    t0.verbose = True
    t1.verbose = True

    while True:
        t0.start( )
        t1.start( )
