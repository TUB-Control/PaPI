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
<Stefan Ruppin
"""



from PyQt5.QtWebKitWidgets import QWebView
from PyQt5 import QtCore
from papi.plugin.base_classes.vip_base import vip_base

class HTMLViewer(vip_base):
    def cb_initialize_plugin(self):

        # ---------------------------
        # Read configuration
        # ---------------------------
        self.config = self.pl_get_current_config_ref()
        content = self.config['content']['value']
        isUrl   = self.config['isUrl']['value']



        # --------------------------------
        # Create Widget
        # --------------------------------
        self.WebView = QWebView()


        # This call is important, because the background structure needs to know the used widget!
        # In the background the qmidiwindow will becreated and the widget will be added
        self.pl_set_widget_for_internal_usage( self.WebView )
        print(isUrl)
        if isUrl == '1':
            url = QtCore.QUrl(content)
            self.WebView.load(url)
        else:
            self.WebView.setHtml(content)
        self.WebView.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.WebView.customContextMenuRequested.connect(self.show_context_menu)

        return True

    def show_context_menu(self, pos):
        gloPos = self.WebView.mapToGlobal(pos)
        self.cmenu = self.pl_create_control_context_menu()
        self.cmenu.exec_(gloPos)

    def cb_pause(self):
        # will be called, when plugin gets paused
        # can be used to get plugin in a defined state before pause
        # e.a.
        pass

    def cb_resume(self):
        # will be called when plugin gets resumed
        # can be used to wake up the plugin from defined pause state
        # e.a. reopen communication ports, files etc.
        pass

    def cb_execute(self, Data=None, block_name = None, plugin_uname = None):
        # Do main work here!
        # If this plugin is an IOP plugin, then there will be no Data parameter because it wont get data
        # If this plugin is a DPP, then it will get Data with data

        # param: Data is a Data hash and block_name is the block_name of Data origin
        # Data is a hash, so use ist like:  Data[CORE_TIME_SIGNAL] = [t1, t2, ...] where CORE_TIME_SIGNAL is a signal_name
        # hash signal_name: value

        # Data could have multiple types stored in it e.a. Data['d1'] = int, Data['d2'] = []

        pass

    def cb_set_parameter(self, name, value):
        # attetion: value is a string and need to be processed !
        # if name == 'irgendeinParameter':
        #   do that .... with value
        pass

    def cb_quit(self):
        # do something before plugin will close, e.a. close connections ...
        pass


    def cb_get_plugin_configuration(self):
        #
        # Implement a own part of the config
        # config is a hash of hass object
        # config_parameter_name : {}
        # config[config_parameter_name]['value']  NEEDS TO BE IMPLEMENTED
        # configs can be marked as advanced for create dialog
        # http://utilitymill.com/utility/Regex_For_Range

        config = {
            "content": {
                'value': """<p> Insert your html code here </p>""",
                'display_text' : 'HTML Content',
                'advanced' : 'HTLM',
                'tooltip' : 'Plain html code to be displayed'
            },
            "isUrl": {
                'value': "0",
                'display_text': "Content==Url?",
                'tooltip': "Set to 1 if the content is an url that should be loaded",
                'advanced' : 'HTML'
            },
        }

        return config

    def cb_plugin_meta_updated(self):
        """
        Whenever the meta information is updated this function is called (if implemented).

        :return:
        """

        #dplugin_info = self.dplugin_info
        pass
