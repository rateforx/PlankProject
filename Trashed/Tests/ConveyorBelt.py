import time
from RPi import GPIO
# from Plank.Encoder import Encoder
from Plank.Engine import Engine
from serial import Serial

GPIO.setmode( GPIO.BCM )

serial = Serial('/dev/ttyACM2', 9600)
# encoder = Encoder( 22, 23 )
engine = Engine( 21, 20, 26 )

# engine.reverse()
engine.setSpeed( 100 )
engine.start()

counter = 0
distance = 500
# breakingDistance = 1000

while True:
    try:
        counter += int( serial.readline() )
        print( counter )

        if counter > distance:
            engine.stop()
            time.sleep(.5)
            counter = 0
            engine.reverse()
            distance *= -1
            engine.setSpeed(100)
            engine.start()
    finally:
        pass

# while True:
#     while encoder.counter < distance:
#         if encoder.counter > breakingDistance:
#             engine.setSpeed( 25 )
#         time.sleep( 1 / 60 )
#
#     engine.stop()
#     time.sleep( .5 )
#     encoder.counter = 0
#     # engine.reverse()
#     engine.setSpeed( 100 )
#     engine.start()