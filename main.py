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

__author__ = 'control'

import sys
from papi.core import Core
from papi.gui.qt_new.main import startGUI as new_startGui
from papi.gui.qt_new.main import GUI
from PySide.QtGui    import QMainWindow, QApplication
import platform

def main():
    print(platform.system())
    # if platform.system() == 'Linux':
    #     core = Core(new_startGui,is_parent=True, use_gui=True)
    #     core.run()
    #     return
    # if platform.system() == 'Windows':
    #     print('Windows port is NOT ready')
    #     return
    # if platform.system() == 'Mac OS X':
    app = QApplication(sys.argv)
    gui = GUI(None,None,1,None,is_parent=True)
    gui.run()
    gui.show()
    app.exec_()




if __name__ == '__main__':
    sys.exit(main())
