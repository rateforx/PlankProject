from MCP230XX import MCP230XX
from Plank._EXIO import EXIO
import random
import time

io = MCP230XX( 'MCP23018', 0x23, '16bit' )
for pin in range( 16 ):
    io.set_mode( pin, 'output', 'enabled' )

try:
    while True:
        for pin in range( 16 ):
            io.output( pin, bool( random.getrandbits( 1 ) ) )
        time.sleep( 1 / 8 )
except KeyboardInterrupt:
    pass

# exio = EXIO()
#
# for pin in range( 16 ):
#     exio.mcp[ 4 ].set_mode( pin, 'output', 'enabled' )
#
# try:
#     while True:
#
#         # for extender in exio.mcp:
#         for pin in range( 16 ):
#             # extender.output( pin, random.getrandbits( 1 ) )
#             exio.mcp[ 4 ].output( pin, random.getrandbits( 1 ) )
#
#         # for pin in range( 63, 79 ):
#             # exio.output( pin, bool( random.getrandbits( 1 ) ) )
#             # exio.mcp[ pin % ( 16 - 1 ) ].output( pin % 16 )
#         time.sleep( 1 / 8 )
# except KeyboardInterrupt:
#     pass
