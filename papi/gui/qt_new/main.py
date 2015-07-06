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
Sven Knuth, Stefan Ruppin
"""

__author__ = 'knuths'

import sys
import os
import traceback
import re


from PyQt5.QtWidgets           import QMainWindow, QApplication, QFileDialog, QMessageBox
from PyQt5.QtGui               import QIcon, QDesktopServices
from PyQt5.QtCore              import QSize, Qt, QUrl
from PyQt5 import QtCore, QtGui

import papi.pyqtgraph

from papi.ui.gui.qt_new.main           import Ui_QtNewMain
from papi.data.DGui             import DGui
from papi.ConsoleLog            import ConsoleLog


from papi.constants import GUI_PAPI_WINDOW_TITLE, GUI_WOKRING_INTERVAL, GUI_PROCESS_CONSOLE_IDENTIFIER, \
    GUI_PROCESS_CONSOLE_LOG_LEVEL, GUI_START_CONSOLE_MESSAGE, GUI_WAIT_TILL_RELOAD, GUI_DEFAULT_HEIGHT, GUI_DEFAULT_WIDTH, \
    PLUGIN_STATE_PAUSE, PLUGIN_STATE_STOPPED, PAPI_ABOUT_TEXT, PAPI_ABOUT_TITLE, PAPI_DEFAULT_BG_PATH, PAPI_LAST_CFG_PATH
from papi.constants import CONFIG_DEFAULT_FILE, PLUGIN_VIP_IDENTIFIER, PLUGIN_PCP_IDENTIFIER, CONFIG_DEFAULT_DIRECTORY

import papi.constants as pc


from papi.gui.qt_new.create_plugin_menu import CreatePluginMenu
from papi.gui.qt_new.overview_menu import OverviewPluginMenu
from papi.gui.qt_new.PapiTabManger import PapiTabManger, TabObject, PaPIWindow

from papi.gui.qt_new.custom import PaPIConfigSaveDialog

from papi.gui.gui_management import GuiManagement

from papi.gui.qt_new import get32Icon, get16Icon

from multiprocessing import Queue, Process
from papi.core import run_core_in_own_process
import signal


# Disable antialiasing for prettier plots
#pg.setConfigOptions(antialias=False)

def run_gui_in_own_process(CoreQueue, GUIQueue, gui_id, args):
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

    gui = GUI(core_queue=CoreQueue, gui_queue=GUIQueue, gui_id=gui_id)
    gui.run()
    # cProfile.runctx('gui.run()', globals(), locals()) # for benchmarks
    gui.show()

    if args:
        if args.config:
            gui.load_config(args.config)

        try:
            if args.debug_level:
                gui.log.lvl = int(args.debug_level)
        except:
            pass

    app.exec_()


class GUI(QMainWindow, Ui_QtNewMain):
    """
    Used to create the qt based PaPI gui.

    """
    def __init__(self, core_queue = None, gui_queue= None, gui_id = None, gui_data = None, is_parent = False, parent=None):
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
        self.is_parent = is_parent

        self.setupUi(self)

        # Create a data structure for gui if it is missing
        # -------------------------------------------------- #
        if not isinstance(gui_data, DGui):
            self.gui_data = DGui()
        else:
            self.gui_data = gui_data


        # check if gui should be the parent process or core is the parent
        # start core if gui is parent
        # -------------------------------------------------- #
        self.core_process = None
        if is_parent:
            core_queue_ref = Queue()
            gui_queue_ref = Queue()
            gui_id_ref = 1
            self.core_process = Process(target = run_core_in_own_process,
                                        args=(gui_queue_ref,core_queue_ref, gui_id_ref ))
            self.core_process.start()
        else:
            if core_queue is None:
                raise Exception('Gui started with wrong arguments')
            if gui_queue is None:
                raise Exception('Gui started with wrong arguments')
            if not isinstance(gui_id, int):
                raise Exception('Gui started with wrong arguments')

            core_queue_ref = core_queue
            gui_queue_ref = gui_queue
            gui_id_ref = gui_id


        # Create the Tab Manager and the gui management unit #
        # connect some signals of management to gui          #
        # -------------------------------------------------- #
        self.TabManager = PapiTabManger(tabWigdet=self.widgetTabs, centralWidget=self.centralwidget)

        self.gui_management = GuiManagement(core_queue_ref,
                                    gui_queue_ref,
                                    gui_id_ref,
                                    self.TabManager,
                                    self.get_gui_config,
                                    self.set_gui_config)

        self.TabManager.gui_api = self.gui_management.gui_api
        self.TabManager.dGui    = self.gui_management.gui_data

        self.gui_management.gui_event_processing.added_dplugin.connect(self.add_dplugin)
        self.gui_management.gui_event_processing.removed_dplugin.connect(self.remove_dplugin)
        self.gui_management.gui_event_processing.dgui_changed.connect(self.changed_dgui)
        self.gui_management.gui_event_processing.plugin_died.connect(self.plugin_died)

        self.gui_management.gui_api.error_occured.connect(self.error_occured)

        # initialize the graphic of the gui
        # -------------------------------------------------- #
        self.gui_graphic_init()

        signal.signal(signal.SIGINT, lambda a,b: self.signal_handler(a,b))



    def signal_handler(self,signal, frame):
        """
        This handler will be called, when CTRL+C is used in the console
        It will react to SIGINT Signal
        As an reaction it will close the gui by first telling the core to close and then closing the gui
        :return:
        """
        self.gui_management.gui_api.do_close_program()
        sys.exit(0)


    def gui_graphic_init(self):
        self.setWindowTitle(GUI_PAPI_WINDOW_TITLE)
        # set GUI size
        self.setGeometry(self.geometry().x(),self.geometry().y(),GUI_DEFAULT_WIDTH,GUI_DEFAULT_HEIGHT)

        self.count = 0

        self.log = ConsoleLog(GUI_PROCESS_CONSOLE_LOG_LEVEL, GUI_PROCESS_CONSOLE_IDENTIFIER)

        self.log.printText(1,GUI_START_CONSOLE_MESSAGE + ' .. Process id: '+str(os.getpid()))

        self.last_config = PAPI_LAST_CFG_PATH

        self.in_run_mode = False

        # -------------------------------------
        # Create placeholder
        # -------------------------------------
        self.overview_menu = None
        self.create_plugin_menu = None
        # -------------------------------------
        # Create callback functions for buttons
        # -------------------------------------
        #self.loadButton.clicked.connect(self.load_triggered)
        #self.saveButton.clicked.connect(self.save_triggered)

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

        self.actionReload_Plugin_DB.triggered.connect(self.reload_plugin_db)

        self.actionPaPI_Wiki.triggered.connect(self.papi_wiki_triggerd)

        self.actionPaPI_Doc.triggered.connect(self.papi_doc_triggerd)
        self.actionAbout.triggered.connect(self.papi_about_triggerd)
        self.actionAbout_Qt.triggered.connect(self.papi_about_qt_triggerd)

        self.set_icons()

    def set_icons(self):
        # -------------------------------------
        # Create Icons for buttons
        # -------------------------------------
        load_icon = get32Icon('folder')
        save_icon = get32Icon('file_save_as')
        # -------------------------------------
        # Set Icons for buttons
        # -------------------------------------
        #self.loadButton.setIconSize(QSize(32, 32))
        #self.loadButton.setIcon(load_icon)

        #self.saveButton.setIconSize(QSize(32, 32))
        #self.saveButton.setIcon(save_icon)

        # -------------------------------------
        # Create Icons for actions
        # -------------------------------------
        load_icon = get16Icon('folder')
        save_icon = get16Icon('file_save_as')
        exit_icon = get16Icon('cancel')
        overview_icon = get16Icon('tree_list')
        create_icon = get16Icon('application_add')
        reload_icon = get16Icon('arrow_rotate_clockwise')
        help_icon = get16Icon('help')
        info_icon = get16Icon('information')
        refresh_icon = get16Icon('arrow_refresh')
        delete_icon = get16Icon('delete')
        view_icon = get16Icon('reviewing_pane')

        # -------------------------------------
        # Set Icons for actions
        # -------------------------------------
        self.actionLoad.setIcon(load_icon)
        self.actionSave.setIcon(save_icon)
        self.actionExit.setIcon(exit_icon)
        self.actionOverview.setIcon(overview_icon)
        self.actionCreate.setIcon(create_icon)
        self.actionReload_Plugin_DB.setIcon(reload_icon)
        self.actionReloadConfig.setIcon(reload_icon)
        self.actionPaPI_Wiki.setIcon(help_icon)
        self.actionPaPI_Doc.setIcon(help_icon)
        self.actionAbout.setIcon(info_icon)
        self.actionAbout_Qt.setIcon(info_icon)
        self.actionAbout_PySide.setIcon(info_icon)
        self.actionResetPaPI.setIcon(delete_icon)
        self.actionRunMode.setIcon(view_icon)

        # -------------------------------------
        # Set Icons visible in menu
        # -------------------------------------
        self.actionLoad.setIconVisibleInMenu(True)
        self.actionSave.setIconVisibleInMenu(True)
        self.actionExit.setIconVisibleInMenu(True)
        self.actionOverview.setIconVisibleInMenu(True)
        self.actionCreate.setIconVisibleInMenu(True)
        self.actionReload_Plugin_DB.setIconVisibleInMenu(True)
        self.actionReloadConfig.setIconVisibleInMenu(True)
        self.actionPaPI_Wiki.setIconVisibleInMenu(True)
        self.actionPaPI_Doc.setIconVisibleInMenu(True)
        self.actionAbout.setIconVisibleInMenu(True)
        self.actionAbout_Qt.setIconVisibleInMenu(True)
        self.actionAbout_PySide.setIconVisibleInMenu(True)
        self.actionResetPaPI.setIconVisibleInMenu(True)
        self.actionRunMode.setIconVisibleInMenu(True)

    def get_gui_config(self):

        actTab = {}
        actTab['Active'] = str(self.TabManager.get_currently_active_tab())

        tabs = {}
        tab_dict = self.TabManager.get_tabs_by_uname()
        for tab in tab_dict:
            tabOb = tab_dict[tab]
            tabs[tab]= {}
            tabs[tab]['Background'] = tabOb.background
            tabs[tab]['Position'] = str(self.TabManager.getTabPosition_by_name(tab))

        size = {}

        size['X']= str(self.size().width())

        size['Y']= str(self.size().height())

        cfg = {}
        cfg['ActiveTab'] = actTab
        cfg['Tabs'] = tabs
        cfg['Size'] = size

        return cfg

    def set_gui_config(self, cfg):
        #################
        # Cfgs for Tabs #
        #################
        if 'tabs' in cfg:
            tabList = {}
            for tab in cfg['tabs']:
                # Tab Name
                name = tab

                # Tab details
                tabDetails = cfg['tabs'][tab]

                # check for background
                if 'background' in tabDetails:
                    bg = tabDetails['background']
                    if bg != 'default':
                        self.TabManager.set_background_for_tab_with_name(name,bg)
                else:
                    bg = None

                # check for position
                if 'position' in tabDetails:
                    pos = int(tabDetails['position'])
                else:
                    if len(list(tabList.keys())) > 1:
                        pos = max(list(tabList.keys()))+1
                    else:
                        pos = 0

                tabList[pos] = [name, bg]

            # sort tabs acoriding to positions
            keys = list(tabList.keys())
            keys.sort()
            for position in keys:
                name = tabList[position][0]
                bg = tabList[position][1]
                tabOb = self.TabManager.add_tab(name)
                self.TabManager.set_background_for_tab_with_name(name,bg)

        if 'activeTab' in cfg:
            if 'value' in cfg['activeTab']['active']:
                self.TabManager.set_tab_active_by_index(int( cfg['activeTab']['active']['value'] ))

        #################
        # windows size: #
        #################
        if 'size' in cfg:
            w = int(cfg['size']['x']['value'])
            h = int(cfg['size']['y']['value'])
            self.resize_gui_window(w,h)

    def reload_plugin_db(self):
        """
        This Callback function will reload the plugin list of the plugin manager

        :return:
        """
        self.gui_management.plugin_manager.collectPlugins()

    def run(self):
        """


        :return:
        """
        # create a timer and set interval for processing events with working loop

        #QtCore.QTimer.singleShot(GUI_WOKRING_INTERVAL, lambda: self.gui_event_processing.gui_working(self.closeEvent))
        self.workingTimer = QtCore.QTimer(self)
        self.workingTimer.timeout.connect(lambda: self.gui_management.gui_event_processing.gui_working(self.closeEvent, self.workingTimer))
        self.workingTimer.start(GUI_WOKRING_INTERVAL)




    def show_create_plugin_menu(self):
        """


        :return:
        """
        self.create_plugin_menu = CreatePluginMenu(self.gui_management.gui_api,
                                                   self.TabManager,
                                                   self.gui_management.plugin_manager )

        self.create_plugin_menu.show()

    def show_overview_menu(self):
        """
        Used to show the overview menu.

        :return:
        """
        self.overview_menu = OverviewPluginMenu(self.gui_management.gui_api)
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
                self.load_config(fileNames[0])

    def load_config(self, file_name):
        self.gui_management.gui_api.do_load_xml(file_name)

    def save_triggered(self):
        """
        Used to start the 'save config' dialog.

        :return:
        """
        fileNames = ''

        dialog = PaPIConfigSaveDialog(self)

        dialog.fill_with(self.gui_management.gui_api.gui_data)

        if dialog.exec_():
            fileNames = dialog.selectedFiles()

        plugin_list, subscription_list = dialog.get_create_lists()

        if len(fileNames):

            if fileNames[0] != '':
                self.gui_management.gui_api.do_save_xml_config_reloaded(fileNames[0], plToSave=plugin_list, sToSave=subscription_list)

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
            self.gui_management.gui_api.do_save_xml_config('papi/last_active_papi.xml')
        except Exception as E:
            tb = traceback.format_exc()

        self.gui_management.gui_api.do_close_program()
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

            # sub_window_ori = dplugin.plugin.get_sub_window()
            #
            # dplugin.plugin.set_window_for_internal_usage(PaPIMDISubWindow())
            # dplugin.plugin.set_widget_for_internal_usage(sub_window_ori.widget())

            sub_window = dplugin.plugin.get_sub_window()

            config = dplugin.startup_config
            tab_name = config['tab']['value']
            if tab_name in self.TabManager.get_tabs_by_uname():
                area = self.TabManager.get_tabs_by_uname()[tab_name]
            else:
                self.log.printText(1,'add dplugin: no tab with tab_id of dplugin')
                area = self.TabManager.add_tab(tab_name)

            area.addSubWindow(sub_window)

            sub_window.show()

            size_re = re.compile(r'([0-9]+)')

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
            config = dplugin.plugin.config
            tab_name = config['tab']['value']
            if tab_name in self.TabManager.get_tabs_by_uname():
                tabOb = self.TabManager.get_tabs_by_uname()[tab_name]
                tabOb.removeSubWindow(dplugin.plugin.get_sub_window())
                if tabOb.closeIfempty is True:
                    if len(tabOb.subWindowList()) == 0:
                        if isinstance(tabOb, TabObject):
                            self.TabManager.closeTab_by_name(tabOb.name)
                        else:
                            self.TabManager.remove_window(tabOb)


    def changed_dgui(self):
        if self.overview_menu is not None:
            self.overview_menu.refresh_action()

    def plugin_died(self, dplugin, e, msg):
        dplugin.state = PLUGIN_STATE_STOPPED

        self.gui_management.gui_api.do_stopReset_plugin_uname(dplugin.uname)

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
            self.toogle_lock()

        elif not self.in_run_mode:
            self.in_run_mode = True
            self.loadButton.hide()
            self.saveButton.hide()
            self.menubar.hide()
            self.toogle_lock()

    def toogle_lock(self):

        if self.in_run_mode:
            for tab_name in self.TabManager.get_tabs_by_uname():
                area = self.TabManager.get_tabs_by_uname()[tab_name]

                windowsList = area.subWindowList()

                for window in windowsList:

                    #window.setAttribute(Qt.WA_NoBackground)

                    #window.setAttribute(Qt.WA_NoSystemBackground)
                    #window.setAttribute(Qt.WA_TranslucentBackground)
                    #window.set_movable(False)
                    window.setMouseTracking(False)
                    window.setWindowFlags(~Qt.WindowMinMaxButtonsHint & (Qt.CustomizeWindowHint | Qt.WindowTitleHint))

        if not self.in_run_mode:
            for tab_name in self.TabManager.get_tabs_by_uname():
                area = self.TabManager.get_tabs_by_uname()[tab_name]

                windowsList = area.subWindowList()

                for window in windowsList:
                    #window.set_movable(True)
                    window.setMouseTracking(True)
                    window.setWindowFlags(Qt.CustomizeWindowHint | Qt.WindowMinMaxButtonsHint | Qt.WindowTitleHint )

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Escape:
            if self.in_run_mode:
                self.toggle_run_mode()

    def resize_gui_window(self, w, h):
        self.setGeometry(self.geometry().x(),self.geometry().y(),w,h)


    def reload_config(self):
        """
        This function is used to reset PaPI and to reload the last loaded configuration file.
        :return:
        """
        if self.last_config is not None:
            self.reset_papi()
            QtCore.QTimer.singleShot(GUI_WAIT_TILL_RELOAD, lambda: self.gui_management.gui_api.do_load_xml(self.last_config))

    def reset_papi(self):
        """
        This function is called to reset PaPI. That means all subscriptions were canceled and all plugins were removed.
        :return:
        """
        h = GUI_DEFAULT_HEIGHT
        w = GUI_DEFAULT_WIDTH
        self.setGeometry(self.geometry().x(),self.geometry().y(),w,h)

        self.TabManager.set_all_tabs_to_close_when_empty(True)
        self.TabManager.close_all_empty_tabs()

        self.gui_management.gui_api.do_reset_papi()



    def papi_wiki_triggerd(self):
        QDesktopServices.openUrl(QUrl(pc.PAPI_WIKI_URL, QUrl.TolerantMode))

    def papi_doc_triggerd(self):
        QDesktopServices.openUrl(QUrl(pc.PAPI_DOC_URL, QUrl.TolerantMode))

    def papi_about_triggerd(self):
        QMessageBox.about(self,PAPI_ABOUT_TITLE, PAPI_ABOUT_TEXT)

    def papi_about_qt_triggerd(self):
        QMessageBox.aboutQt(self)




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
