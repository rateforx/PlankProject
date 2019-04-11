import serial.tools.list_ports

MEGA_SN0 = '857333237393510172E0'
MEGA_SN1 = '85334333831351D00110'
UNO_SN0  = '95635333531351501131'
UNO_SN1  = '75735303132351A030C1'


class ArduinoSerialPortFinder:

    def getArduinoPort( serialNumber: str ):
        ports = list( serial.tools.list_ports.comports( ) )
        for port in ports:
            if serialNumber in str( port.serial_number ):
                return port.device
        return None


if __name__ == '__main__':
    print( 'Uno port: {}'.format( ArduinoSerialPortFinder.getArduinoPort( UNO_SN0 ) ) )
    print( 'Mega port: {}'.format( ArduinoSerialPortFinder.getArduinoPort( MEGA_SN0 ) ) )
