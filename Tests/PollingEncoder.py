from RPi import GPIO
from time import sleep

aPin = 17
bPin = 18

GPIO.setmode( GPIO.BCM )
GPIO.setup( aPin, GPIO.IN, pull_up_down=GPIO.PUD_OFF )
GPIO.setup( bPin, GPIO.IN, pull_up_down=GPIO.PUD_OFF )

counter = 0
aLastState = GPIO.input( aPin )

try:
    while True:
        aState = GPIO.input( aPin )
        bState = GPIO.input( bPin )
        if aState != aLastState:
            if bState != aState:
                counter += 1
            else:
                counter -= 1
            print( counter )
        aLastState = aState
        sleep( 1 / 1000000 )
finally:
    GPIO.cleanup( )
