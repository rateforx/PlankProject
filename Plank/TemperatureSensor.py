from w1thermsensor import W1ThermSensor
import _thread

sensorIds = [
    '00000a01a45b',
    '00000a02e5e8',
]


class TemperatureSensor:
    verbose = False

    def __init__( self, id ):
        self.id = sensorIds[ id ]
        self.sensor = W1ThermSensor( sensor_id = sensorIds[ id ] )
        self.lastState = self.sensor.get_temperature( )

    def getTemperature( self ):
        self.lastState = self.sensor.get_temperature( )
        if self.verbose:
            print( '{} temp: {}'.format( self.id, self.lastState ) )
        return
        # self.update()

    def update( self ):
        try:
            if _thread._count( ) < 6:
                _thread.start_new_thread( self.getTemperature, [ ] )
        except:
            print( 'Unable to start new thread.' )

if __name__ == '__main__':
    t0 = TemperatureSensor( 0 )
    t1 = TemperatureSensor( 1 )

    t0.verbose = True
    t1.verbose = True

    while True:
        t0.update()
        t1.update()
