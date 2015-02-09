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
Sven Knuth, Stefan Ruppin
"""

__author__ = 'knuths'

import sys
import os
import traceback
import cProfile
import re
import threading

from PySide.QtGui               import QMainWindow, QApplication, QFileDialog, QDesktopServices
from PySide.QtGui               import QIcon
from PySide.QtCore              import QSize, Qt, QUrl

import papi.pyqtgraph as pg
from papi.pyqtgraph import QtCore, QtGui

from papi.ui.gui.qt_new.main           import Ui_QtNewMain
from papi.data.DGui             import DGui
from papi.ConsoleLog            import ConsoleLog

from papi.constants import GUI_PAPI_WINDOW_TITLE, GUI_WOKRING_INTERVAL, GUI_PROCESS_CONSOLE_IDENTIFIER, \
    GUI_PROCESS_CONSOLE_LOG_LEVEL, GUI_START_CONSOLE_MESSAGE, GUI_WAIT_TILL_RELOAD, GUI_DEFAULT_HEIGHT, GUI_DEFAULT_WIDTH, \
    PLUGIN_STATE_PAUSE, PLUGIN_STATE_STOPPED, PAPI_ABOUT_TEXT, PAPI_ABOUT_TITLE, PAPI_DEFAULT_BG_PATH, PAPI_LAST_CFG_PATH

from papi.constants import CONFIG_DEFAULT_FILE, PLUGIN_VIP_IDENTIFIER, PLUGIN_PCP_IDENTIFIER, CONFIG_DEFAULT_DIRECTORY

from papi.gui.gui_api import Gui_api
from papi.gui.gui_event_processing import GuiEventProcessing

from papi.gui.qt_new.create_plugin_menu import CreatePluginMenu
from papi.gui.qt_new.overview_menu import OverviewPluginMenu


# Disable antialiasing for prettier plots
pg.setConfigOptions(antialias=False)


class GUI(QMainWindow, Ui_QtNewMain):
    """
    Used to create the qt based PaPI gui.

    """
    def __init__(self, core_queue, gui_queue,gui_id, gui_data = None, parent=None):
        """
        Init function

        :param core_queue: Queue used to send papi events to Core
        :param gui_queue: GUI queue which contains papi events for the gui
        :param gui_id: Unique ID for this gui
        :param gui_data: Contains all data for the current session
        :param parent: parent element
        :return:
        """
        super(GUI, self).__init__(parent)
        self.setupUi(self)

        if gui_data is None:
            self.gui_data = DGui()
        else:
            self.gui_data = gui_data

        self.gui_api = Gui_api(self.gui_data, core_queue, gui_id)

        self.gui_event_processing = GuiEventProcessing(self.gui_data, core_queue, gui_id, gui_queue)

        self.gui_event_processing.added_dplugin.connect(self.add_dplugin)
        self.gui_event_processing.removed_dplugin.connect(self.remove_dplugin)
        self.gui_event_processing.dgui_changed.connect(self.changed_dgui)
        self.gui_event_processing.plugin_died.connect(self.plugin_died)

        self.gui_api.error_occured.connect(self.error_occured)

        self.gui_api.resize_gui.connect(self.resize_gui_window)

        self.setWindowTitle(GUI_PAPI_WINDOW_TITLE)


        self.gui_api.set_bg_gui.connect(self.update_background)

        # set GUI size
        size = self.size()
        self.gui_api.gui_size_height    = size.height()
        self.gui_api.gui_size_width     = size.width()

        self.original_resize_function = self.resizeEvent
        self.resizeEvent = self.user_window_resize

        self.setGeometry(self.geometry().x(),self.geometry().y(),GUI_DEFAULT_WIDTH,GUI_DEFAULT_HEIGHT)

        self.core_queue = core_queue
        self.gui_queue = gui_queue

        self.gui_id = gui_id

        self.count = 0

        self.log = ConsoleLog(GUI_PROCESS_CONSOLE_LOG_LEVEL, GUI_PROCESS_CONSOLE_IDENTIFIER)

        self.log.printText(1,GUI_START_CONSOLE_MESSAGE + ' .. Process id: '+str(os.getpid()))

        self.last_config = PAPI_LAST_CFG_PATH

        self.update_background(PAPI_DEFAULT_BG_PATH)

        self.in_run_mode = False

        # -------------------------------------
        # Create placeholder
        # -------------------------------------
        self.overview_menu = None
        self.create_plugin_menu = None
        # -------------------------------------
        # Create callback functions for buttons
        # -------------------------------------
        self.loadButton.clicked.connect(self.load_triggered)
        self.saveButton.clicked.connect(self.save_triggered)

        # -------------------------------------
        # Create actions
        # -------------------------------------
        self.actionLoad.triggered.connect(self.load_triggered)
        self.actionSave.triggered.connect(self.save_triggered)

        self.actionOverview.triggered.connect(self.show_overview_menu)
        self.actionCreate.triggered.connect(self.show_create_plugin_menu)

        self.actionResetPaPI.triggered.connect(self.reset_papi)
        self.actionReloadConfig.triggered.connect(self.reload_config)

        self.actionRunMode.triggered.connect(self.toggle_run_mode)

        self.actionSetBackground.triggered.connect(self.set_background_for_gui)

        self.actionPaPI_Wiki.triggered.connect(self.papi_wiki_triggerd)

        self.actionPaPI_Doc.triggered.connect(self.papi_doc_triggerd)
        self.actionAbout.triggered.connect(self.papi_about_triggerd)
        self.actionAbout_Qt.triggered.connect(self.papi_about_qt_triggerd)
        # -------------------------------------
        # Create Icons for buttons
        # -------------------------------------
        load_icon = QIcon.fromTheme("document-open")
        save_icon = QIcon.fromTheme("document-save")

        # -------------------------------------
        # Set Icons for buttons
        # -------------------------------------
        self.loadButton.setIconSize(QSize(30, 30))
        self.loadButton.setIcon(load_icon)

        self.saveButton.setIconSize(QSize(30, 30))
        self.saveButton.setIcon(save_icon)


    def set_background_for_gui(self):
        """
        Used to handle request for setting background image.

        :return:
        """
        fileNames = ''

        dialog = QFileDialog(self)
        dialog.setFileMode(QFileDialog.AnyFile)
        #dialog.setNameFilter( self.tr("PaPI-Cfg (*.xml)"))
        dialog.setDirectory(CONFIG_DEFAULT_DIRECTORY)

        if dialog.exec_():
            fileNames = dialog.selectedFiles()

        if len(fileNames):
            if fileNames[0] != '':
                path = fileNames[0]
                pixmap  = QtGui.QPixmap(path)
                self.gui_api.gui_bg_path = path
                self.widgetArea.setBackground(pixmap)

    def update_background(self, path):
        """
        Used to change the background by giving a path to a picture.

        :param path: Path of a picture.
        :return:
        """
        pixmap  = QtGui.QPixmap(path)
        self.widgetArea.setBackground(pixmap)

    def run(self):
        """


        :return:
        """
        # create a timer and set interval for processing events with working loop

        #QtCore.QTimer.singleShot(GUI_WOKRING_INTERVAL, lambda: self.gui_event_processing.gui_working(self.closeEvent))
        self.workingTimer = QtCore.QTimer(self)
        self.workingTimer.timeout.connect(lambda: self.gui_event_processing.gui_working(self.closeEvent, self.workingTimer))
        self.workingTimer.start(GUI_WOKRING_INTERVAL)




    def show_create_plugin_menu(self):
        """


        :return:
        """
        self.create_plugin_menu = CreatePluginMenu(self.gui_api)

        self.create_plugin_menu.show()
        # self.create_plugin_menu.raise_()
        # self.create_plugin_menu.activateWindow()

        # del self.create_plugin_menu
        #
        # self.create_plugin_menu = None

    def show_overview_menu(self):
        """
        Used to show the overview menu.

        :return:
        """
        self.overview_menu = OverviewPluginMenu(self.gui_api)
        self.overview_menu.show()

    def load_triggered(self):
        """
        Used to start the 'load config' dialog.

        :return:
        """
        fileNames = ''

        dialog = QFileDialog(self)
        dialog.setFileMode(QFileDialog.ExistingFile)
        dialog.setNameFilter( self.tr("PaPI-Cfg (*.xml)"))
        dialog.setDirectory(CONFIG_DEFAULT_DIRECTORY)
        dialog.setWindowTitle("Load Configuration")

        if dialog.exec_():
            fileNames = dialog.selectedFiles()

        if len(fileNames):
            if fileNames[0] != '':
                self.last_config = fileNames[0]
                self.gui_api.do_load_xml(fileNames[0])

    def save_triggered(self):
        """
        Used to start the 'save config' dialog.

        :return:
        """
        fileNames = ''

        dialog = QFileDialog(self)
        dialog.setFileMode(QFileDialog.AnyFile)
        dialog.setNameFilter( self.tr("PaPI-Cfg (*.xml)"))
        dialog.setDirectory(CONFIG_DEFAULT_DIRECTORY)
        dialog.setWindowTitle("Save Configuration")
        dialog.setAcceptMode(QFileDialog.AcceptSave)

        if dialog.exec_():
            fileNames = dialog.selectedFiles()

        if len(fileNames):
            if fileNames[0] != '':
                self.gui_api.do_save_xml_config(fileNames[0])

    def closeEvent(self, *args, **kwargs):
        """
        Handle close event.
        Saves current session as 'papi/last_active_papi.xml'
        Closes all opened windows.

        :param args:
        :param kwargs:
        :return:
        """
        try:
            self.gui_api.do_save_xml_config('papi/last_active_papi.xml')
        except Exception as E:
            tb = traceback.format_exc()

        self.gui_api.do_close_program()
        if self.create_plugin_menu is not None:
            self.create_plugin_menu.close()

        if self.overview_menu is not None:
            self.overview_menu.close()

        self.close()

    def add_dplugin(self, dplugin):
        """
        Callback function called by 'DPlugin added signal'
        Used to add a DPlugin SubWindow on the GUI if possible.

        :param dplugin:
        :return:
        """
        if dplugin.type == PLUGIN_VIP_IDENTIFIER or dplugin.type == PLUGIN_PCP_IDENTIFIER:
            sub_window = dplugin.plugin.get_sub_window()
            self.widgetArea.addSubWindow(sub_window)
            sub_window.show()
            size_re = re.compile(r'([0-9]+)')
            config = dplugin.startup_config
            pos = config['position']['value']
            window_pos = size_re.findall(pos)
            sub_window.move(int(window_pos[0]), int(window_pos[1]))

            # see http://qt-project.org/doc/qt-4.8/qt.html#WindowType-enum

            sub_window.setWindowFlags(Qt.CustomizeWindowHint | Qt.WindowMinMaxButtonsHint | Qt.WindowTitleHint )

        if self.overview_menu is not None:
            self.overview_menu.refresh_action(dplugin)

    def remove_dplugin(self, dplugin):
        """
        Callback function called by 'DPlugin removed signal'
        Used to removed a DPlugin SubWindow from the GUI if possible.

        :param dplugin:
        :return:
        """
        if dplugin.type == PLUGIN_VIP_IDENTIFIER or dplugin.type == PLUGIN_PCP_IDENTIFIER:
            self.widgetArea.removeSubWindow(dplugin.plugin.get_sub_window())

    def changed_dgui(self):
        if self.overview_menu is not None:
            self.overview_menu.refresh_action()

    def plugin_died(self, dplugin, e, msg):
        dplugin.state = PLUGIN_STATE_STOPPED

        self.gui_api.do_stopReset_plugin_uname(dplugin.uname)

        errMsg = QtGui.QMessageBox(self)
        errMsg.setFixedWidth(650)
        errMsg.setWindowTitle("Plugin: " + dplugin.uname + " // " + str(e))
        errMsg.setText("Error in plugin" + dplugin.uname + " // " + str(e))
        errMsg.setDetailedText(str(msg))
        errMsg.setWindowModality(Qt.NonModal)
        errMsg.show()

    def error_occured(self, title, msg, detailed_msg):

        errMsg = QtGui.QMessageBox(self)
        errMsg.setFixedWidth(650)
        errMsg.setWindowTitle(title)
        errMsg.setText(str(msg))
        errMsg.setDetailedText(str(detailed_msg))
        errMsg.setWindowModality(Qt.NonModal)
        errMsg.show()

    def toggle_run_mode(self):
        if self.in_run_mode:
            self.in_run_mode = False
            self.loadButton.show()
            self.saveButton.show()
            self.menubar.setHidden(False)

        elif not self.in_run_mode:
            self.in_run_mode = True

            self.loadButton.hide()
            self.saveButton.hide()
            self.menubar.hide()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            if self.in_run_mode:
                self.toggle_run_mode()

    def resize_gui_window(self, w, h):

        self.setGeometry(self.geometry().x(),self.geometry().y(),w,h)
        size = self.size()
        self.gui_api.gui_size_height    = size.height()
        self.gui_api.gui_size_width     = size.width()

    def user_window_resize(self, event):
        size = event.size()
        self.gui_api.gui_size_width = size.width()
        self.gui_api.gui_size_height = size.height()
        self.original_resize_function(event)


    def reload_config(self):
        """
        This function is used to reset PaPI and to reload the last loaded configuration file.
        :return:
        """
        if self.last_config is not None:
            self.reset_papi()
            QtCore.QTimer.singleShot(GUI_WAIT_TILL_RELOAD, lambda: self.gui_api.do_load_xml(self.last_config))

    def reset_papi(self):
        """
        This function is called to reset PaPI. That means all subscriptions were canceled and all plugins were removed.
        :return:
        """
        h = GUI_DEFAULT_HEIGHT
        w = GUI_DEFAULT_WIDTH
        self.setGeometry(self.geometry().x(),self.geometry().y(),w,h)
        self.gui_api.do_reset_papi()

    def papi_wiki_triggerd(self):
        QDesktopServices.openUrl(QUrl("https://github.com/TUB-Control/PaPI/wiki", QUrl.TolerantMode))

    def papi_doc_triggerd(self):
        QDesktopServices.openUrl(QUrl("http://tub-control.github.io/PaPI/", QUrl.TolerantMode))

    def papi_about_triggerd(self):
        QtGui.QMessageBox.about(self,PAPI_ABOUT_TITLE, PAPI_ABOUT_TEXT)

    def papi_about_qt_triggerd(self):
        QtGui.QMessageBox.aboutQt(self)

def startGUI(CoreQueue, GUIQueue,gui_id):
    """
    Function to call to start gui operation
    :param CoreQueue: link to queue of core
    :type CoreQueue: Queue
    :param GUIQueue: queue where gui receives messages
    :type GUIQueue: Queue
    :param gui_id: id of gui for events
    :type gui_id: int
    :return:
    """
    app = QApplication(sys.argv)
    gui = GUI(CoreQueue, GUIQueue,gui_id)
    gui.run()

#   cProfile.runctx('gui.run()', globals(), locals())

    gui.show()
    app.exec_()

def startGUI_TESTMOCK(CoreQueue, GUIQueue,gui_id, data_mock):
    """
    Function to call to start gui operation
    :param CoreQueue: link to queue of core
    :type CoreQueue: Queue
    :param GUIQueue: queue where gui receives messages
    :type GUIQueue: Queue
    :param gui_id: id of gui for events
    :type gui_id: int
    :return:
    """
    app = QApplication(sys.argv)
    app.aboutToQuit.connect(app.deleteLater)

    gui = GUI(CoreQueue, GUIQueue,gui_id, data_mock)

    gui.run()
    gui.show()
    app.exec_()

if __name__ == '__main__':
    # main of GUI, just for stand alone gui testing
    app = QApplication(sys.argv)
    frame = GUI(None,None,None)
    frame.show()
    app.exec_()
