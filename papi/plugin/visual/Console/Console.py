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

You should have received a copy of the GNU Lesser General Public License
along with PaPI.  If not, see <http://www.gnu.org/licenses/>.

Contributors:
<Stefan Ruppin
"""

__author__ = 'Stefan'


from PyQt5 import QtCore

from PyQt5.QtWidgets import QWidget
from PyQt5 import QtWidgets
from PyQt5 import QtGui

from papi.plugin.base_classes.vip_base import vip_base
from papi.data.DParameter import DParameter

from papi.plugin.visual.Console.CmdInput import CmdInput


class Console(vip_base):


    def initiate_layer_0(self, config=None):

        # ---------------------------
        # Read configuration
        # ---------------------------


        # --------------------------------
        # Create Widget
        # --------------------------------
        self.ConsoleW = PaPIConsoleWidget(plugin=self)


        # This call is important, because the background structure needs to know the used widget!
        # In the background the qmidiwindow will becreated and the widget will be added
        self.set_widget_for_internal_usage( self.ConsoleW )


        self.ConsoleW.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.ConsoleW.customContextMenuRequested.connect(self.show_context_menu)

        return True

    def show_context_menu(self, pos):
        gloPos = self.ConsoleW.mapToGlobal(pos)
        self.cmenu = self.create_control_context_menu()
        self.cmenu.exec_(gloPos)

    def pause(self):
        # will be called, when plugin gets paused
        # can be used to get plugin in a defined state before pause
        # e.a.
        pass

    def resume(self):
        # will be called when plugin gets resumed
        # can be used to wake up the plugin from defined pause state
        # e.a. reopen communication ports, files etc.
        pass

    def execute(self, Data=None, block_name = None, plugin_uname = None):
        # Do main work here!
        # If this plugin is an IOP plugin, then there will be no Data parameter because it wont get data
        # If this plugin is a DPP, then it will get Data with data

        # param: Data is a Data hash and block_name is the block_name of Data origin
        # Data is a hash, so use ist like:  Data['t'] = [t1, t2, ...] where 't' is a signal_name
        # hash signal_name: value

        # Data could have multiple types stored in it e.a. Data['d1'] = int, Data['d2'] = []

        pass

    def set_parameter(self, name, value):
        # attetion: value is a string and need to be processed !
        # if name == 'irgendeinParameter':
        #   do that .... with value
        pass

    def quit(self):
        # do something before plugin will close, e.a. close connections ...
        pass


    def get_plugin_configuration(self):
        #
        # Implement a own part of the config
        # config is a hash of hass object
        # config_parameter_name : {}
        # config[config_parameter_name]['value']  NEEDS TO BE IMPLEMENTED
        # configs can be marked as advanced for create dialog
        # http://utilitymill.com/utility/Regex_For_Range

        config = {
            'name': {
                'value': 'Console',
                'tooltip': 'Used for window title'
            }
        }

        return config

    def plugin_meta_updated(self):
        """
        Whenever the meta information is updated this function is called (if implemented).

        :return:
        """

        #dplugin_info = self.dplugin_info
        pass





class PaPIConsoleWidget(QWidget):
    def __init__(self, parent = None, plugin = None):
        QWidget.__init__(self, parent)

        self.plugin = plugin

        self.ui = Ui_Form()
        self.ui.setupUi(self)


        self.ui.input.sigExecuteCmd.connect(self.runCmd)

        self.ui.output.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.ui.output.customContextMenuRequested.connect(self.showContextMenu)

        self.ui.output.setStyleSheet("background-color: black")
        self.ui.input.setStyleSheet("background-color: black; color: green;")
        self.ui.input.setContentsMargins(0,0,0,0)
        self.ui.output.setContentsMargins(0,0,0,0)

        font = QtGui.QFont("Monospace");
        font.setStyleHint(QtGui.QFont.TypeWriter);

        self.ui.output.setFont(font)

        self.ui.input.setFont(font)

        scrollbar = self.ui.output.verticalScrollBar()
        scrollbar.setStyleSheet("background-color: green")

        self.setStyleSheet("background-color: black")


        self.write("<div style='background-color: #000'>",html=True)

    def showContextMenu(self,pos):
        plaintextmenu = self.ui.output.createStandardContextMenu()
        papimenu = self.plugin.create_control_context_menu()

        plaintextmenu.setStyleSheet("background-color: black; color: green")
        plaintextmenu.setTitle('Actions')
        papimenu.setTitle('Control')

        menu = QtGui.QMenu()
        menu.addMenu(papimenu)
        menu.addMenu(plaintextmenu)

        menu.setStyleSheet("background-color: black; color: green")
        papimenu.setStyleSheet("background-color: black; color: green")


        gloPos = self.mapToGlobal(pos)

        menu.exec_(gloPos)

    def runCmd(self, cmd):
        self.write("<font color='green'>%s</font><br>\n"%cmd, html=True)
        sb = self.ui.output.verticalScrollBar()
        sb.setValue(sb.maximum())

    def write(self, strn, html=False):
        self.ui.output.moveCursor(QtGui.QTextCursor.End)
        if html:
            self.ui.output.textCursor().insertHtml(strn)
        else:
            if self.inCmd:
                self.inCmd = False
                self.ui.output.textCursor().insertHtml("</div><br><div style='font-weight: normal; #background-color: #FFF;'>")
                #self.stdout.write("</div><br><div style='font-weight: normal; background-color: #FFF;'>")
            self.ui.output.insertPlainText(strn)



class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(710, 497)
        self.gridLayout = QtWidgets.QGridLayout(Form)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setSpacing(0)
        self.gridLayout.setObjectName("gridLayout")
        self.splitter = QtWidgets.QSplitter(Form)
        self.splitter.setOrientation(QtCore.Qt.Vertical)
        self.splitter.setObjectName("splitter")
        self.layoutWidget = QtWidgets.QWidget(self.splitter)
        self.layoutWidget.setObjectName("layoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.layoutWidget)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.output = QtWidgets.QPlainTextEdit(self.layoutWidget)
        font = QtGui.QFont()
        font.setFamily("Monospace")
        self.output.setFont(font)
        self.output.setReadOnly(True)
        self.output.setObjectName("output")
        self.verticalLayout.addWidget(self.output)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.input = CmdInput(self.layoutWidget)
        self.input.setObjectName("input")
        self.horizontalLayout.addWidget(self.input)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.gridLayout.addWidget(self.splitter, 0, 0, 1, 1)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Console"))

