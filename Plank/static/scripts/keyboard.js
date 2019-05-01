/* VIRTUAL KEYBOARD DEMO - https://github.com/Mottie/Keyboard */
$( () => {
    // create a new language (love, awww) by copying the english language
    // file. we're doing this just for this demo, so we can add "<3" to the
    // combo regex
    $.keyboard.language.love = $.extend($.keyboard.language.en);

    $( 'input[type=number]').keyboard({
        // set this to ISO 639-1 language code to override language set by
        // the layout: http://en.wikipedia.org/wiki/List_of_ISO_639-1_codes
        // language defaults to ["en"] if not found
        language: ['love'],
        rtl: false,

        // *** choose layout & positioning ***
        // choose from 'qwerty', 'alpha',
        // 'international', 'dvorak', 'num' or
        // 'custom' (to use the customLayout below)
        layout: 'custom',
        customLayout: {
            'default': [
                '7 8 9',
                '4 5 6',
                '1 2 3',
                '{bksp} 0 {accept}'
            ]
        },
        // Used by jQuery UI position utility
        position: {
            // null = attach to input/textarea;
            // use $(sel) to attach elsewhere
            of: $(window),
            my: 'center top',
            at: 'center top',
            // used when "usePreview" is false
            at2: 'right bottom'
        },

        // allow jQuery position utility to reposition the keyboard on
        // window resize
        reposition: true,

        // true: preview added above keyboard;
        // false: original input/textarea used
        usePreview: false,

        // if true, the keyboard will always be visible
        alwaysOpen: false,

        // give the preview initial focus when the keyboard
        // becomes visible
        initialFocus: false,
        // Avoid focusing the input the keyboard is attached to
        noFocus: true,

        // if true, keyboard will remain open even if
        // the input loses focus.
        stayOpen: true,

        // Prevents the keyboard from closing when the user clicks or
        // presses outside the keyboard. The `autoAccept` option must
        // also be set to true when this option is true or changes are lost
        userClosed: true,

        // if true, keyboard will not close if you press escape.
        ignoreEsc: true,

        // *** change keyboard language & look ***
        display: {
            // check mark (accept)
            'a': '\u2714:Accept (Shift-Enter)',
            'accept': '<i class="material-icons">done</i>',
            'alt': 'AltGr:Alternate Graphemes',
            // Left arrow (same as &larr;)
            'b': '\u2190:Backspace',
            'bksp': '<i class="material-icons">backspace</i>',
            // big X, close/cancel
            'c': '\u2716:Cancel (Esc)',
            'cancel': '<i class="material-icons">cancel</i>',
            // clear num pad
            'clear': 'C:Clear',
            'combo': '\u00f6:Toggle Combo Keys',
            // num pad decimal '.' (US) & ',' (EU)
            'dec': '.:Decimal',
            // down, then left arrow - enter symbol
            'e': '\u21b5:Enter',
            'empty': '\u00a0', // &nbsp;
            'enter': 'Enter:Enter',
            // left arrow (move caret)
            'left': '\u2190',
            // caps lock
            'lock': '\u21ea Lock:Caps Lock',
            'next': 'Next \u21e8',
            'prev': '\u21e6 Prev',
            // right arrow (move caret)
            'right': '\u2192',
            // thick hollow up arrow
            's': '\u21e7:Shift',
            'shift': 'Shift:Shift',
            // +/- sign for num pad
            'sign': '\u00b1:Change Sign',
            'space': '\u00a0:Space',
            // right arrow to bar
            // \u21b9 is the true tab symbol
            't': '\u21e5:Tab',
            'tab': '\u21e5 Tab:Tab',
            // replaced by an image
            'toggle': ' ',

            // added to titles of keys
            // accept key status when acceptValid:true
            'valid': 'valid',
            'invalid': 'invalid',
            // combo key states
            'active': 'active',
            'disabled': 'disabled'

        },

        css: {
            // input & preview
            input: 'ui-widget-content ui-corner-all',
            // keyboard container
            container: 'ui-widget-content ui-widget ui-corner-all ui-helper-clearfix',
            // keyboard container extra class (same as container, but separate)
            popup: '',
            // default state
            buttonDefault: 'ui-state-default ui-corner-all btn wave-effect wave-light',
            // hovered button
            buttonHover: 'ui-state-hover',
            // Action keys (e.g. Accept, Cancel, Tab, etc);
            // this replaces "actionClass" option
            buttonAction: 'ui-state-active',
            // Active keys
            // (e.g. shift down, meta keyset active, combo keys active)
            buttonActive: 'ui-state-active',
            // used when disabling the decimal button {dec}
            // when a decimal exists in the input area
            buttonDisabled: 'ui-state-disabled',
            // {empty} button class name
            buttonEmpty: 'ui-keyboard-empty'
        },

        autoAccept: false,
        autoAcceptOnEsc: false,
        lockInput: false,
        restrictInput: false,
        restrictInclude: '',
        acceptValid: true,
        autoAcceptOnValid: false,
        // if acceptValid is true & the validate function returns
        // a false, this option will cancel a keyboard close only
        // after the accept button is pressed
        cancelClose: true,
        tabNavigation: false,
        enterNavigation: false,
        enterMod: 'altKey',
        stopAtEnd: true,
        appendLocally: false,
        appendTo: 'body',
        stickyShift: true,
        preventPaste: false,
        caretToEnd: false,
        scrollAdjustment: 10,
        maxLength: false,
        maxInsert: true,
        repeatDelay: 500,
        repeatRate: 20,
        resetDefault: false,
        openOn: 'focus',
        keyBinding: 'mousedown touchstart',

        // *** Methods ***
        // Callbacks - attach a function to any of these
        // callbacks as desired
        initialized: function (e, keyboard, el) {
        },
        beforeVisible: function (e, keyboard, el) {
        },
        visible: function (e, keyboard, el) {

        },
        beforeInsert: function (e, keyboard, el, textToAdd) {
            return textToAdd;
        },
        change: function (e, keyboard, el) {
        },
        beforeClose: function (e, keyboard, el, accepted) {
        },
        accepted: function (e, keyboard, el) {
        },
        canceled: function (e, keyboard, el) {
        },
        restricted: function (e, keyboard, el) {
        },
        hidden: function (e, keyboard, el) {
        },
    });

});