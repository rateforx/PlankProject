import sys
import PyQt5.uic as uic
from PyQt5 import QtWidgets
from distutils.dep_util import newer
from Trashed.ui import Ui_Dialog


class GUI:

    def __init__( self ):
        self.app = QtWidgets.QApplication( sys.argv )
        self.window = QtWidgets.QDialog( )
        self.ui = Ui_Dialog( )
        self.ui.setupUi( self.window )
        # self.app.exec_( )

    def compileUi( self, ui_file ):
        # py_file = os.path.splitext( ui_file )[ 0 ] + "_ui.py"
        py_file = '__init__.py'
        if not newer( ui_file, py_file ):
            return
        fp = open( py_file, "w" )
        uic.compileUi( ui_file, fp, from_imports = True )
        fp.close( )