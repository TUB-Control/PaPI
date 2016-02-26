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
Sven Knuth, Stefan Ruppin
"""

import sys
import os
import traceback
import re
import signal
from multiprocessing import Queue, Process

from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog, QMessageBox
from PyQt5.QtGui import QIcon, QDesktopServices, QPixmap
from PyQt5.QtCore import Qt, QUrl
from PyQt5 import QtCore, QtGui

import papi.constants as pc

from papi.ui.gui.default.DefaultMain import Ui_DefaultMain
from papi.data.DGui import DGui
from papi.ConsoleLog import ConsoleLog
from papi.gui.default.item import PaPIFavAction

from papi.gui.default.CreatePluginDialog import CreatePluginDialog
from papi.gui.default.CreatePluginMenu import CreatePluginMenu
from papi.gui.default.OverviewPluginMenu import OverviewPluginMenu
from papi.gui.default.PaPITabManger import PaPITabManger, TabObject
from papi.gui.default.custom import PaPIConfigSaveDialog
from papi.gui.default import get16Icon

from papi.gui.gui_management import GuiManagement

from papi.core import run_core_in_own_process


def run_gui_in_own_process(core_queue, gui_queue, gui_id, args):
    """
    This is the main function which is called to initialize and start the GUI.
    This function is called by the core process in the context of a new process thus the GUI is executed within
    its own process.

    The multiprocessing queues 'core_queue' and 'gui_queue' are used for message exchange.
    Messages within 'core_queue' are received by the core, message within 'gui_queue' are appointed for the GUI.
    Events sent by the GUI are marked with 'gui_id'.
    The object 'args' provides access to the provided cli arguments.

    :param core_queue: link to queue of core
    :type core_queue: Queue
    :param gui_queue: queue where gui receives messages
    :type gui_queue: Queue
    :param gui_id: id of gui for events
    :type gui_id: int
    :return:
    """

    gui_app = QApplication(sys.argv)

    gui = GUI(core_queue=core_queue, gui_queue=gui_queue, gui_id=gui_id)

    # -----------------------------------------
    # Read the arguments specified by the CLI
    # -----------------------------------------
    if args:
        if args.user_config:
            gui.load_config(args.user_config)

        if args.full_screen:
            gui.triggered_toggle_fullscreen()

        if args.run_mode:
            gui.triggered_toggle_run_mode()

        if args.config:
            gui.load_config(args.config)
        else:
            gui.load_config(pc.PAPI_USER_CFG)

        try:
            if args.debug_level:
                gui.log.lvl = int(args.debug_level)
                gui.gui_management.gui_api.log.lvl = int(args.debug_level)
                gui.gui_management.gui_event_processing.log.lvl = int(args.debug_level)
        except:
            pass
    else:
        gui.load_config(pc.PAPI_USER_CFG)

    # -----------------------------------------
    # Start the GUI
    # -----------------------------------------

    gui.run()
    gui.show()
    gui_app.exec_()


class GUI(QMainWindow, Ui_DefaultMain):
    """
    This class defines the default GUI written by PyQt5.

    """

    def __init__(self, core_queue=None, gui_queue=None, gui_id=None, gui_data=None, is_parent=False, parent=None):
        """
        Constructor of this class. Called to initialize the GUI.

        This constructor is called within an own process which is reliable for the GUI and all graphical plugins.

        :param core_queue: Queue used to send PaPI events to the Core
        :param gui_queue: GUI queue which contains PaPI events for the GUI
        :param gui_id: Unique ID for this gui
        :param gui_data: Contains all data for the current session
        :param parent: parent element
        :return:
        """

        super(GUI, self).__init__(parent)
        self.setupUi(self)
        self.is_parent = is_parent

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
            self.core_process = Process(target=run_core_in_own_process,
                                        args=(gui_queue_ref, core_queue_ref, gui_id_ref))
            self.core_process.start()
        else:
            if core_queue is None:
                raise Exception('Gui started with wrong arguments')
            if gui_queue is None:
                raise Exception('Gui started with wrong arguments')
            if not isinstance(gui_id, str):
                raise Exception('Gui started with wrong arguments')

            core_queue_ref = core_queue
            gui_queue_ref = gui_queue
            gui_id_ref = gui_id

        # Create the Tab Manager and the gui management unit #
        # connect some signals of management to gui          #
        # -------------------------------------------------- #
        self.TabManager = PaPITabManger(tabWigdet=self.widgetTabs, centralWidget=self.centralwidget)

        self.gui_management = GuiManagement(core_queue_ref,
                                            gui_queue_ref,
                                            gui_id_ref,
                                            self.TabManager,
                                            self.get_gui_config,
                                            self.set_gui_config
                                            )

        self.TabManager.gui_api = self.gui_management.gui_api
        self.TabManager.dGui = self.gui_management.gui_data

        self.gui_management.gui_event_processing.added_dplugin.connect(self.add_dplugin)
        self.gui_management.gui_event_processing.removed_dplugin.connect(self.remove_dplugin)
        self.gui_management.gui_event_processing.dgui_changed.connect(self.triggered_changed_dgui)
        self.gui_management.gui_event_processing.plugin_died.connect(self.triggered_plugin_died)

        self.gui_management.gui_api.error_occured.connect(self.triggered_error_occurred)



        signal.signal(signal.SIGINT, lambda a, b: self.signal_handler())

        # List for keys that are active
        self.keysActiveList = []

        # -------------------------------------
        # Create placeholder
        # -------------------------------------
        self.overview_menu = None
        self.create_plugin_menu = None
        self.plugin_create_dialog = None

        self.log = None
        self.last_config = None
        self.in_run_mode = None
        self.workingTimer = None

        # initialize the graphic of the gui
        # -------------------------------------------------- #
        self.init_gui_graphic()

    def signal_handler(self):
        """
        This handler will be called, when CTRL+C is used in the console
        It will react to SIGINT Signal
        As an reaction it will close the gui by first telling the core to close and then closing the gui

        :return:
        """

        self.gui_management.gui_api.do_close_program()
        sys.exit(0)

    def init_gui_graphic(self):
        """
        Called to set mandatory variables, create child dialogs and actions.
        This function is called once within the constructor.

        :return:
        """

        self.setWindowTitle(pc.GUI_PAPI_WINDOW_TITLE)
        # set GUI size
        self.setGeometry(self.geometry().x(), self.geometry().y(), pc.GUI_DEFAULT_WIDTH, pc.GUI_DEFAULT_HEIGHT)

        self.log = ConsoleLog(pc.GUI_PROCESS_CONSOLE_LOG_LEVEL, pc.GUI_PROCESS_CONSOLE_IDENTIFIER)
        self.log.printText(1, pc.GUI_START_CONSOLE_MESSAGE + ' .. Process id: ' + str(os.getpid()))

        self.last_config = pc.PAPI_LAST_CFG_PATH

        self.in_run_mode = False

        # -------------------------------------
        # Create menues
        # -------------------------------------
        self.plugin_create_dialog = CreatePluginDialog(self.gui_management.gui_api, self.TabManager)

        # -------------------------------------
        # Create actions
        # -------------------------------------
        _translate = QtCore.QCoreApplication.translate

        self.action_load_config.triggered.connect(self.triggered_load_config)
        self.action_load_config.setShortcut(_translate("DefaultMain", "Ctrl+L"))

        self.action_save_config.triggered.connect(self.triggered_save_config)
        self.action_save_config.setShortcut(_translate("DefaultMain", "Ctrl+S"))

        self.action_open_overview_menu.triggered.connect(self.triggered_open_overview_menu)
        self.action_open_overview_menu.setShortcut(_translate("DefaultMain", "Ctrl+O"))

        self.action_open_create_plugin_menu.triggered.connect(self.triggered_open_create_plugin_menu)
        self.action_open_create_plugin_menu.setShortcut(_translate("DefaultMain", "Ctrl+N"))

        self.action_reset_papi.triggered.connect(self.triggered_reset_papi)
        self.action_reload_config.triggered.connect(self.triggered_reload_config)

        self.action_toggle_run_mode.triggered.connect(self.triggered_toggle_run_mode)

        self.action_reload_plugin_db.triggered.connect(self.triggered_reload_plugin_db)

        self.action_open_papi_wiki.triggered.connect(self.triggered_open_papi_wiki)

        self.action_open_papi_doc.triggered.connect(self.triggered_open_papi_doc)
        self.action_open_papi_doc.setShortcut(_translate("DefaultMain", "Ctrl+H"))

        self.action_open_papi_about.triggered.connect(self.triggered_open_papi_about)
        self.action_open_qt_about.triggered.connect(self.triggered_open_qt_about)

        self.action_toggle_toolbar.triggered.connect(self.triggered_toggle_toolbar)

        self.toolbar.clickedFavouritePlugin.connect(self.toolbar_add_fav_plugin)
        self.toolbar.removedFavouritePlugin.connect(self.fav_plugin_was_removed)

        self.actionFullscreen.triggered.connect(self.triggered_toggle_fullscreen)

        self.init_set_icons()

    def fav_plugin_add(self, plugin_name):
        """
        This function is used to mark an arbitrary plugin as a favourite plugin.
        Favourite plugins are always displayed in the toolbar.

        This function is called by dropping a plugin icon from the create menu on the toolbar.
        It is also called in the initialize phase of the gui for restoring favourite plugin in the configuration file.

        :param plugin_name: Name of the plugin
        :return:
        """

        plugin_manager = self.gui_management.plugin_manager
        plugin_manager.locatePlugins()

        candidates = plugin_manager.getPluginCandidates()
        plugins_info = {c[2].path: c[2] for c in candidates}
        plugins_info_loadable = {p.path: p for p in plugin_manager.getAllPlugins()}

        for plugin_info in plugins_info.values():
            if plugin_info.name == plugin_name:

                if plugin_info.path in plugins_info_loadable.keys():
                    plugin_info = plugins_info_loadable[plugin_info.path]
                    plugin_info.loadable = True
                else:
                    plugin_info.loadable = False

                self.toolbar_add_fav_plugin(plugin_info)

    def fav_plugin_was_removed(self):
        """
        This function is called when a favourite plugin was removed.
        This function is called by using the context menu of the toolbar and using it to remove a plugin.

        :return:
        """

        self.gui_management.gui_api.do_save_xml_config_reloaded(
            pc.PAPI_USER_CFG, plToSave=[], sToSave=[], saveUserSettings=True)

    def init_set_icons(self):
        """
        This function sets the icon for all actions.
        This function is called once during the initializing of the GUI.

        :return:
        """

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
        delete_icon = get16Icon('delete')
        view_icon = get16Icon('reviewing_pane')

        # -------------------------------------
        # Set Icons for actions
        # -------------------------------------
        self.action_load_config.setIcon(load_icon)
        self.action_save_config.setIcon(save_icon)
        self.action_exit.setIcon(exit_icon)
        self.action_open_overview_menu.setIcon(overview_icon)
        self.action_open_create_plugin_menu.setIcon(create_icon)
        self.action_reload_plugin_db.setIcon(reload_icon)
        self.action_reload_config.setIcon(reload_icon)
        self.action_open_papi_wiki.setIcon(help_icon)
        self.action_open_papi_doc.setIcon(help_icon)
        self.action_open_papi_about.setIcon(info_icon)
        self.action_open_qt_about.setIcon(info_icon)
        self.actionAbout_PySide.setIcon(info_icon)
        self.action_reset_papi.setIcon(delete_icon)
        #self.action_toggle_run_mode.setIcon(view_icon)

        # -------------------------------------
        # Set Icons visible in menu
        # -------------------------------------
        self.action_load_config.setIconVisibleInMenu(True)
        self.action_save_config.setIconVisibleInMenu(True)
        self.action_exit.setIconVisibleInMenu(True)
        self.action_open_overview_menu.setIconVisibleInMenu(True)
        self.action_open_create_plugin_menu.setIconVisibleInMenu(True)
        self.action_reload_plugin_db.setIconVisibleInMenu(True)
        self.action_reload_config.setIconVisibleInMenu(True)
        self.action_open_papi_wiki.setIconVisibleInMenu(True)
        self.action_open_papi_doc.setIconVisibleInMenu(True)
        self.action_open_papi_about.setIconVisibleInMenu(True)
        self.action_open_qt_about.setIconVisibleInMenu(True)
        self.actionAbout_PySide.setIconVisibleInMenu(True)
        self.action_reset_papi.setIconVisibleInMenu(True)
        #self.action_toggle_run_mode.setIconVisibleInMenu(True)

    def get_gui_config(self, save_user_settings=False):
        """
        Returns a dictionary which describes the current state of the GUI, like e.g. size, background image and postion.

        This function is called when the current configuration is stored.
        This function is also called when a plugin was marked or unmarked as favourite plugin,

        If 'saveUserSettings==True' the dictionary will also contain the current favourite plugins.
        It is not necessary to save user specific settings when a configuration was saved by using the 'save configuration dialog'.

        :param save_user_settings:
        :return:
        """
        current_active_tab = {
            'Active': str(self.TabManager.get_currently_active_tab())
        }

        tabs = {}
        tab_dict = self.TabManager.get_tabs_by_uname()
        for tab in tab_dict:
            tab_config = tab_dict[tab]
            tabs[tab] = {}
            tabs[tab]['Background'] = tab_config.background
            tabs[tab]['Position'] = str(self.TabManager.getTabPosition_by_name(tab))

        size = {
            'X': str(self.size().width()),
            'Y': str(self.size().height())
        }

        cfg = {
            'ActiveTab': current_active_tab,
            'Tabs': tabs,
            'Size': size
        }

        # ----------------------
        # Set favourite plugins
        # ----------------------
        if save_user_settings:
            favourites = {}
            actions = self.toolbar.actions()
            for i in range(len(actions)):
                action = actions[i]
                if isinstance(action, PaPIFavAction):
                    favourites[action.text()] = {}
                    favourites[action.text()]['position'] = str(i)

            cfg['Favourites'] = favourites

        return cfg

    def set_gui_config(self, cfg):
        """
        A configuration as dictionary is loaded by this function.
        This function is called when a configuration was loaded. It restores attributes as size, position and favourite plugins.

        :param cfg:
        :type {};
        :return:
        """

        #################
        # windows size: #
        #################
        if 'Size' in cfg:
            w = int(cfg['Size']['X'])
            h = int(cfg['Size']['Y'])
            self.resize_gui_window(w, h)

        # ------------------------
        # Restore favourite icons
        # ------------------------
        if 'Favourites' in cfg:
            sorted_positions = {}

            for plugin in cfg['Favourites']:
                sorted_positions[int(cfg['Favourites'][plugin]['position'])] = plugin

            for position in sorted(sorted_positions.keys()):
                plugin = sorted_positions[position]
                self.fav_plugin_add(plugin)

        # -----------------------
        # Restore Tabs
        # -----------------------
        if 'Tabs' in cfg:
            for tabName in cfg['Tabs']:
                tab = cfg['Tabs'][tabName]
                self.TabManager.add_tab(tabName)
                if 'Background' in tab:
                    self.TabManager.set_background_for_tab_with_name(tabName, tab['Background'])

    def triggered_reload_plugin_db(self):
        """
        This callback function reloads the list of plugins of the plugin manager.
        This function is triggered by using the action "Reload DB" in the toolbar menu "Plugin".

        :return:
        """
        self.gui_management.plugin_manager.collectPlugins()

    def run(self):
        """
        Creates a timer and sets an interval for processing events with working loop.

        :return:
        """

        self.workingTimer = QtCore.QTimer(self)
        self.workingTimer.timeout.connect(
            lambda: self.gui_management.gui_event_processing.gui_working(
                self.closeEvent, self.workingTimer
            )
        )
        self.workingTimer.start(pc.GUI_WOKRING_INTERVAL)

    def triggered_open_create_plugin_menu(self):
        """
        Used to open the create plugin menu.
        This function is triggered by using the action "Create" in the toolbar menu "Plugin" or
        by the action "Create" in the toolbar.

        :return:
        """

        self.create_plugin_menu = CreatePluginMenu(self.gui_management.gui_api,
                                                   self.TabManager,
                                                   self.gui_management.plugin_manager)
        self.create_plugin_menu.show()

    def triggered_open_overview_menu(self):
        """
        Used to open the overview menu.
        This function is triggered by using the action "Overview" in the toolbar menu "Plugin" or
        by the action "Overview" in the toolbar.

        :return:
        """
        self.overview_menu = OverviewPluginMenu(self.gui_management.gui_api, self.gui_management.tab_manager)
        self.overview_menu.show()

    def triggered_toggle_toolbar(self):
        """
        Used to toogle the vision of the the toolbar
        This function is triggered by using the action "Toolbar" in the toolbar menu "View".

        :return:
        """

        self.toolbar.setHidden(not self.toolbar.isHidden())

        self.action_toggle_toolbar.setChecked(not self.toolbar.isHidden())

    def triggered_toggle_fullscreen(self):
        """

        :return:
        """
        if self.isFullScreen() is False:
            self.toolbar.setHidden(True)
            self.action_toggle_toolbar.setChecked(False)
            self.showFullScreen()
        else:
            self.toolbar.setHidden(False)
            self.action_toggle_toolbar.setChecked(True)
            self.showNormal()

        self.actionFullscreen.setChecked(self.isFullScreen())
        self.actionFullscreen.setChecked(self.isFullScreen())

    def triggered_load_config(self):
        """
        Used to open the 'load config' dialog.
        This function is triggered by using the action "Load" in the toolbar menu "PaPI" or
        by the action "Load" in the toolbar.

        :return:
        """
        file_names = ''

        dialog = QFileDialog(self)
        dialog.setFileMode(QFileDialog.ExistingFile)
        dialog.setNameFilter(self.tr("PaPI-Cfg (*.xml)"))
        dialog.setDirectory(os.path.abspath(pc.CONFIG_DEFAULT_DIRECTORY))
        dialog.setWindowTitle("Load Configuration")

        if dialog.exec_():
            file_names = dialog.selectedFiles()

        if len(file_names):
            if file_names[0] != '':
                self.last_config = file_names[0]
                self.load_config(file_names[0])

    def load_config(self, file_name):
        """
        Called with a PaPI XML Configuration which is determined by file_name,
        This function is called when a configuration file was chosen by the "Load Dialog" and during the initialize phase for loading
        the user specific configuration file.

        :param file_name:
        :return:
        """

        self.gui_management.gui_api.do_load_xml(file_name)

    def triggered_save_config(self):
        """
        Used to start the 'save config' dialog.
        This function is triggered by using the action "Save" in the toolbar menu "PaPI" or
        by the action "Save" in the toolbar.

        :return:
        """

        file_names = ''

        dialog = PaPIConfigSaveDialog(self, self.gui_management.gui_api)

        dialog.fill_with()

        if dialog.exec_():
            file_names = dialog.selectedFiles()

        plugin_list, subscription_list = dialog.get_create_lists()

        if len(file_names):
            if file_names[0] != '':
                if "json" in dialog.selectedNameFilter():
                    self.gui_management.gui_api.do_save_json_config_reloaded(
                        file_names[0], plToSave=plugin_list, sToSave=subscription_list
                    )

                if "xml" in dialog.selectedNameFilter():
                    self.gui_management.gui_api.do_save_xml_config_reloaded(
                        file_names[0], plToSave=plugin_list, sToSave=subscription_list
                    )

    def closeEvent(self, *args, **kwargs):
        """
        Handles close events.
        Saves current session as pc.PAPI_LAST_CFG_PATH
        Closes all opened windows.

        :param args:
        :param kwargs:
        :return:
        """

        try:
            self.gui_management.gui_api.do_save_xml_config_reloaded(pc.PAPI_LAST_CFG_PATH)
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

        Is called whenever a plugin was created.

        :param dplugin:
        :return:
        """

        if dplugin.type == pc.PLUGIN_VIP_IDENTIFIER:

            sub_window = dplugin.plugin._get_sub_window()
            
            config = dplugin.startup_config
            tab_name = config['tab']['value']
            if tab_name in self.TabManager.get_tabs_by_uname():
                area = self.TabManager.get_tabs_by_uname()[tab_name]
            else:
                self.log.printText(1, 'add dplugin: no tab with tab_id of dplugin')
                area = self.TabManager.add_tab(tab_name)

            area.addSubWindow(sub_window)

            is_maximized= config['maximized']['value'] == '1'

            size_re = re.compile(r'([0-9]+)')

            pos = config['position']['value']
            window_pos = size_re.findall(pos)
            sub_window.move(int(window_pos[0]), int(window_pos[1]))

            if not is_maximized:
                sub_window.show()
            else:
                sub_window.showMaximized()

            # see http://qt-project.org/doc/qt-4.8/qt.html#WindowType-enum
            sub_window.setWindowFlags(Qt.CustomizeWindowHint | Qt.WindowMinMaxButtonsHint | Qt.WindowTitleHint)

            if self.in_run_mode:
                sub_window.disableInteraction()

        if self.overview_menu is not None:
            self.overview_menu.refresh_action(dplugin)

    def remove_dplugin(self, dplugin):
        """
        Callback function called by 'DPlugin removed signal'
        Used to removed a DPlugin SubWindow from the GUI if possible.

        Is called whenever a plugin was removed.

        :param dplugin:
        :return:
        """

        if dplugin.type == pc.PLUGIN_VIP_IDENTIFIER:
            config = dplugin.plugin.pl_get_current_config()
            tab_name = config['tab']['value']
            if tab_name in self.TabManager.get_tabs_by_uname():
                tabOb = self.TabManager.get_tabs_by_uname()[tab_name]
                tabOb.removeSubWindow(dplugin.plugin._get_sub_window())
                if tabOb.closeIfempty is True:
                    if len(tabOb.subWindowList()) == 0:
                        if isinstance(tabOb, TabObject):
                            self.TabManager.closeTab_by_name(tabOb.name)
                        else:
                            self.TabManager.remove_window(tabOb)

    def triggered_changed_dgui(self):
        """
        This is triggered to refresh the overview menu if it is active.
        This is needed to guarantee the consistency between the data structure dgui and the data seen by the user.

        :return:
        """
        if self.overview_menu is not None:
            self.overview_menu.refresh_action()

    def triggered_plugin_died(self, dplugin, e, msg):
        """
        Triggered when a plugin died.

        :param dplugin:
        :param e:
        :param msg:
        :return:
        """

        dplugin.state = pc.PLUGIN_STATE_STOPPED

        self.gui_management.gui_api.do_stopReset_plugin_uname(dplugin.uname)

        err_msg = QtGui.QMessageBox(self)
        err_msg.setFixedWidth(650)

        err_msg.setIcon(QtGui.QMessageBox.Critical)
        err_msg.setSizeGripEnabled(True)
        err_msg.setWindowTitle("Plugin: " + dplugin.uname + " // " + str(e))
        err_msg.setText("Error in plugin" + dplugin.uname + " // " + str(e))
        err_msg.setDetailedText(str(msg))
        err_msg.setWindowModality(Qt.NonModal)
        err_msg.show()

    def triggered_error_occurred(self, title, msg, detailed_msg):
        """
        Triggered when an error occured. Creates an error dialog for the user.
        Title defines the title of the error dialog.
        Msg contains a messages displayed in the dialog.
        Detailed_msg should contain more information about the occured error which is optional displayed.

        :param title:
        :param msg:
        :param detailed_msg:
        :return:
        """

        err_msg = QtGui.QMessageBox(self)
        err_msg.setFixedWidth(650)

        err_msg.setWindowTitle(title)
        err_msg.setText(str(msg))
        err_msg.setDetailedText(str(detailed_msg))
        err_msg.setWindowModality(Qt.NonModal)
        err_msg.show()

    def triggered_toggle_run_mode(self):
        """
        Toggles the run mode, i.e. it changes from active to passive and vice versa.
        This function is triggered by using the action "Toolbar" in the toolbar menu "View".

        :return:
        """

        if self.in_run_mode is False:
            # hide toolbar
            self.toolbar.setHidden(True)
            self.action_toggle_toolbar.setChecked(False)
            # disable context menu of tabmanger
            self.TabManager.disableContextMenus()
            self.TabManager.setTabs_movable_closable(False, False)
            self.action_toggle_run_mode.setChecked(True)
            # lock subwindows in tabs
            for tab_name in self.TabManager.tab_dict_uname:
                tab = self.TabManager.tab_dict_uname[tab_name]

                for sub_window in tab.subWindowList():
                    sub_window.disableInteraction()
            self.in_run_mode = True
            self.menubar.hide()
        else:
            # show toolbar
            self.toolbar.setHidden(False)
            self.action_toggle_toolbar.setChecked(True)
            # disable context menu of tabmanger
            self.TabManager.enableContextMenus()
            self.TabManager.setTabs_movable_closable(True, True)
            self.action_toggle_run_mode.setChecked(False)
            # unlock subwindows in tabs
            for tab_name in self.TabManager.tab_dict_uname:
                tab = self.TabManager.tab_dict_uname[tab_name]

                for sub_window in tab.subWindowList():
                    sub_window.enableInteraction()
            self.in_run_mode = False
            self.menubar.show()

    def keyPressEvent(self, event):
        """
        Default callback function which is called when an any key was pressed by the user.

        :param event:
        :return:
        """

        if event.key() not in self.keysActiveList:
            self.keysActiveList.append(event.key())

        # if QtCore.Qt.Key_Escape in self.keysActiveList:
            # if self.in_run_mode:
            #     self.triggered_toggle_run_mode()
            # if self.isFullScreen():
            #     self.triggered_toggle_fullscreen()

        if QtCore.Qt.Key_D in self.keysActiveList and QtCore.Qt.Key_Control in self.keysActiveList:
            self.gui_management.tab_manager.select_next_tab()
            self.keysActiveList.remove(QtCore.Qt.Key_D)

        if QtCore.Qt.Key_A in self.keysActiveList and QtCore.Qt.Key_Control in self.keysActiveList:
            self.gui_management.tab_manager.select_prev_tab()
            self.keysActiveList.remove(QtCore.Qt.Key_A)

        if QtCore.Qt.Key_M in self.keysActiveList and QtCore.Qt.Key_Control in self.keysActiveList:
            self.toggleMenuBarHide()

    def keyReleaseEvent(self, event):
        """
        Default callback function which is called when any key was released by the user.

        :param event:
        :return:
        """

        if event.key() in self.keysActiveList:
            self.keysActiveList.remove(event.key())

    def resize_gui_window(self, w, h):
        """
        Internal function for resizing the window of the GUI.

        :param event:
        :return:
        """

        self.setGeometry(self.geometry().x(), self.geometry().y(), w, h)

    def toggleMenuBarHide(self):
            if not self.menubar.isHidden():
                self.menubar.hide()
            else:
                self.menubar.show()

    def triggered_reload_config(self):
        """
        This function is used to reset PaPI and to reload the last loaded configuration file.

        :return:
        """

        if self.last_config is not None:
            self.triggered_reset_papi()
            QtCore.QTimer.singleShot(pc.GUI_WAIT_TILL_RELOAD,
                                     lambda: self.gui_management.gui_api.do_load_xml(self.last_config))

    def triggered_reset_papi(self):
        """
        This function is called to reset PaPI. That means all subscriptions are canceled and all plugins are removed.
        This function is triggered by using the action "Reset" in the toolbar menu "PaPI" or
        by the action "Reset" in the toolbar.

        :return:
        """

        h = pc.GUI_DEFAULT_HEIGHT
        w = pc.GUI_DEFAULT_WIDTH

        self.setGeometry(self.geometry().x(), self.geometry().y(), w, h)
        self.TabManager.set_all_tabs_to_close_when_empty(True)
        self.TabManager.close_all_empty_tabs()
        self.gui_management.gui_api.do_reset_papi()

    def triggered_open_papi_wiki(self):
        """
        Opens the PaPI Wiki in the default browser.
        This function is triggered by using the action "PaPI Wiki" in the toolbar menu "Help".

        :return:
        """

        QDesktopServices.openUrl(QUrl(pc.PAPI_WIKI_URL, QUrl.TolerantMode))

    def triggered_open_papi_doc(self):
        """
        Opens the PaPI documentation in the default browser.
        This function is triggered by using the action "PaPI Doc" in the toolbar menu "Help".

        :return:
        """

        QDesktopServices.openUrl(QUrl(pc.PAPI_DOC_URL, QUrl.TolerantMode))

    def triggered_open_papi_about(self):
        """
        Opens a dialog with information about PaPI.
        This function is triggered by using the action "About" in the toolbar menu "Help".

        :return:
        """

        QMessageBox.about(self, pc.PAPI_ABOUT_TITLE, pc.PAPI_ABOUT_TEXT)

    def triggered_open_qt_about(self):
        """
        Opens the default dialog provided by Qt which contains information about Qt.
        This function is triggered by using the action "About Qt" in the toolbar menu "Help".

        :return:
        """

        QMessageBox.aboutQt(self)

    def toolbar_add_fav_plugin(self, plugin_info):
        """
        Adds an plugin described by plugin_info to the toolbar as an action.
        Plugin_info is an object which is created by the plugin manager yapsy to describe a plugin.
        The description contains information like e.g., name and path.

        :param plugin_info:
        :return:
        """

        l = len(plugin_info.name)
        path = plugin_info.path[:-l]
        path += 'box.png'
        px = QPixmap(path)

        icon = QIcon(px)

        for action in self.toolbar.actions():
            if action.text() == plugin_info.name:
                return

        plugin_action = PaPIFavAction(icon, plugin_info.name, self)
        plugin_action.triggered.connect(lambda ignore, p1=plugin_info: self.show_create_plugin_dialog(p1))

        self.toolbar.addAction(plugin_action)

        self.gui_management.gui_api.do_save_xml_config_reloaded(
            pc.PAPI_USER_CFG, plToSave=[], sToSave=[], saveUserSettings=True)

    def show_create_plugin_dialog(self, plugin_info):
        """
        Opens the create plugin dialog for a plugin described by plugin_info.
        Plugin_info is an object which is created by the plugin manager yapsy to describe a plugin.
        The description contains information like e.g., name and path.

        This dialog is triggered by clicking on a favourite plugin.

        :param plugin_info:
        :return:
        """

        if plugin_info is not None:
            if plugin_info.loadable:
                self.plugin_create_dialog.set_plugin(plugin_info)
                self.plugin_create_dialog.show()

def startGUI_TESTMOCK(CoreQueue, GUIQueue, gui_id, data_mock):
    """
    Function to call to start gui operation
    Function is used for testing.

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

    gui = GUI(CoreQueue, GUIQueue, gui_id, data_mock)

    gui.run()
    gui.show()
    app.exec_()

if __name__ == '__main__':
    # main of GUI, just for stand alone gui testing
    app = QApplication(sys.argv)
    frame = GUI(None, None, None)
    frame.show()
    app.exec_()