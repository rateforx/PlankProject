import sys
from PyQt5.QtWidgets import QApplication
import PyQt5.uic as uic

if __name__ == "__main__":
    app = QApplication( sys.argv )
    window = uic.loadUi( 'ui/main.ui' )
    window.show( )
    sys.exit( app.exec_( ) )
