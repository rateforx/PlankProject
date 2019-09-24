#define INPUT_SIZE      32
#define DECODE          '\''
#define COMMAND_CHAR    '('
#define SEPARATOR_CHAR  ','
#define TERMINATOR_CHAR ')'

#define STOP_COMMAND "STOP"

#define CW    1
#define CCW   0
#define UNSET -1

volatile long counter = 0;
volatile long lastCount = 0;
int aPin = 3;
int bPin = 4;

volatile int direction = UNSET;
volatile long target = 0;

void callback() {
  if ( digitalRead( bPin ) == LOW ) {
    counter++;
  } else {
    counter--;
  }
}

void setup() {
  Serial.begin( 115200 );
  pinMode( aPin, INPUT );
  pinMode( bPin, INPUT );
  attachInterrupt( digitalPinToInterrupt( 3 ), callback, RISING );
}

void loop() {
  if( Serial.available() > 0 ) {
    String command = Serial.readStringUntil( COMMAND_CHAR );

    int pin = -1;
    int value = -1;
    switch( command[ 0 ] ) {

      case 'm':
        value = Serial.readStringUntil( TERMINATOR_CHAR ).toInt();
        target = counter + value;
        direction = value > 0 ? CW : CCW;

//        Serial.print( counter );
//        Serial.print( " -> " );
//        Serial.println( target );
        break;
      
      case 'r':
//        pin = Serial.readStringUntil( TERMINATOR_CHAR ).toInt();
//        value = pinRead( pin );
//        Serial.println( value );
        break;
    }
  }

  switch( direction ) {
    case CW:
      if( counter >= target ) {
        Serial.println( STOP_COMMAND );
        direction = UNSET;
      }
      break;
    case CCW:
      if( counter <= target ) {
        Serial.println( STOP_COMMAND );
        direction = UNSET;
      }
      break;
    case UNSET:
      break;
  }
  
//  if ( counter != lastCount ) {
//    lastCount = counter;
//    Serial.println( counter );
//  }
//
//  if( Serial.available() > 0 ) {
//    if( Serial.read() == 'r' ) {
//      Serial.println( counter );
//    }
//  }
}

