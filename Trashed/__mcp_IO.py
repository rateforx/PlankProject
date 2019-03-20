from Trashed.MCP230XX import MCP230XX as MCP


class Input:
    """ MCP230XX wrapper for generic input """

    def __init__( self, mcp: MCP, pin, pullUp = False ):
        self.mcp = mcp
        self.pin = pin
        self.initialState = self.getState()
        self.lastState = self.getState()

        # mcp.set_mode( pin, 'input', 'enable' if pullUp else 'disable' )

    def getState( self ):
        self.lastState = self.mcp.input( self.pin )
        return self.lastState

    def onLow( self, callback ):
        self.mcp.add_interrupt( self.pin, callbackFunctLow = callback )

    def onHigh( self, callback ):
        self.mcp.add_interrupt( self.pin, callbackFunctHigh = callback )


class Output:
    """ MCP230XX wrapper for generic output """

    def __init__( self, mcp: MCP, pin ):
        self.mcp = mcp
        self.pin = pin

        mcp.set_mode( pin, 'output' )

    def set( self, value ):
        self.mcp.output( self.pin, value )