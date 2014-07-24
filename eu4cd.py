import sys

from eu4cd.main import MainWindow
from PyQt4.QtGui import (
    QApplication,
    )

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.resize(800, 600)
    window.show()
    window.raise_()
    sys.exit(app.exec_())
    
if __name__ == '__main__':
    main()
