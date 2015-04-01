#!/usr/bin/python3
#-*- coding: utf-8 -*-

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
Mirjana Ruppel
"""

__author__ = 'Mirjana'

# basic import for block and parameter structure
from papi.data.DPlugin import DBlock
from papi.data.DParameter import DParameter
from papi.data.DSignal import DSignal
from papi.plugin.base_classes.dpp_base import dpp_base

import tornado.ioloop
import tornado.web
import tornado.websocket
import tornado.template
import tornado.tcpserver
import threading
import multiprocessing

import time

# This class initializes a WebSocket to enable bidirectional communication between browser and server
class WSHandler(tornado.websocket.WebSocketHandler):

    # WebSockets don't use CORS headers and can bypass the usual same-origin policies
    # to accept cross-origin traffic, always return True
    def check_origin(self, origin):
        return True
      
    # Initialize the data that shall be sent
    def initialize(self, QuatData):
        self.QuatData = QuatData

    def open(self):
        print('Connection opened')
  
    # This function is called when a new WebSocket is opened
    def on_message(self, message):

    # index.html sends a message to the server when it is ready to render a new frame
        # the answer to this message is the current quaternion data received from the ORTD Plugin
        self.write_message(str(self.QuatData()).encode('utf-8'))


    # This function is called when the WebSocket is closed
    def on_close(self):
        print('Connection closed')

# Main Plugin
class Human(dpp_base):

    def start_init(self, config=None):

        # Plugin is triggered by arrival of data
        self.set_event_trigger_mode(True)

    # Initialize and start a thread
        self.thread_goOn = True
        self.lock = threading.Lock()
        self.thread = threading.Thread(target=self.thread_execute)
        self.thread.start()
        
        # Initialize a variable to store the data 
        self.Angle_Data = 0

        # Return init success
        return True

    def pause(self):
        # Will be called, when plugin gets paused
        pass

    def resume(self):
        # Will be called when plugin gets resumed
        pass

    def execute(self, Data=None, block_name = None, plugin_uname = None):

        # IMPORTANT: The identification names have to be the same as written in RTmain.sce!

        if 'quat_upperarm_w' in Data and 'quat_upperarm_x' in Data and 'quat_upperarm_y' in Data \
            and 'quat_upperarm_z' in Data and 'quat_forearm_w' in Data and 'quat_forearm_x' in Data \
            and 'quat_forearm_y' in Data and 'quat_forearm_z' in Data:

            # Quaternion for upper arm
            self.Angle_Data_Up_w = Data['quat_upperarm_w'][0]
            self.Angle_Data_Up_x = Data['quat_upperarm_x'][0]
            self.Angle_Data_Up_y = Data['quat_upperarm_y'][0]
            self.Angle_Data_Up_z = Data['quat_upperarm_z'][0]

            # Quaternion for forearm
            self.Angle_Data_Fo_w = Data['quat_forearm_w'][0]
            self.Angle_Data_Fo_x = Data['quat_forearm_x'][0]
            self.Angle_Data_Fo_y = Data['quat_forearm_y'][0]
            self.Angle_Data_Fo_z = Data['quat_forearm_z'][0]

            # Be sure the order is equal to the order used in index.html!
            self.Angle_Data = [self.Angle_Data_Up_w,self.Angle_Data_Up_x,
                               self.Angle_Data_Up_y,self.Angle_Data_Up_z,
                               self.Angle_Data_Fo_w, self.Angle_Data_Fo_x,
                               self.Angle_Data_Fo_y, self.Angle_Data_Fo_z]


    def set_parameter(self, name, value):
        pass

    def quit(self):
        #TODO: self.thread.join()
        pass


    def get_plugin_configuration(self):
        config = {}
        return config

    def plugin_meta_updated(self):
        pass




    def thread_execute(self):
        print('Start a thread')
        # Start a tornado web application in the thread 
        # tornado.web.Application() is a collection of request handlers that create a web application
        # Pass a list of regexp or request_class tuples
        application = tornado.web.Application([
            (r'/ws', WSHandler, {'QuatData': self.get_data} ),	# Pass quaternion data, so class WSHandler can process it
            (r"/(.*)", tornado.web.StaticFileHandler, {"path": "./resources"}),
        ])

        print('Application created successfully')
        
        # Port has to be the same as the WebSocket port in index.html
        application.listen(9999)
        
        print('Start IOLoop')
        # tornado.ioloop is an I/O event loop for non-blocking sockets
        # start the main ioloop
        tornado.ioloop.IOLoop.instance().start()
        print('IO Loop started successfully')


    def get_data(self):
        return self.Angle_Data
