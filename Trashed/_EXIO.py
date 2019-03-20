from Trashed.MCP230XX import MCP230XX as MCP


class EXIO:
    """ Extended input output class """

    INPUT = 'input'
    OUTPUT = 'output'
    mcp = [ None ] * 8

    def __init__( self ):
        address = 0x20
        for i in range ( 8 ):
            self.mcp[ i ] = MCP( 'MCP23018', address )
            address += 1

    def output( self, pin, value ): # pin = [ 0, 127 ]
        extenderNumber = pin % 8 # pin = 111 -> 7
        extenderPin = extenderNumber * 16 - pin # -> 1
        self.mcp[ extenderNumber ].output( extenderPin, value )

    def input( self, pin ):
        extenderNumber = pin % 8
        extenderPin = extenderNumber * 16 - pin
        return self.mcp[ extenderNumber ].input( extenderPin )

    def setMode( self, pin, mode, pullUp = False ):
        extenderNumber = pin % 8  # pin = 111 -> 7
        extenderPin = extenderNumber * 16 - pin  # -> 1
        pullUp = 'enable' if pullUp else 'disable'
        self.mcp[ extenderNumber ].set_mode( extenderPin, mode, pullUp )