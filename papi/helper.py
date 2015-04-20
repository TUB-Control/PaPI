#!/usr/bin/python3
# -*- coding: utf-8 -*-

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

Contributors:
<Stefan Ruppin
"""

__author__ = 'knuths'

from PyQt4.QtGui import QColor
import re


def get_color_by_string(color_string, inverse = False):
    color_re = re.compile(r'\d+')
    rgb = color_re.findall(color_string)
    color = None
    if inverse:
        color = QColor.fromRgb(255 - int(rgb[0]), 255 - int(rgb[1]), 255 - int(rgb[2]))
    if not inverse:
        color = QColor.fromRgb(int(rgb[0]), int(rgb[1]),int(rgb[2]))
    return color
