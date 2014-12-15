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

from PySide.QtGui import QApplication

from papi.gui.qt_dev.gui_main import GUI
from papi.data.DGui import DGui
from papi.data.DCore import DBlock


def get_gui_data():
    """

    :return:
    :rtype DGui:
    """
    dgui = DGui()
    #Create dplugins
    d_pl_1 = dgui.add_plugin(None, 1, None, None, None, dgui.create_id())
    d_pl_2 = dgui.add_plugin(None, 1, None, None, None, dgui.create_id())
    d_pl_3 = dgui.add_plugin(None, 1, None, None, None, dgui.create_id())

    #Create dblocks
    d_bl_1 = DBlock(None, 0, 0, 'Block_1')
    d_bl_2 = DBlock(None, 0, 0, 'Block_2')
    d_bl_3 = DBlock(None, 0, 0, 'Block_3')

    #assign dblocks to DPlugin d_pl_1
    d_pl_1.add_dblock(d_bl_1)
    d_pl_1.add_dblock(d_bl_2)
    d_pl_1.add_dblock(d_bl_3)
    return dgui

if __name__ == '__main__':
    app = QApplication(sys.argv)
#    mw = QtGui.QMainWindow
    frame = GUI(None,None,None)
    frame.set_dgui_data(get_gui_data())
    frame.show()
    app.exec_()