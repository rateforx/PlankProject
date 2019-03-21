import time
from Plank.Encoder import Encoder
from Trashed.MCP230XX import MCP230XX

mcp = MCP230XX( 0x22 )

engine = Engine( , 20, 10, 13 )
engine.setSpeed( 100 )

encoder = Encoder()

engine.runBoard( )
try:
    pos = int( encoder.serial.readline( ) )
except ValueError:
    pos = 0

distance = 1000
speed = 100

while True:
    try:
        pos = int( encoder.serial.readline( ) )
        # print( pos )

        if pos > 0.8 * distance and engine.__direction == engine.CLOCKWISE:
            engine.setSpeed( speed / 4 )

        if pos > distance and engine.__direction == engine.CLOCKWISE:
            engine.stop( )
            engine.reverse( )
            engine.setSpeed( speed )
            time.sleep( 1 )
            engine.slowStart( 3 )

        if pos < - 0.8 * distance and engine.__direction == engine.ANTICLOCKWISE:
            engine.setSpeed( speed / 4 )

        if pos < - distance and engine.__direction == engine.ANTICLOCKWISE:
            engine.stop()
            engine.reverse()
            engine.setSpeed( speed )
            time.sleep( 1 )
            engine.slowStart( 3 )
    except ValueError:
        print( 'Could not convert data to integer.' )
    except OSError as e:
        print( "I/O error({0}): {1}".format( e.errno, e.strerror ) )
