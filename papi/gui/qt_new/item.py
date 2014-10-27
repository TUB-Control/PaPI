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
from papi.data.DPlugin import *
# ------------------------------------
# Item Object
# ------------------------------------


class PaPITreeItem(QStandardItem):
    def __init__(self, object,  name):
        super(PaPITreeItem, self).__init__(name)
        self.object = object
        # self.setEditable(False)
        # self.setSelectable(False)
        self.name = name
        self.tool_tip = "Plugin: " + self.name

    def data(self, role):
        '''
        For Qt.Role see 'http://qt-project.org/doc/qt-4.8/qt.html#ItemDataRole-enum'
        :param role:
        :return:
        '''

        if role == Qt.ToolTipRole:
            return self.tool_tip

        if role == Qt.DisplayRole:
            return self.name

        if role == Qt.DecorationRole:
            return self.get_decoration()

        if role == Qt.UserRole:
            return self.object

        return None

    def get_decoration(self):
        return None


class PaPIRootItem(QStandardItem):
    def __init__(self, name):
        super(PaPIRootItem, self).__init__(name)
        self.setEditable(False)
        self.setSelectable(False)

# ------------------------------------
# Model Objects
# ------------------------------------


class PaPItreeModel(QStandardItemModel):
    def __init__(self, parent=None):
        super(PaPItreeModel, self).__init__(parent)

    # def setData(self, index, value, role):
    #     pass

    # def data(self, index, role):
    #     row = index.row()
    #     col = index.column()
    #
    #     pass

# ------------------------------------
# Item Custom
# ------------------------------------


class PluginTreeItem(PaPITreeItem):
    def __init__(self,  plugin):
        super(PluginTreeItem, self).__init__(plugin, plugin.name)
        self.plugin = plugin
        self.setEditable(False)


    def get_decoration(self):
        l = len(self.object.name)
        path = self.object.path[:-l]
        path += 'box.png'
        px = QPixmap(path)
        return px


class DPluginTreeItem(PaPITreeItem):
    def __init__(self,  dplugin: DPlugin):
        super(DPluginTreeItem, self).__init__(dplugin, dplugin.uname)
        self.dplugin = dplugin
        self.name = dplugin.uname

#        print(self.isEditable())

        # super(PaPITreeItem, self).setEditable(False)
        self.setEditable(True)
        # self.setEditable(False)

#        print(self.isEditable())

        print(self.flags())
        self.setFlags(self.flags() & ~Qt.ItemIsEditable)
        print(self.flags())
        self.setFlags(self.flags() & ~Qt.ItemIsEditable)

    def get_decoration(self):
        return None


class DParameterTreeItem(PaPITreeItem):
    def __init__(self,  dparameter : DParameter):
        super(DParameterTreeItem, self).__init__(dparameter, dparameter.name)
        self.dparameter = dparameter
        self.setEditable(False)

    def get_decoration(self):
        return None


class DBlockTreeItem(PaPITreeItem):
    def __init__(self,  dblock: DBlock):
        super(DBlockTreeItem, self).__init__(dblock, dblock.name)
        self.setSelectable(False)

    def get_decoration(self):
        return None

# ------------------------------------
# Model Custom
# ------------------------------------


class PluginTreeModel(PaPItreeModel):
    def __init__(self, parent=None):
        super(PluginTreeModel, self).__init__(parent)


class DPluginTreeModel(PaPItreeModel):
    def __init__(self, parent=None):
        super(DPluginTreeModel, self).__init__(parent)


class DParameterTreeModel(PaPItreeModel):
    def __init__(self, parent=None):
        super(DParameterTreeModel, self).__init__(parent)


class DBlockTreeModel(PaPItreeModel):
    def __init__(self, parent=None):
        super(DBlockTreeModel, self).__init__(parent)
