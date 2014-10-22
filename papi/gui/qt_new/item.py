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

from PySide.QtGui import QStandardItem, QStandardItemModel
# from PySide.QtCore import QStandardItemModel



from PySide.QtCore import *
from PySide.QtGui import *

class PaPITreeItem(QStandardItem):
    def __init__(self, object,  name):
        super(PaPITreeItem, self).__init__(name)
        self.object = object
        self.setEditable(False)
        self.name = name

    def data(self, role):
        '''
        For Qt.Role see 'http://qt-project.org/doc/qt-4.8/qt.html#ItemDataRole-enum'
        :param role:
        :return:
        '''

        if role == Qt.ToolTipRole:
            return "Plugin: " + self.name

        if role == Qt.DisplayRole:
            return self.name

        if role == Qt.DecorationRole:
            return QColor(255, 0, 0, 127)
            # path = self.object.path+'/box.png'
            # print(path)
            # image = QPixmap()
            # print(image.load(path) )
            # return image

        if role == Qt.UserRole:
            return self.object

        return None

    def mousePressEvent(self, event):
        print('mouse event')

class RootItem(QStandardItem):
    def __init__(self, name):
        super(RootItem, self).__init__(name)
        self.setEditable(False)

class PaPItreeModel(QStandardItemModel):
    def __init__(self, parent=None):
        super(PaPItreeModel, self).__init__(parent)

class PaPITreeView(QTreeView):
    def __init__(self, parent=None):
        super(PaPITreeView, self).__init__(parent)

    def mousePressEvent(self, *args, **kwargs):
        pass
