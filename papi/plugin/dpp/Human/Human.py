#!/usr/bin/python3
#-*- coding: utf-8 -*-

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
Mirjana Ruppel
"""



# basic import for block and parameter structure
from papi.data.DPlugin import DBlock
from papi.data.DParameter import DParameter
from papi.data.DSignal import DSignal
from papi.plugin.base_classes.dpp_base import dpp_base
import papi.constants as pc

import tornado.ioloop
import tornado.web
import tornado.websocket
import tornado.template
import tornado.tcpserver
import threading
import multiprocessing

import time
import os
import http.server
import socketserver

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

class HumanRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):

        if self.path == '/':
            parent = 'papi/plugin/dpp/Human'
            self.path += parent
        return http.server.SimpleHTTPRequestHandler.do_GET(self)

# Main Plugin
class Human(dpp_base):

    def cb_initialize_plugin(self):

        # Plugin is triggered by arrival of data
        self.pl_set_event_trigger_mode(True)
        self.config = self.pl_get_current_config_ref()
        # Read Configuration

        self.Up_w_Id = self.config['quat_upperarm_w']['value']
        self.Up_x_Id = self.config['quat_upperarm_x']['value']
        self.Up_y_Id = self.config['quat_upperarm_y']['value']
        self.Up_z_Id = self.config['quat_upperarm_z']['value']

        self.Fo_w_Id = self.config['quat_forearm_w']['value']
        self.Fo_x_Id = self.config['quat_forearm_x']['value']
        self.Fo_y_Id = self.config['quat_forearm_y']['value']
        self.Fo_z_Id = self.config['quat_forearm_z']['value']

        self.http_port = int(self.config['http_port']['value'])

        self.Angle_Data_Up_w = 0
        self.Angle_Data_Up_x = 0
        self.Angle_Data_Up_y = 0
        self.Angle_Data_Up_z = 0

        # Quaternion for forearm
        self.Angle_Data_Fo_w = 0
        self.Angle_Data_Fo_x = 0
        self.Angle_Data_Fo_y = 0
        self.Angle_Data_Fo_z = 0

        self.Angle_Data = [self.Angle_Data_Up_w, self.Angle_Data_Up_x,
                           self.Angle_Data_Up_y, self.Angle_Data_Up_z,
                           self.Angle_Data_Fo_w, self.Angle_Data_Fo_x,
                           self.Angle_Data_Fo_y, self.Angle_Data_Fo_z]

        # Initialize and start a thread
        self.thread_goOn = True
        self.lock = threading.Lock()
        self.thread = threading.Thread(target=self.thread_execute)
        self.thread.start()
        
        # Initialize a variable to store the data 
        #self.Angle_Data = 0

        # Start simple web server


        Handler = HumanRequestHandler

        self.httpd = socketserver.TCPServer(("", self.http_port), Handler)

        print("serving at port", self.http_port)

        self.thread_http = threading.Thread(target=self.thread_http)
        self.thread_http.start()

        # Return init success
        return True

    def cb_pause(self):
        # Will be called, when plugin gets paused
        pass

    def cb_resume(self):
        # Will be called when plugin gets resumed
        pass

    def cb_execute(self, Data=None, block_name = None, plugin_uname = None):

        # IMPORTANT: The identification names have to be the same as written in RTmain.sce!


        # if 'quat_upperarm_w' in Data and 'quat_upperarm_x' in Data and 'quat_upperarm_y' in Data \
        #     and 'quat_upperarm_z' in Data and 'quat_forearm_w' in Data and 'quat_forearm_x' in Data \
        #     and 'quat_forearm_y' in Data and 'quat_forearm_z' in Data:
        #
        #     # Quaternion for upper arm
        #     self.Angle_Data_Up_w = Data['quat_upperarm_w'][0]
        #     self.Angle_Data_Up_x = Data['quat_upperarm_x'][0]
        #     self.Angle_Data_Up_y = Data['quat_upperarm_y'][0]
        #     self.Angle_Data_Up_z = Data['quat_upperarm_z'][0]
        #
        #     # Quaternion for forearm
        #     self.Angle_Data_Fo_w = Data['quat_forearm_w'][0]
        #     self.Angle_Data_Fo_x = Data['quat_forearm_x'][0]
        #     self.Angle_Data_Fo_y = Data['quat_forearm_y'][0]
        #     self.Angle_Data_Fo_z = Data['quat_forearm_z'][0]
        #
        #     # Be sure the order is equal to the order used in index.html!
        #     self.Angle_Data = [self.Angle_Data_Up_w, self.Angle_Data_Up_x,
        #                        self.Angle_Data_Up_y, self.Angle_Data_Up_z,
        #                        self.Angle_Data_Fo_w, self.Angle_Data_Fo_x,
        #                        self.Angle_Data_Fo_y, self.Angle_Data_Fo_z]



        if self.Fo_w_Id in Data:
            self.Angle_Data_Fo_w = Data[self.Fo_w_Id][0]

        if self.Fo_x_Id in Data:
            self.Angle_Data_Fo_x = Data[self.Fo_x_Id][0]

        if self.Fo_y_Id in Data:
            self.Angle_Data_Fo_y = Data[self.Fo_y_Id][0]

        if self.Fo_z_Id in Data:
            self.Angle_Data_Fo_z = Data[self.Fo_z_Id][0]


        if self.Up_w_Id in Data:
            self.Angle_Data_Up_w = Data[self.Up_w_Id][0]

        if self.Up_x_Id in Data:
            self.Angle_Data_Up_x = Data[self.Up_x_Id][0]

        if self.Up_y_Id in Data:
            self.Angle_Data_Up_y = Data[self.Up_y_Id][0]

        if self.Up_z_Id in Data:
            self.Angle_Data_Up_z = Data[self.Up_z_Id][0]

        #
        # Be sure the order is equal to the order used in index.html!
        self.Angle_Data = [self.Angle_Data_Up_w, self.Angle_Data_Up_x,
                           self.Angle_Data_Up_y, self.Angle_Data_Up_z,
                           self.Angle_Data_Fo_w, self.Angle_Data_Fo_x,
                           self.Angle_Data_Fo_y, self.Angle_Data_Fo_z]


    def cb_set_parameter(self, name, value):
        pass

    def cb_quit(self):
        #TODO: self.thread.join()

        self.thread_goOn = False
        self.httpd.shutdown()
        self.thread_http.join()

        pass


    def cb_get_plugin_configuration(self):
        config = {
            "quat_upperarm_w": {
                'value': 'quat_upperarm_w'
            },
            "quat_upperarm_x": {
                'value': 'quat_upperarm_x'
            },
            "quat_upperarm_y": {
                'value': 'quat_upperarm_y'
            },
            "quat_upperarm_z": {
                'value': 'quat_upperarm_z'
            },
            "quat_forearm_w": {
                'value': 'quat_forearm_w'
            },
            "quat_forearm_x": {
                'value': 'quat_forearm_x'
            },
            "quat_forearm_y": {
                'value': 'quat_forearm_y'
            },
            "quat_forearm_z": {
                'value': 'quat_forearm_z'
            },
            "http_port": {
                'value': '8080',
                'regex' : pc.REGEX_SINGLE_INT
            }
        }
        return config

    def cb_plugin_meta_updated(self):
        pass


    def thread_http(self):

        self.httpd.serve_forever()

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
