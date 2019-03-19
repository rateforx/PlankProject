from MCP230XX import MCP23018 as MCP
import random
import time

mcps = list( )

def init():
    global mcps
    mcps = list()

    mcps.append( MCP( 0x22 ) )
    # mcps.append( MCP( 0x24 ) )
    # mcps.append( MCP( 0x25 ) )
    # mcps.append( MCP( 0x26 ) )

    for mcp in mcps:
        for pin in range( 0, 16 ):
            mcp.output( pin, 1 )

def outputRandom( ):
    try:
        for mcp in mcps:
            for pin in range( 0, 16 ):
                mcp.output( pin, random.getrandbits( 1 ) )
    except OSError:
        init()

def setAll( value ):
    for mcp in mcps:
        for pin in range( 0, 16 ):
            mcp.output( pin, value )

def setInterval( function, delay ):
    try:
        while True:
            function()
            time.sleep( delay )
    except KeyboardInterrupt:
        pass

try:
    init()
    setInterval( outputRandom, 1 )
except OSError:
    print( 'errno121, restarting...' )
    init( )