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

You should have received a copy of the GNU General Public License
along with PaPI.  If not, see <http://www.gnu.org/licenses/>.

Contributors:
Stefan Ruppin
"""

import re
from PyQt5.QtWidgets import QMdiSubWindow, QMenu, QAction
from papi.plugin.base_classes.base_plugin import base_plugin
from papi.constants import PLUGIN_VIP_IDENTIFIER



class base_visual(base_plugin):
    """
    This class is used by all plugins which are not running in an own process.
    They are all executed the gui process.

    """
    def __init__(self):
        super(base_visual, self).__init__()

    def _init_plugin(self, CoreQueue, pluginQueue, id, control_api, dpluginInfo = None,TabManger = None):
        """
        Internal initialize function called by the PaPI framework;

        :param CoreQueue: Queue used to send messages to the Core.
        :param pluginQueue: Queue which is used by the PaPI framework to send messages to this plugins.
        :param id: The internal plugin ID.
        :param control_api: Access to the control_api provided by the PaPI framework.
        :param dpluginInfo: Meta information about this plugin.
        :param TabManger: The tab mananger.
        :return:
        """
        super(base_visual, self)._papi_init()
        self._Core_event_queue__ = CoreQueue
        self.__plugin_queue__ = pluginQueue
        self.__id__ = id
        self.control_api = control_api
        self._dplugin_info = dpluginInfo
        self.TabManager = TabManger
        self.movable = True

    def _starting_sequence(self, config=None):
        """
        Internal start function called by the PaPI framework;

        :param config:
        :return:
        """
        self._config = config
        # --------------------------------

        # get needed data from config
        size_re = re.compile(r'([0-9]+)')
        self.window_size = size_re.findall(self._config['size']['value'])
        self.window_pos = size_re.findall(self._config['position']['value'])

        self.window_name = self._config['name']['value']

        self._set_window_for_internal_usage(QMdiSubWindow())
        return self._start_plugin_base()

    def _start_plugin_base(self):
        """
        Needs to be implemented by plugin base class

        :return:
        """
        raise NotImplementedError("Please Implement this method")

    def _get_configuration_base(self):
        """
        Returns the basic configuration for this plugin base.

        :return:
        """
        config = {
            'size': {
                'value': "(300,300)",
                'regex': '\(([0-9]+),([0-9]+)\)',
                'advanced': '1',
                'tooltip': 'Determine size: (height,width)'
            },
            'position': {
                'value': "(0,0)",
                'regex': '\(([0-9]+),([0-9]+)\)',
                'advanced': '1',
                'tooltip': 'Determine position: (x,y)'
            },
            'name': {
                'value': 'VisualPlugin',
                'tooltip': 'Used for window title'
            },
            'tab': {
                'value': 'Tab',
                'tooltip': 'Used for tabs'
            },
            'maximized' : {
                'value' : '0',
                'type' : 'bool',
                'advanced' : '1',
                'tooltip' : 'Set true to start plugin maximized',
                'display_text' : 'Start maximized'
            }
        }
        return config


    def _set_window_for_internal_usage(self, subwindow):
        """
        This function will take a subwindow and will prepare all his call back function to work within PaPI
        It will also set the window reference for later use.

        :param subwindow
        :type subwindow: QMdiSubWindow
        :return:
        """
        self._subWindow = subwindow
        self.original_resize_function = self._subWindow.resizeEvent
        self.original_move_function = self._subWindow.moveEvent
        self.original_mouse_move_function = self._subWindow.mouseMoveEvent

        self._subWindow.resizeEvent = self._window_resize
        self._subWindow.moveEvent = self._window_move


        self._subWindow.setWindowTitle(self.window_name)
        self._subWindow.resize(int(self.window_size[0]), int(self.window_size[1]))

    def pl_set_widget_for_internal_usage(self, widget):
        """
        Will take QWidget and will place it in the subwindow

        Gets called by plugin developer!

        :param widget: QWidget
        :type widget: QWidget
        :return:
        """
        self._widget = widget
        self._subWindow.setWidget(self._widget)


    def _window_move(self, event):
        """
        New callback function for movement of a subwindow.
        Will do some PaPI specific tasks and then call the original subwindow callback function.

        :param event:
        :return:
        """
        pos = self._subWindow.pos()

        x = pos.x()
        y = pos.y()
        self._config['position']['value'] = '(' + str(x) + ',' + str(y) + ')'
        self.original_move_function(event)


    def _window_resize(self, event):
        """
        New callback function for resizing of a subwindow.
        Will do some PaPI specific tasks and then call the original subwindow callback function.

        :param event:
        :return:
        """
        size = event.size()
        w = size.width()
        h = size.height()

        isMaximized = self._get_sub_window().isMaximized()

        if isMaximized:
            self._config['maximized']['value'] = '1'
        else:
            self._config['maximized']['value'] = '0'

        self._config['size']['value'] = '(' + str(w) + ',' + str(h) + ')'
        self.original_resize_function(event)

    def _window_mouse_move(self, event):
        """
        New callback function for mouse move of a subwindow.
        Will do some PaPI specific tasks and then call the original subwindow callback function.

        :param event:
        :return:
        """
        if self.movable:
            self.original_mouse_move_function(event)

    def _get_sub_window(self):
        """
        Getter method to get subwindow of plugin

        :return: QMdiSubWindow
        """
        return self._subWindow

    def pl_get_widget(self):
        """
        Getter method to get widget of plugin

        :return: QWidget
        """
        return self._widget

    def pl_create_control_context_menu(self):
        """
        This function will create the general PaPI Control context menu to be used in Plugins.

        :return: QMenu
        """

        ctrlMenu = QMenu("Control")

        del_action = QAction('Close plugin',self._widget)
        del_action.triggered.connect(self._ctlrMenu_exit)

        pause_action = QAction('Pause plugin',self._widget)
        pause_action.triggered.connect(self._ctlrMenu_pause)

        resume_action = QAction('Resume plugin',self._widget)
        resume_action.triggered.connect(self._ctlrMenu_resume)

        subMenu_action = QAction('Open Signal Manager',self._widget)
        #subMenu_action.triggered.connect(self._ctlrMenu_resume)

        tabs = list(self.TabManager.get_tabs_by_uname().keys())
        if len(tabs) > 1:
            tabMenu = ctrlMenu.addMenu('Move to tab')
            tab_entrys = []
            for t in tabs:
                if t != self._config['tab']['value']:
                    entry = QAction(t, self._widget)
                    entry.triggered.connect(lambda ignore, p=t: self._tabMenu_move_triggered(p))
                    tab_entrys.append(entry)
                    tabMenu.addAction(entry)

        ctrlMenu.addAction(subMenu_action)
        if self._get_type() == PLUGIN_VIP_IDENTIFIER:
           ctrlMenu.addAction(resume_action)
           ctrlMenu.addAction(pause_action)
        ctrlMenu.addAction(del_action)
        return ctrlMenu

    def _tabMenu_move_triggered(self, item):
        """
        This callback function gets called when the user clicked on the moveToTab action at the context menu.
        Will start the process of moving the plugin window to another tab

        :param item: TabName to be moved to
        :return:
        """
        pos = self._subWindow.pos()
        posX = pos.x()
        posY = pos.y()
        if self.TabManager.moveFromTo(self._config['tab']['value'], item, self._subWindow, posX=posX, posY=posY):
            self._config['tab']['value'] = item


    def _ctlrMenu_exit(self):
        """
        Callback function for context menu for closing plugins

        :return:
        """
        self.control_api.do_delete_plugin_uname(self._dplugin_info.uname)
        print(self._config['tab']['value'])

    def _ctlrMenu_pause(self):
        """
        Callback function for context menu for pausing plugins

        :return:
        """
        self.control_api.do_pause_plugin_by_uname(self._dplugin_info.uname)

    def _ctlrMenu_resume(self):
        """
        Callback function for context menu for resuming plugins

        :return:
        """
        self.control_api.do_resume_plugin_by_uname(self._dplugin_info.uname)

    def cb_new_parameter_info(self, dparameter_object):
        """
        Will be called to notify a plugin that a new parameter subscription was done and will give
        information about the init values
        :param dparameter_object: DParameter
        :return:
        """
        pass