#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Copyright (C) 2014 Technische Universität Berlin,
Fakultät IV - Elektrotechnik und Informatik,
Fachgebiet Regelungssysteme,
Einsteinufer 17, D-10587 Berlin, Germany

This file is part of PaPI.

PaPI is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

PaPI is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with PaPI.  If not, see <http://www.gnu.org/licenses/>.

Contributors:
Stefan Ruppin
"""

from PyQt5.QtWidgets import QMdiSubWindow
from PyQt5.QtCore import Qt

class PaPISubWindow(QMdiSubWindow):
    def __init__(self, parent = None):
        QMdiSubWindow.__init__(self,parent)
        self._interaction_possible = True
        self._default_window_flag = self.windowFlags()

    def mouseMoveEvent(self, QMouseEvent):
        if self._interaction_possible:
            QMdiSubWindow.mouseMoveEvent(self,QMouseEvent)
        else:
            pass

    def disableInteraction(self):
        self._interaction_possible = False
        self.setWindowFlags(Qt.CustomizeWindowHint | Qt.WindowTitleHint)
        self.setFocus()
        self.show()

    def enableInteraction(self):
        self._interaction_possible = True
        self.setWindowFlags(Qt.WindowMaximizeButtonHint | Qt.WindowTitleHint | Qt.WindowMinimizeButtonHint)
        self.setFocus()
        self.show()

    def isInteractionAllowed(self):
        return self._interaction_possible
