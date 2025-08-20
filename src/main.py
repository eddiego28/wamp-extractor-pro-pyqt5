
# -*- coding: utf-8 -*-
import sys
from PyQt5 import QtWidgets
from .app import Controller

def main():
    app = QtWidgets.QApplication(sys.argv)
    c = Controller(app)
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
