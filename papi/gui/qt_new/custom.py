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

__author__ = 'knuths'

from PyQt5.QtGui        import QColor
from PyQt5.QtWidgets    import QLineEdit, QFileDialog, QColorDialog, QPushButton

#from PyQt5.QtWidgets import QLineEdit, QFileDialog, QColorDialog, QPushButton, QColor
import os, re
import papi.helper as ph

class FileLineEdit(QLineEdit):
    def __init__(self):
        super(FileLineEdit, self).__init__()

        self.file_type = "File (*)"

    def set_file_type(self, type):
        self.file_type = type

    def mousePressEvent(self, event):

        fileNames = ''

        path, file = os.path.split(self.text())

        dialog = QFileDialog(self)
        dialog.setFileMode(QFileDialog.AnyFile)
        dialog.setNameFilter( self.tr(self.file_type))
        dialog.setDirectory(path)

        if dialog.exec_():
            fileNames = dialog.selectedFiles()

        if len(fileNames):
            if fileNames[0] != '':
                self.setText(fileNames[0])


class ColorLineEdit(QPushButton):
    def __init__(self):
        super(ColorLineEdit, self).__init__()
        self.clicked.connect(self.open_color_picker)
        self.color_picker = QColorDialog()

    def set_default_color(self, color_string):

        #self.setStyleSheet("filter: invert(100%)")
        self.setText(color_string)


        color_inverse = ph.get_color_by_string(color_string, inverse=True)
        color_string_inverse = self.__get_string_by_color(color_inverse)

        self.setStyleSheet("\
                QPushButton {   \
                    border : 1px outset black;  \
                    background-color: rgb" + color_string + " ;color: rgb" + color_string_inverse + ";    \
                }   \
                QPushButton:checked{\
                    background-color: rgb" + color_string + "; \
                    border-style: outset;  \
                } \
                QPushButton:hover{  \
                    background-color: rgb " + color_string + "; \
                    border-style: solid;  \
                }  \
                ");

    def open_color_picker(self):
        color = self.color_picker.getColor()

        if color.isValid():

            color_string = self.__get_string_by_color(color)
            self.set_default_color(color_string)

        pass

    def __get_string_by_color(self, color):

        color_string = '(' + str(color.red()) + ',' + str(color.green()) + ',' + str(color.blue()) + ')'

        return color_string
