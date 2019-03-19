import time
import RPi.GPIO as GPIO
from MCP230XX import MCP23018

mcp = None
pressCounter = 0
releaseCounter = 0

def buttonPressedHandler( pin ):
    global pressCounter
    print( pressCounter, 'interrupt: pin#', pin, '-> high.' )
    pressCounter += 1


def buttonReleasedHandler( pin ):
    global releaseCounter
    print( releaseCounter, 'interrupt: pin#', pin, '-> low.' )
    releaseCounter += 1


def init( ):
    global mcp
    interruptPin = 26
    mcp = MCP23018( 0x20, interruptPin )

    for pin in range( 0, 16 ):
        # mcp.invert_input( pin, True )
        mcp.add_interrupt(
            pin = pin,
            callbackFunctLow = buttonReleasedHandler,
            callbackFunctHigh = buttonPressedHandler
        )
        time.sleep( .01 )

try:
    init( )
except OSError:
    init( )
except KeyboardInterrupt:
    GPIO.cleanup( )
