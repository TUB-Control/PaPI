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

#from papi.plugin.plugin_base import plugin_base

from papi.plugin.base_classes.iop_base import iop_base

from papi.data.DPlugin import DBlock
from papi.data.DParameter import DParameter

import threading

import time
import numpy
import os

import socket
import pickle

import struct
import json


class ORTD_UDP(iop_base):

    def get_plugin_configuration(self):
        config = {
        'address': {
                'value': '127.0.0.1'
            },
        'port': {
                'value': '20001'
        }

        }

        return config

    def start_init(self, config=None):
        self.t = 0
        

        print(['Fourier: process id: ',os.getpid()] )

        # open UDP
        ip = config['address']['value']
        port = int(config['port']['value'])
        self.HOST = ip
        self.PORT = port

        # SOCK_DGRAM is the socket type to use for UDP sockets
        self.sock2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock2.setblocking(1)
        
        # Load protocol config. TODO: Transfer this using UDP
        f = open('plugin/io/ORTD_UDP/DataSourceExample/ProtocollConfig.json', 'r')
        self.ProtocolConfig = json.load(f)
        
        self.Sources = self.ProtocolConfig['SourcesConfig']
        self.Parameters = self.ProtocolConfig['ParametersConfig']
        
        # loop through all groups and create a block for each; each group yields in its own assigned block
        # TODO
        
        
        # For each group:: loop through all sources (=signals) in the group and register the signals
        # Register signals
        names = ['t']
        #names.append('Testsignal')
        
        index = 0
        
        for Sid in self.Sources:
            Source = self.Sources[Sid]
            print(str(index) + " ) Source " + Source['SourceName'] + " vector length = " + Source['NValues_send'])
            names.append( Source['SourceName'] )
            index = index + 1

        self.block1 = DBlock(None,1,2,'SourceFrq1',names)
        self.send_new_block_list([self.block1])


        
        # Register parameters TODO: read list of parameters from self.Parameters
        self.para_1 = DParameter('', 'Par1', 0.01, [0,2],1)
        
        self.send_new_parameter_list([self.para_1])



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
                rev = self.sock.recv(1600)
                #rev = str.encode(rev_)
                #print("Got data" + str(len(rev)) )
            except socket.error:
                pass
            else:
                
                # unpack header
                SenderId, Counter, SourceId = struct.unpack_from('<iii', rev)
                
                if SourceId == -1:
                    # unpack group ID
                    GroupId = struct.unpack_from('<i', rev, 3*4)[0]
                    
                    #print("finishing group #" + str(GroupId) )
                    pass
                    # flush data to papi
                
                else:
                    # Received a data packet
                    
                    # Lookup the Source behind the given SourceId
                    Source = self.Sources[str(SourceId)]
                    NValues = Source['NValues_send']
                
                    #print("Got something from source " + Source['SourceName'] + " vector length = " + NValues)

                    #self.send_new_data([self.t], [   [val1]   ], 'SourceFrq1')

                    # Read NVales from the received packet (TODO)
                    val1 = struct.unpack_from('<d', rev, 3*4)[0]
                    #print(val1)
                
                    # send only if source zero (REMOVE and store all values for all sources into a structure)
                    if SourceId == 0:
                        
                    
                        vec = numpy.zeros((2,1))
                        
                        vec[0,0] = self.t
                        vec[1,0] = val1
                            
                        self.t += 0.1

                        self.send_new_data([self.t], [[val1]], 'SourceFrq1')
            
                
                #   for Sid in Sources:
                #
                #   Sid_ = int(Sid)
                #   print("investigating Source "+ str(Sid_) )
                #
                #   if SourceId == Sid_:
                #       #if SourceId == 0:
                #       #print(Counter)
                #       print(val1)
                #
                #       SrcCfg = self.ProtocolConfig['SourcesConfig'][str(Sid)]
                #
                #       print("Got something from source " + SrcCfg['SourceName'] + " vector length = " + SrcCfg['NValues_send'])
                #
                #       # send only if source zero
                #       if Sid_ == 0:
                #           vec = numpy.zeros((2,1))
                #
                #           vec[0,0] = self.t
                #           vec[1,0] = val1
                #
                #           self.t += 0.1
                #
                #           self.send_new_data(vec,'SourceFrq1')
            



            
            
            
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
        data = struct.pack('<iiid', 12, Counter, ParameterId, float(value))
        
        self.sock2.sendto(data, (self.HOST, self.PORT) )
        print("sent")
        print(data)
        

    def quit(self):
        print('Fourier_Rect: will quit')


    def plugin_meta_updated(self):
        pass