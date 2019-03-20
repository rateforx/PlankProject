import sys
from RPi import GPIO
from Plank.Engine import Engine

GPIO.setmode( GPIO.BCM )

engine = Engine( 21, 20, 26 )

engine.stop()

GPIO.cleanup()

del engine
# sys.exit( 0 )