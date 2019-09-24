#define INPUT_SIZE 32
#define COMMAND_CHAR '('
#define SEPARATOR_CHAR ','
#define TERMINATOR_CHAR ')'
#define MAXIO 70

struct Input {
    int lastState = -1;
    bool enabled = false;
    bool analog = false;
};

Input inputs[ MAXIO ];
bool running = false;

void pinSetup( int pin, int mode ) {
    switch( mode ) {
        case 0:
            pinMode( pin, OUTPUT );
            inputs[ pin ].enabled = false;
            inputs[ pin ].analog = false;
            break;

        case 1:
            pinMode( pin, INPUT );
            inputs[ pin ].enabled = true;
            inputs[ pin ].analog = false;
            break;

        case 2:
            pinMode( pin, INPUT_PULLUP );
            inputs[ pin ].enabled = true;
            inputs[ pin ].analog = false;
            break;

        case 3:
            pinMode( pin, INPUT );
            inputs[ pin ].enabled = true;
            inputs[ pin ].analog = true;
            break;
    }
}

int pinRead( int pin ) {
    return digitalRead( pin );
}

int pinAnalogRead( int pin ) {
    return map( analogRead( pin ), .1 * 1024, .9 * 1024, 0, 250 );
}

void pinWrite( int pin, int value ) {
    switch( value ) {
        case 0:
            digitalWrite( pin, LOW );
            break;
        case 1:
            digitalWrite( pin, HIGH );
            break;
    }
}

void setup( ) {
    Serial.begin( 115200 );

    for( int pin = 22; pin < 30; pin++ ) {
        digitalWrite( pin, HIGH );
        pinMode( pin, OUTPUT );
    }
    for( int pin = 46; pin < 54; pin++ ) {
        digitalWrite( pin, HIGH );
        pinMode( pin, OUTPUT );
    }
}

void loop( ) {
    if( running ) {
        for ( int pin = 0; pin < MAXIO; pin++ ) {
            if ( inputs[ pin ].enabled ) {
                int value = inputs[ pin ].analog ? pinAnalogRead( pin ) : pinRead( pin );
                if ( value != inputs[ pin ].lastState ) {
                    inputs[ pin ].lastState = value;

                    Serial.print( pin );
                    Serial.print( ':' );
                    Serial.print( value );
                    Serial.println( ';' );

                    if ( inputs[ pin ].analog ) inputs[ pin ].enabled = false;
                }
            }
        }
    }

    if( Serial.available() ) {

        String command = Serial.readStringUntil( COMMAND_CHAR );

        int pin = -1;
        int value = -1;
        switch( command[ 0 ] ) {

            case 'm':
                pin = Serial.readStringUntil( SEPARATOR_CHAR ).toInt();
                value = Serial.readStringUntil( TERMINATOR_CHAR ).toInt();
                pinSetup( pin, value );
                break;

            case 'w':
                pin = Serial.readStringUntil( SEPARATOR_CHAR ).toInt();
                value = Serial.readStringUntil( TERMINATOR_CHAR ).toInt();
                pinWrite( pin, value );
                break;

//            case 'r':
//                pin = Serial.readStringUntil( TERMINATOR_CHAR ).toInt();
//                value = pinRead( pin );
//                Serial.println( value );
//                break;

            case 'a':
                pin = Serial.readStringUntil( TERMINATOR_CHAR ).toInt();
                inputs[ pin ].enabled = true;
                break;

            case 's':
                running = true;
                break;

            case 'b':
                running = false;
                break;
        }
    }
}