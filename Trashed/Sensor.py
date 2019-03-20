from RPi import GPIO
import time

PULL_UP = 1
PULL_DOWN = -1

GPIO.setmode( GPIO.BCM )

class Sensor:

    def __init__( self, pin, pullUpDown = GPIO.PUD_OFF ):
        self.pin = pin

        GPIO.setup( pin, GPIO.IN, pullUpDown )

    def attachCallback( self, *args, **kwargs ):
        GPIO.add_event_detect( *args, **kwargs )