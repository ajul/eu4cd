import sys

from eu4cd.main import MainWindow
from PyQt5.QtWidgets import (
    QApplication,
    )

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.resize(800, 600)
    window.show()
    sys.exit(app.exec_())
    
if __name__ == '__main__':
    main()
