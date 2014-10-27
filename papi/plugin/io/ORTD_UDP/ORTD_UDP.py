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

Contributors
Sven Knuth
"""

__author__ = 'CK'

from papi.plugin.plugin_base import plugin_base
from papi.data.DPlugin import DBlock
from papi.data.DParameter import DParameter

import threading

import time
import numpy
import os

import socket
import pickle

import struct


class ORTD_UDP(plugin_base):
    max_approx = 300
    amax = 20
    
    def start_init(self, config=None):
        self.t = 0
        
        
        #        self.amax = Fourier_Rect_MOD.amax
        #        self.amplitude = 1
        #        self.max_approx = Fourier_Rect_MOD.max_approx
        #        self.freq = 1
        
        
        # self.vec = numpy.zeros( 2,1 )

        print(['Fourier: process id: ',os.getpid()] )

        # open UDP
        self.HOST = "127.0.0.1"
        self.PORT = 20001
        # SOCK_DGRAM is the socket type to use for UDP sockets
        self.sock2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock2.setblocking(1)
        
        # Register parameters
        self.para_1 = DParameter('', 'Par1', 0.01, [0,2],1)
        
        self.send_new_parameter_list([self.para_1])


        # Register signals
        names = ['t']
        names.append('Testsignal')

        self.block1 = DBlock(None,1,2,'SourceFrq1',names)
        self.send_new_block_list([self.block1])

        self.set_event_trigger_mode(True)

        thread = threading.Thread(target=self.thread_execute, args=(self.HOST,self.PORT) )
        thread.start()

        return True

    def pause(self):
        pass

    def resume(self):
        pass

    def thread_execute(self,host,port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind( ('127.0.0.1', 20000) )
        
        self.sock.setblocking(1)
        #vec = numpy.zeros( (self.max_approx,  (self.amax) ))

        while True:
            #   self.sock.sendto(b'GET', (self.HOST, self.PORT) )

#            try:
#                received = self.sock.recv(60000)
#            except socket.error:
#                pass
#            else:
#                data = pickle.loads(received)


            
            try:
                #print("Waiting for data")
                rev = self.sock.recv(20)
                #rev = str.encode(rev_)
                print("Got data")
            except socket.error:
                pass
            else:
                SenderId, Counter, SourceId, val1 = struct.unpack('<iiid', rev)
                
                if SourceId == 0:
                    print(Counter)
                    print(val1)
                
                    vec = numpy.zeros((2,1))
    
                    vec[0,0] = self.t
                    vec[1,0] = val1
        
                    self.t += 0.1

                    self.send_new_data(vec,'SourceFrq1')
            
            
            
            
            #print("Hallo")
            

            #time.sleep(0.1)


    def execute(self, Data=None, block_name = None):
        print("EXECUTE FUNC")
        pass

    def set_parameter(self, name, value):
        print("Setting parameter " + name + " ")
        print(value)
        
        ParameterId = 0
        Counter = 111;
        data = struct.pack('<iiid', 12, Counter, ParameterId, value)
        
        self.sock2.sendto(data, (self.HOST, self.PORT) )
        print("sent")
        print(data)
        

    def quit(self):
        print('Fourier_Rect: will quit')

#    def get_output_sizes(self):
#        return [1, int( Fourier_Rect_MOD.amax*(Fourier_Rect_MOD.max_approx + 1) ) ]

    def get_type(self):
        return 'IOP'
