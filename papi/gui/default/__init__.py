#!/usr/bin/python3
# -*- coding: latin-1 -*-

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

You should have received a copy of the GNU Lesser General Public License
along with PaPI.  If not, see <http://www.gnu.org/licenses/>.

Contributors
Sven Knuth
"""



import os
from PyQt5.QtGui import QIcon, QPixmap

def get32Icon(file):
    path = os.path.abspath('./papi/gui/default/images/32/' + file)
    return QIcon(path)

def get16Icon(file):
    path = os.path.abspath('./papi/gui/default/images/16/' + file)
    return QIcon(path)

def get32Pixmap(file):
    path = os.path.abspath('./papi/gui/default/images/32/' + file)
    return QPixmap(path)

def get16Pixmap(file):
    path = os.path.abspath('./papi/gui/default/images/16/' + file)
    return QPixmap(path)
