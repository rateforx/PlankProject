from Plank.Engine import Engine
from Plank.Input import Input, HIGH

class LimitEngine:
    IDLE = 0
    MOVING = 1

    FORWARD = 1
    BACKWARD = 0
    UNSET = -1

    limitSensor = None # type: Input
    direction = UNSET
    state = IDLE

    def __init__(
            self,
            engine: Engine,
            minLimitSensor: Input,
            maxLimitSensor: Input,
    ):
        self.engine = engine
        self.minLimitSensor = minLimitSensor
        self.maxLimitSensor = maxLimitSensor

    def run( self, direction: int, limitInput: Input ):
        self.direction = direction
        self.limitSensor = limitInput

        if  0 <= direction <= 1 and limitInput is not None and limitInput.getState() != HIGH:
            self.engine.setForward( ) if direction == LimitEngine.FORWARD else self.engine.setBackward( )
            self.engine.start( )
            self.state = LimitEngine.MOVING

    def update( self ):
        self.minLimitSensor.update()
        self.maxLimitSensor.update()

        if self.direction != LimitEngine.UNSET:
            if self.limitSensor is not None:
                if self.limitSensor.lastState == HIGH:
                    self.engine.stop( )
                    self.direction = LimitEngine.UNSET
                    self.limitSensor = None
                    self.state = LimitEngine.IDLE
            else:
                self.engine.stop( )
                self.direction = None
                self.state = LimitEngine.IDLE

    def stop( self ):
        self.engine.stop( )
        self.direction = LimitEngine.UNSET
        self.limitSensor = None
        self.state = LimitEngine.IDLE

if __name__ == '__main__':
    pass
    # lengthSled = LengthSled( press.yellow, 47, 46, 2, 4 )
