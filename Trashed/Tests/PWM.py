import RPi.GPIO as GPIO
import time

PWM_PIN = 21

GPIO.setmode( GPIO.BCM )
GPIO.setwarnings( False )
GPIO.setup( PWM_PIN, GPIO.OUT )

frequency = 1000
pwm = GPIO.PWM( PWM_PIN, frequency )
dutyCycle = 0
pwm.start( dutyCycle )

try:
    while True:
        for dutyCycle in range( 0, 100, 5 ):
            pwm.ChangeDutyCycle( dutyCycle )
            time.sleep( 1 / 60 )
        for dutyCycle in range( 100, 0, 5 ):
            pwm.ChangeDutyCycle( dutyCycle )
            time.sleep( 1 / 60 )
except KeyboardInterrupt:
    pass
pwm.stop()
GPIO.cleanup()
