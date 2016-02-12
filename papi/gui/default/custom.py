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

You should have received a copy of the GNU General Public License
along with PaPI.  If not, see <http://www.gnu.org/licenses/>.

Contributors
Sven Knuth
"""

from PyQt5.QtWidgets import QLineEdit, QFileDialog, QColorDialog, QPushButton
from PyQt5 import QtWidgets

import os
import papi.helper as ph
import papi.constants as pc

class FileLineEdit(QLineEdit):
    """
    A QFileDialog is used to determine the content of this QLineEdit.
    Used in the 'CreatePluginDialog' for a config element if the config elements contains the type : 'file'

    """
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
    """
    A QColorDialog is used to determine the content of this QLineEdit.
    Used in the 'CreatePluginDialog' for a config element if the config elements contains the type : 'color'

    """

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


class PaPIConfigSaveDialog(QtWidgets.QFileDialog):
    """
    The default QFileDialog for save operations was enhanced by additional options.
    These options are hidden in the QFileDialog till the 'More Details'-Button was clicked.

    """

    def __init__(self, parent, gui_api):
        super(PaPIConfigSaveDialog, self).__init__(parent)
        self.setOption(QtWidgets.QFileDialog.DontUseNativeDialog)

        inital_hidden = True

        self.gui_api = gui_api

        self.file_dialog = QFileDialog()

        self.setFileMode(QFileDialog.AnyFile)
        self.setNameFilters( [ self.tr("PaPI-Cfg (*.xml)"), self.tr("PaPI-Cfg (*.json)") ])
        self.setDirectory(os.path.abspath(pc.CONFIG_DEFAULT_DIRECTORY))
        self.setWindowTitle("Save Configuration")
        self.setAcceptMode(QFileDialog.AcceptSave)


        button = QPushButton('More details ...')
        button.clicked.connect(self.button_clicked)

        glayout = self.layout()


        self.detailed_widget = QtWidgets.QWidget()


        # ------------------
        # Layout for table
        # ------------------


        self.detailed_layout = QtWidgets.QVBoxLayout()
        self.pluginTable = QtWidgets.QTableWidget()
#        self.pluginTable.setHeaderLabels(['Plugin', 'Create', 'Subscriptions'])
        self.pluginTable.setHidden(inital_hidden)

        self.detailed_layout.addWidget(self.pluginTable)


        self.pluginTable.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)


        # --------------------
        # Buttons for comfort
        # --------------------

        self.buttons_widget = QtWidgets.QWidget()
        self.buttons_widget.setHidden(inital_hidden)

        select_all_plugins = QPushButton('All plugins')
        select_all_subs = QPushButton('All subscriptions')

        unselect_all_plugins = QPushButton('No plugins')
        unselect_all_subs = QPushButton('No subscriptions')

        select_for_simulink_ortd = QPushButton('Select for Simulink/ORTD')

        select_all_plugins.clicked.connect(lambda  ignore, p = 1 : self.select_items(p))
        select_all_subs.clicked.connect(lambda  ignore, p = 2 : self.select_items(p))

        unselect_all_plugins.clicked.connect(lambda  ignore, p = -1 : self.select_items(p))
        unselect_all_subs.clicked.connect(lambda  ignore, p = -2 : self.select_items(p))

        select_for_simulink_ortd.clicked.connect(lambda  ignore : self.select_simulink_ortd())


        self.button_vlayout = QtWidgets.QVBoxLayout(self.buttons_widget)

        self.button_vlayout.addWidget(select_all_plugins)
        self.button_vlayout.addWidget(select_all_subs)
        self.button_vlayout.addWidget(unselect_all_plugins)
        self.button_vlayout.addWidget(unselect_all_subs)
        self.button_vlayout.addWidget(select_for_simulink_ortd)

#        self.vlayout.addWidget(self.buttons_widget)

        glayout.addWidget(button, 5,0)

        glayout.addWidget(self.buttons_widget, 6,0,1,1)
        glayout.addLayout(self.detailed_layout, 6, 1, 1, 3)

    def button_clicked(self):


        self.pluginTable.setHidden(not self.pluginTable.isHidden())

        self.buttons_widget.setHidden(not self.buttons_widget.isHidden())

    def select_items(self, flag):
        for r in range(self.pluginTable.rowCount()-1):

            if flag in [1, 2]:
                self.pluginTable.cellWidget(r, flag).setChecked(True)

            if flag in [-1, -2]:
                self.pluginTable.cellWidget(r, abs(flag)).setChecked(False)

    def select_simulink_ortd(self):
        for r in range(self.pluginTable.rowCount()-1):
            label = self.pluginTable.cellWidget(r, 0)
            dplugin = self.gui_api.gui_data.get_dplugin_by_uname(label.text())

            self.pluginTable.cellWidget(r, 1).setChecked(True)
            self.pluginTable.cellWidget(r, 2).setChecked(True)

            if dplugin.plugin_identifier in ['PaPIController']:
                self.pluginTable.cellWidget(r, 1).setChecked(False)
                self.pluginTable.cellWidget(r, 2).setChecked(False)

            if dplugin.plugin_identifier in ['UDP_Plugin']:
                self.pluginTable.cellWidget(r, 1).setChecked(False)


    def fill_with(self):

        dplugins = self.gui_api.gui_data.get_all_plugins()

        row = 0

        self.pluginTable.setColumnCount(4)

        self.pluginTable.setHorizontalHeaderLabels(["Plugin" , "C", 'S',''])

        vertical_header = []

        for dplugin_id in dplugins:
            dplugin = dplugins[dplugin_id]

#            vertical_header.append(str(dplugin.id))
            vertical_header.append('')

            self.pluginTable.setRowCount(row + 1)
#            qlabel = QtWidgets.QLabel(dplugin.uname)

            self.pluginTable.setCellWidget(row, 0, QtWidgets.QLabel(dplugin.uname))

            check_plugin = QtWidgets.QCheckBox();
            check_plugin.setChecked(True)

            check_subscription = QtWidgets.QCheckBox();
            check_subscription.setChecked(True)

            self.pluginTable.setCellWidget(row, 1, check_plugin)
            self.pluginTable.setCellWidget(row, 2, check_subscription)
            row += 1


        vertical_header.append('')
        self.pluginTable.setRowCount(row + 1)

        self.pluginTable.setVerticalHeaderLabels(vertical_header)

        self.pluginTable.resizeColumnToContents(1)
        self.pluginTable.resizeColumnToContents(2)

        self.pluginTable.horizontalHeader().setStretchLastSection(True)
        self.pluginTable.verticalHeader().setStretchLastSection(True)

    def get_create_lists(self):

        plugin_list = []
        subscription_list = []

        for r in range(self.pluginTable.rowCount()-1):
            qlabel = self.pluginTable.cellWidget(r, 0)

            if self.pluginTable.cellWidget(r, 1).isChecked():
                plugin_list.append(qlabel.text())

            if self.pluginTable.cellWidget(r, 2).isChecked():
                subscription_list.append(qlabel.text())

        return plugin_list, subscription_list
