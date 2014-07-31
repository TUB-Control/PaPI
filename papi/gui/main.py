#!/usr/bin/python3
# -*- coding: latin-1 -*-

"""
Copyright (C) 2014 Technische Universität Berlin,
Fakultät IV - Elektrotechnik und Informatik,
Fachgebiet Regelungssysteme,
Einsteinufer 17, D-10587 Berlin, Germany

This file is part of PaPI.

PaPI is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

PaPI is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with PaPI.  If not, see <http://www.gnu.org/licenses/>.

Contributors
Sven Knuth
"""

__author__ = 'knuths'

import sys
import time

from PySide.QtGui import QMainWindow, QApplication

import pyqtgraph as pg
from pyqtgraph import QtGui, QtCore

# Enable antialiasing for prettier plots
pg.setConfigOptions(antialias=True)

from papi.ui.gui.main import Ui_MainGUI
from papi.gui.manager import Manager

class GUI(QMainWindow, Ui_MainGUI):

    def __init__(self, parent=None):
        super(GUI, self).__init__(parent)
        self.setupUi(self)

        self.create_actions()

        self.manager_visual = Manager('visual')
        self.manager_io = Manager('io')
        self.manager_parameter = Manager('parameter')

        self.setWindowTitle('PaPI')

    def dbg(self):
        print("Action")

    def create_actions(self):
        self.actionM_License.triggered.connect(self.menu_license)
        self.actionM_Quit.triggered.connect(self.menu_quit)

        self.actionAP_Visual.triggered.connect(self.ap_visual)
        self.actionAP_IO.triggered.connect(self.ap_io)
        self.actionAP_Parameter.triggered.connect(self.ap_parameter)

        self.actionRP_IO.triggered.connect(self.rp_io)
        self.actionRP_Visual.triggered.connect(self.rp_visual)

    def menu_license(self):
        pass

    def menu_quit(self):
        self.close()
        pass

    def ap_visual(self):
        self.manager_visual.show()

        pass

    def ap_io(self):
        self.manager_io.show()
        pass

    def ap_parameter(self):
        self.manager_parameter.show()
        pass

    def rp_visual(self):
        pass

    def rp_io(self):
        pass

    def closeEvent(self, *args, **kwargs):
        self.manager_visual.close()
        self.manager_parameter.close()
        self.manager_io.close()
        self.close()

def startGUI( CoreQueue, GUIQueue, timeArr, valueArr, lock):
    app = QApplication(sys.argv)
#    mw = QtGui.QMainWindow
    gui = GUI()
    gui.show()
    app.exec_()

if __name__ == '__main__':
    app = QApplication(sys.argv)
#    mw = QtGui.QMainWindow
    frame = GUI()
    frame.show()
    app.exec_()
