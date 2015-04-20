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
Sven Knuth
"""

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from papi.ui.gui.qt_new.CreateRecording import Ui_CreateRecording
from PyQt4.QtGui import QMainWindow

from papi.gui.qt_new.item import CustomFieldModel, CustomFieldItem, StructTreeModel, StructTreeNode, StructRootNode

class CreateRecordingConfig(QMainWindow, Ui_CreateRecording):
    def __init__(self, gui_api):
        super(CreateRecordingConfig, self).__init__()
        self.setupUi(self)
        self.gui_api = gui_api

        # -----------------------------------------
        # Initiate first tab: Fields
        # -----------------------------------------

        self.addFieldButton.clicked.connect(self.add_button_triggered)
        self.previewButton.clicked.connect(self.preview_button_triggered)

        self.field_model = CustomFieldModel()
        self.field_model.dataChanged.connect(self.custom_field_edited)
        self.field_model.setHorizontalHeaderLabels(['Field', 'Type', 'Remove'])

        self.customFieldTable.setModel(self.field_model)

        self.struct_model = StructTreeModel()
        self.structureView.setModel(self.struct_model)
        self.struct_model.setHorizontalHeaderLabels(['Name', 'Size'])
        self.root_struct = StructRootNode('Data')

        self.struct_model.appendRow(self.root_struct)

        # -----------------------------------------
        # Initiate second tab: Subscription
        # -----------------------------------------

        self.previewButton_sub.clicked.connect(self.preview_sub_button_triggered)

        self.struct_model_sub = StructTreeModel()
        self.struct_model_sub.setHorizontalHeaderLabels(['Name', 'Size'])
        self.structureView_sub.setModel(self.struct_model_sub)
        self.root_struct_sub = StructRootNode('Data')

        self.struct_model_sub.appendRow(self.root_struct_sub)


    def showEvent(self, *args, **kwargs):

        pass

    def add_button_triggered(self):
        custom_field_item = CustomFieldItem(CustomField())

        self.field_model.appendRow(custom_field_item)

    def preview_button_triggered(self):

        self.struct_model.clear()
        self.struct_model.setHorizontalHeaderLabels(['Name', 'Size'])

        self.root_struct = StructRootNode('Data')
        self.struct_model.appendRow(self.root_struct)

        for i in range(self.field_model.rowCount()):
            field = self.field_model.item(i).object

            self.root_struct.appendRow(field)

        self.structureView.expandAll()

    def preview_sub_button_triggered(self):

        self.struct_model_sub.clear()
        self.struct_model_sub.setHorizontalHeaderLabels(['Name', 'Size'])

        self.root_struct_sub = StructRootNode('Data')
        self.struct_model_sub.appendRow(self.root_struct_sub)

        for i in range(self.field_model.rowCount()):
            field = self.field_model.item(i).object

            self.root_struct_sub.appendRow(field)

        self.structureView_sub.expandAll()

    def custom_field_edited(self, index, none):
        print('Edited !!')


class CustomField():
    def __init__(self):
        self.desc = '1::2::3'
        self.size = '3x1'