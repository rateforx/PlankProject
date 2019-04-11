const freq = 1 / 30;
let timer;

function getInputsData( ) {
    timer = Date.now();
    $.ajax('/api/inputs', {
        success: inputs => {
            updateInputs( inputs );
        },
        error: () => {
            M.toast( {
                html: 'Nie udało się pobrać stanu wejść',
                displayLength: 1000,
            } );
            getInputsData( );
        },
        timeout: 1000,
    });
}

function updateInputs( inputs ) {
    for( let i = 0; i < inputs.length; i++ ) {

        let item = $( `#inputs ul li:nth-child( ${ i + 1 } ) span.input-state` );
        if( inputs[ i ].lastState === 1 ) {
            item.addClass( 'green' );
            item.removeClass( 'red' );
            item.attr( 'data-badge-caption', 'HIGH' );
        } else {
            item.addClass( 'red' );
            item.removeClass( 'green' );
            item.attr( 'data-badge-caption', 'LOW' )
        }

    }

    if ( Date.now( ) - timer > freq )
        getInputsData( );
    else
        setTimeout( getInputsData, freq - Date.now( ) - timer )
}

function getStatesData( ) {
    $.ajax( '/api/states', {
        success: states => {
            updateStates( states );
        },
        error: () => {
            M.toast( {
                html: 'Nie udało się pobrać stanu maszyny',
            } );
            getStatesData();
        },
        timeout: 1000,
    } );
}

function updateStates( states ) {
    $('#viceState').val( states.viceState );
    $('#pressState').val( states.pressState );
    $('#currentSlat').text( states.currentSlat );
    $('#slatsPerBoard').text( states.slatsPerBoard );
    $('#currentBoard').text( states.currentBoard );
    $('#boardsPerRow').text( states.boardsPerRow );
    $('#currentRow').text( states.currentRow );
    $('#rowsPerSet').text( states.rowsPerSet );
    $('#pressTempTop').text( states.pressTempTop.toPrecision( 3 ) );
    $('#pressTempDown').text( states.pressTempDown.toPrecision( 3 ) );
    $('#pressPressureTop').text( states.pressPressureTop );
    $('#pressPressureSide').text( states.pressPressureSide );

    if ( Date.now( ) - timer > freq )
        getStatesData( );
    else
        setTimeout( getStatesData, freq - Date.now( ) - timer )
}