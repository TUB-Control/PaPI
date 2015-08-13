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
(at your option) any later version.b

PaPI is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with PaPI.  If not, see <http://www.gnu.org/licenses/>.

Contributors
Christian Klauer
Stefan Ruppin




IDEAS
-----

- The ProtocolConfig.json may contain information about how to place indivual elements in the GUI
- How to handle multiple instances and dynamically created datasources?
- Show a separated screen/page in the gui for each datasource; something like tabs?
- initial Configuration and later updates via UDP




"""

__author__ = 'CK'

from papi.plugin.base_classes.iop_base import iop_base

from papi.data.DPlugin import DBlock
from papi.data.DSignal import DSignal
from papi.data.DParameter import DParameter

import numpy as np

import threading

import os
import sys

import socket
import ast
import struct
import json
import time
import pickle
import base64

from threading import Timer
from socketIO_client import SocketIO, LoggingNamespace




class OptionalObject(object):
    def __init__(self, ORTD_par_id, nvalues):
        self.ORTD_par_id = ORTD_par_id
        self.nvalues = nvalues
        self.sendOnReceivePort = True
        self.UseSocketIO = True



class ORTD_UDP(iop_base):
    def get_plugin_configuration(self):
        config = {
            'address': {
                'value': '127.0.0.1',
                'advanced': '1'
            },
            'source_port': {
                'value': '20000',
                'advanced': '1'
            },
            'out_port': {
                'value': '20001',
                'advanced': '1'
            },
            'Cfg_Path': {
                'value': '/home/control/PycharmProjects/PaPI/data_sources/ORTD/DataSourceExample/ProtocollConfig.json',
                'type': 'file',
                'advanced': '0'
            },
            'SeparateSignals': {
                'value': '0',
                'advanced': '1'
            },
            'SendOnReceivePort': {
                'value': '0',    # NOTE: chnage back to 0
                'advanced': '1',
                'display_text': 'Use same port for send and receive'
            },
            "UseSocketIO" : {
                'value' : '0',   # NOTE: change back to 0 !!
                'advanced' : '1',
                'tooltip' : 'Use socket.io connection to node.js target-server',
                'type' : 'bool'
            },
            'socketio_port': {
                'value': '8091',
                'advanced': '1'
            },
            "OnlyInitialConfig" : {
                'value' :'0',
                'tooltip' : 'Use only first configuration, ignore further configurations.',
                'type' : 'bool'
            }
        }

        return config

    def start_init(self, config=None):
        print('ORTD', self.__id__, ':process id', os.getpid())

        # open UDP
        self.HOST = config['address']['value']
        self.SOURCE_PORT = int(config['source_port']['value'])
        self.OUT_PORT = int(config['out_port']['value'])

        self.LOCALBIND_HOST = '' # config['source_address']['value']     #CK



        self.sendOnReceivePort = True if config['SendOnReceivePort']['value'] == '1' else False
        self.UseSocketIO = True if config['UseSocketIO']['value'] == '1' else False

        if self.UseSocketIO:
            self.SocketIOPort = int(config['socketio_port']['value'])


        #self.sendOnReceivePort = True  # NOTE: remove this
        #self.UseSocketIO = True  # NOTE: remove this


        print ("SendOnReceivePort = ", self.sendOnReceivePort)
        print ("UseSocketIO = ", self.UseSocketIO)

        self.PAPI_SIMULINK_BLOCK = False

        self.separate = int(config['SeparateSignals']['value'])

        self.onlyInitialConfig = config['OnlyInitialConfig']['value'] == '1'
        self.hasInitialConfig = False

        if (not self.sendOnReceivePort):
            # SOCK_DGRAM is the socket type to use for UDP sockets
            self.sock_parameter = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sock_parameter.setblocking(1)



        self.ControlBlock = DBlock('ControllerSignals')
        self.ControlBlock.add_signal(DSignal('ControlSignalReset'))
        self.ControlBlock.add_signal(DSignal('ControlSignalCreate'))
        self.ControlBlock.add_signal(DSignal('ControlSignalSub'))
        self.ControlBlock.add_signal(DSignal('ControllerSignalParameter'))
        self.ControlBlock.add_signal(DSignal('ControllerSignalClose'))
        self.ControlBlock.add_signal(DSignal('ActiveTab'))
        self.send_new_block_list([self.ControlBlock])


        self.t = 0

        self.set_event_trigger_mode(True)

        self.sock_recv = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        if (not self.sendOnReceivePort):
            self.sock_recv.bind((self.LOCALBIND_HOST, self.SOURCE_PORT)) # CK
            print("ORTD_UDP-plugin listening on: ", self.LOCALBIND_HOST, ":", self.SOURCE_PORT)     #CK
        else:
            print ("---- Using client UDP mode (not binding to a port) ----")


        self.sock_recv.settimeout(1)

        self.thread_goOn = True
        self.lock = threading.Lock()
        self.thread = threading.Thread(target=self.thread_execute)
        self.thread.start()

        if self.UseSocketIO:
            print ("Using socket.io connection on port", self.SocketIOPort)

            self.thread_socket_goOn = True
            self.thread_socketio = threading.Thread(target=self.thread_socketio_execute)

        self.blocks = {}
        self.Sources = {}

        self.parameters = {}

        self.signal_values = {}

        self.block_id = 0

        self.config_complete = False
        self.config_buffer = {}

        self.timer = Timer(3,self.callback_timeout_timer)
        self.timer_active = False



        self.ConsoleBlock = DBlock('ConsoleSignals')
        self.ConsoleBlock.add_signal(DSignal('MainSignal'))
        self.send_new_block_list([self.ConsoleBlock])

        self.consoleIn      = DParameter('consoleIn',default='')
        self.send_new_parameter_list([self.consoleIn])

        if self.UseSocketIO:
            self.thread_socketio.start()

        return True

    def SIO_callback_SCISTOUT(self, data):
        # Got a chunk of data from a console interface in the target server
        self.sio_count += 1

        self.send_new_data(self.ConsoleBlock.name, [self.sio_count], {'MainSignal':data['Data']})

    def SIO_callback_PAPICONFIG(self, data):
        # Got a new PaPI plugin configuration in JSON-format via socket.io connection
        # currently the config is transmitted via ORTD packets that may also be encapsulated into socket.io
        # added 12.8.15, CK

        print ("Got a new config in JSON/socket.io format")
        print (data)

        self.check_and_process_cfg(data)

        # TODO: Test this

    def SIO_callback_ORTDPACKET(self, data):
        # Got an encapsulated packet from ORTD, not transfered via UDP but encapsulated within the socket.io connection
        #print ("Got data packet from ORTD via socket.io")
        #print (data)
        self.process_received_package(base64.b64decode(data))  # data must be a binary blob






    def thread_socketio_execute(self):
        #self.sio = SocketIO('localhost', 8091, LoggingNamespace)
        #self.sio.on('SCISTOUT',self.callback_SCISTOUT)

        with SocketIO(self.HOST, self.SocketIOPort, LoggingNamespace) as self.sio:
            self.sio.on('SCISTOUT',self.SIO_callback_SCISTOUT)
            self.sio.on('PAPICONFIG',self.SIO_callback_PAPICONFIG)
            self.sio.on('ORTDPACKET',self.SIO_callback_ORTDPACKET)

            self.sio_count = 0
            while self.thread_socket_goOn:
                self.sio.wait(seconds=1)



    def pause(self):
        self.lock.acquire()
        self.thread_goOn = False
        self.lock.release()
        self.thread.join()

    def resume(self):
        self.thread_goOn = True
        self.thread = threading.Thread(target=self.thread_execute, args=(self.HOST, self.SOURCE_PORT))
        self.thread.start()

    def thread_execute(self):
        time.sleep(1)
        self.request_new_config_from_ORTD()

        goOn = True
        newData = False
        signal_values = {}
        while goOn:
            try:
                if not self.sendOnReceivePort:
                    rev = self.sock_recv.recv(20000)  # not feasible for network connection other than loopback
                else:
                    #print ("---- Waiting for data ----")
                    rev, server = self.sock_recv.recvfrom(20000)  # not feasible for network connection other than loopback
                    #print ("---- got ----")
                    #print (rev)

            except socket.timeout:
                # print('timeout')
                newData = False

            except socket.error:
                print('ORTD got socket error')
            else:
               newData = True

            if newData:
               self.process_received_package(rev)

            # check if thread should go on
            self.lock.acquire()
            goOn = self.thread_goOn
            self.lock.release()
        # Thread ended
        self.sock_recv.close()

    def process_received_package(self, rev):
        SenderId, Counter, SourceId = struct.unpack_from('<iii', rev)

        if SourceId == -1 and len(self.blocks) > 0:
            # data stream finished
            self.process_finished_action(SourceId, rev)
            self.signal_values = {}

        if SourceId >= 0 and len(self.blocks) > 0:
            # got data stream
            self.process_data_stream(SourceId, rev)

        if SourceId == -2:
            # new config in ORTD available
            # send trigger to get new config
            self.request_new_config_from_ORTD()
            self.config_complete = False
            self.config_buffer = {}

        if SourceId == -100:
            self.PAPI_SIMULINK_BLOCK = True
            # got data stream from the PaPI-Simulink Block
            self.process_papi_data_stream(rev)
    
        if SourceId == -4:
            self.PAPI_SIMULINK_BLOCK = False
            # new configItem
            # print("Part of a new configuration");
            # receive new config item and execute cfg in PaPI

            # unpack package
            i = 16 # Offset: 4 ints
            unp = ''
            while i < len(rev):
                unp = unp + str(struct.unpack_from('<s',rev,i)[0])[2]
                i += 1

            self.config_buffer[int(Counter)] = unp

            # Check counter key series for holes
            counters = list(self.config_buffer.keys())
            counters.sort()
            i = 1
            config_file = ''

            self.config_complete = True
            for c in counters:
                if i == c:
                    config_file += self.config_buffer[c]
                    i += 1
                else:
                    self.config_complete = False
                    break

            if self.config_complete:
                if not self.check_and_process_cfg(config_file):
                    self.start_timeout_timer()
                else:
                    self.stop_timeout_timer()

            else:
                self.start_timeout_timer()


    def start_timeout_timer(self):
        if not self.timer_active:
            self.timer = Timer(3,self.callback_timeout_timer)
            self.timer.start()
            self.timer_active = True
        else:
            self.timer.cancel()
            self.timer = Timer(3,self.callback_timeout_timer)
            self.timer.start()

    def stop_timeout_timer(self):
        if self.timer_active:
            self.timer.cancel()
            self.timer_active = False

    def callback_timeout_timer(self):
        print('ORTD_PLUGIN: Config timeout, requesting a new config')
        self.timer_active = False

        self.config_buffer = {}
        self.request_new_config_from_ORTD()

    def request_new_config_from_ORTD(self):
        Counter = 1
        data = struct.pack('<iiid', 12, Counter, int(-3), float(0))

        if self.UseSocketIO:
            print ("Requesting config via socket.io")

            self.sio.emit('ORTDPACKET', base64.b64encode(data).decode('ascii') )
            # TODO test this

        else:

            if not self.sendOnReceivePort:
                self.sock_parameter.sendto(data, (self.HOST, self.OUT_PORT))
            else:
                self.sock_recv.sendto(data, (self.HOST, self.SOURCE_PORT))



    def check_and_process_cfg(self, config_file):
        try:
            # config completely received
            # extract new configuration
            cfg = json.loads(config_file)
            ORTDSources, ORTDParameters, plToCreate, \
            plToClose, subscriptions, paraConnections, activeTab = self.extract_config_elements(cfg)


            if self.hasInitialConfig and self.onlyInitialConfig:
                return True

            self.hasInitialConfig = True

            self.update_block_list(ORTDSources)
            self.update_parameter_list(ORTDParameters)

            self.process_papi_configuration(plToCreate, plToClose, subscriptions, paraConnections, activeTab)

            return True
        except ValueError as e:
            return False


    def process_papi_configuration(self, toCreate, toClose, subs, paraConnections, activeTab):

        self.send_new_data('ControllerSignals', [1], {'ControlSignalReset': 1,
                                                              'ControlSignalCreate':None,
                                                              'ControlSignalSub':None,
                                                              'ControllerSignalParameter':None,
                                                              'ControllerSignalClose':None,
                                                              'ActiveTab': None })

        self.send_new_data('ControllerSignals', [1], {'ControlSignalReset':0,
                                                              'ControlSignalCreate':toCreate,
                                                              'ControlSignalSub':subs,
                                                              'ControllerSignalParameter':paraConnections,
                                                              'ControllerSignalClose':toClose,
                                                              'ActiveTab': activeTab})

    def parse_json_stream(self,stream):
        decoder = json.JSONDecoder()
        while stream:
            obj, idx = decoder.raw_decode(stream)
            yield obj
            stream = stream[idx:].lstrip()

    def update_parameter_list(self, ORTDParameter):

        newList ={}

        for para_id in ORTDParameter:
            para_name = ORTDParameter[para_id]['ParameterName']
            if para_name in self.parameters:
                para_object = self.parameters.pop(para_name)
            else:
                val_count = int(ORTDParameter[para_id]['NValues'])
                opt_object = OptionalObject(para_id, val_count)

                if "initial_value" in ORTDParameter[para_id]:
                    val = ORTDParameter[para_id]['initial_value']
                    if val_count > 1:
                        val = val[1:-1]
                        init_value = list(map(float,val.split(',')))
                    else:
                        init_value = float(val)
                else:
                    init_value = 0

                para_object = DParameter(para_name, default=str(init_value), OptionalObject=opt_object)
                self.send_new_parameter_list([para_object])


            newList[para_name] = para_object

        toDeleteDict = self.parameters
        self.parameters = newList

        for par in toDeleteDict:
            self.send_delete_parameter(par)


    def update_block_list(self,ORTDSources):
        #self.block_id = self.block_id +1
        #newBlock = DBlock('SourceGroup'+str(self.block_id))
        #self.blocks['SourceGroup'+str(self.block_id)] = newBlock
        if 'SourceGroup0' in self.blocks:
            self.send_delete_block('SourceGroup0')
        newBlock = DBlock('SourceGroup0')
        self.blocks['SourceGroup0'] = newBlock
        self.Sources = ORTDSources
        keys = list(self.Sources.keys())
        for key in keys:
            Source = self.Sources[key]
            sig_name = Source['SourceName']
            newBlock.add_signal(DSignal(sig_name))

        self.send_new_block_list([newBlock])

        # Remove BLOCKS
        #if 'SourceGroup'+str(self.block_id-1) in self.blocks:
            #self.send_delete_block(self.blocks.pop('SourceGroup'+str(self.block_id-1)).name)

    def process_papi_data_stream(self, rev):

        timestamp = None

        offset = 4*4
        for i in range(len(self.Sources)):

            try:
                val = []
#                offset += i*(4+4+4)

                # Get current signal ID:

#                signal_id,data = struct.unpack_from('<id', rev, offset)
                signal_id, data = struct.unpack_from('<id', rev, offset)

                # print('Offset=' + str(offset))
                #
                # print('SignalID: ' + str(signal_id))
#                print('Data: ' + str(data))
                if str(signal_id) in self.Sources:

                    Source = self.Sources[str(signal_id)]
                    NValues = int(Source['NValues_send'])

                    # print("NValues : " +  str(NValues))

                    #print("Offset:" + str(offset))

                    offset += 4
                    for n in range(NValues):
                        # print('#Value=' + str(n))
                        # print('Offset=' + str(offset))
                        try:
                            data = struct.unpack_from('<d', rev, offset)[0]
                            # print('Data=' + str(data))

                            val.append(data)
                        except struct.error:
                            # print(sys.exc_info()[0])
                            # print('!!!! except !!!!')
                            val.append(0)

                        offset += 8

                    # print('Data: ' + str(val))

                    # if NValues > 1:
                    #     signal_id,data = struct.unpack_from('<id%sd' %NValues, rev, offset)
                    #     offset += (NValues-1)*(4+4)
                    if self.Sources[str(signal_id)]["SourceName"] == "time":
                            timestamp = val[0]

                    self.signal_values[signal_id] = val
                                
                #print("Signal: " + str(signal_id) + " Data: " + str(data)  );
            except struct.error:
                print(sys.exc_info()[0])
                print("Can't unpack.")
        self.process_finished_action(-1,None, timestamp)
    

    def process_data_stream(self, SourceId, rev):
        # Received a data packet
        # Lookup the Source behind the given SourceId
        if str(SourceId) in self.Sources:
            Source = self.Sources[str(SourceId)]
            NValues = int(Source['NValues_send'])

            # Read NVales from the received packet
            val = []
            for i in range(NValues):
                try:
                    val.append(struct.unpack_from('<d', rev, 3 * 4 + i * 8)[0])
                except:
                    val.append(0)

            self.signal_values[SourceId] = val

        else:
            print('ORTD_PLUGIN - '+self.dplugin_info.uname+': received data with an unknown id ('+str(SourceId)+')')

    def process_finished_action(self, SourceId, rev, timestamp=None):
        if SourceId == -1:
            # unpack group ID
            # GroupId = struct.unpack_from('<i', rev, 3 * 4)[0]
            self.t += 1.0

            keys = list(self.signal_values.keys())
            keys.sort()                    # REMARK: Die liste keys nur einmal sortieren; bei initialisierung

            signals_to_send = {}
            for key in keys:
                if str(key) in self.Sources:
                    sig_name = self.Sources[str(key)]['SourceName']
                    signals_to_send[sig_name] = self.signal_values[key]

            if len( list(self.blocks.keys()) ) >0:
                block = list(self.blocks.keys())[0]
                if len(self.blocks[block].signals) == len(signals_to_send):
                    if timestamp is None:
                        self.send_new_data(block, [self.t], signals_to_send )
                    else:
                        self.send_new_data(block, [timestamp], signals_to_send )

    def execute(self, Data=None, block_name = None, plugin_uname = None):
        raise Exception('Should not be called!')

    def set_parameter(self, name, value):
        if name in self.parameters:
            parameter = self.parameters[name]
            Pid = parameter.OptionalObject.ORTD_par_id
            Counter = 111
            if value is not None:
                data = None

                # get values in float from string

                valueCast = ast.literal_eval(value)
                # check is it is a list, if not, cast to list
                if not isinstance(valueCast,list):
                    valueCast = [valueCast]

                if self.PAPI_SIMULINK_BLOCK:
                    data = struct.pack('<iii%sd' %len(valueCast), 12, Counter, int(Pid),*valueCast)
                else:
                    data = struct.pack('<iii%sd' %len(valueCast), 12, Counter, int(Pid),*valueCast)

                #if isinstance(valueCast, list):
                    #data += struct.pack('%sd' %len(valueCast),*valueCast)
                #    for i in range(0,len(valueCast)):
                #        data += struct.pack('<d',valueCast[i])
                #else:
                #    data +=  struct.pack('d',float(value))


                if self.UseSocketIO:
                    print ("Setting parameter via socket.io")

                    self.sio.emit('ORTDPACKET', base64.b64encode(data).decode('ascii') )
                    # TODO test this

                else:

                    if not self.sendOnReceivePort:
                        self.sock_parameter.sendto(data, (self.HOST, self.OUT_PORT))
                    else:
                        self.sock_recv.sendto(data, (self.HOST, self.SOURCE_PORT))
        else:
            if name == 'consoleIn':
                self.sio.emit('ConsoleCommand', { 'ConsoleId' : '1' ,  'Data' : value  })


    def quit(self):
        self.lock.acquire()
        self.thread_goOn = False
        self.lock.release()
        self.thread.join()
        if not self.sendOnReceivePort:
            self.sock_parameter.close()
        print('ORTD-Plugin will quit')

    def plugin_meta_updated(self):
        pass

    def plconf(self):
        cfg   = {}
        subs  = {}
        paras = {}
        close = {}
        if 'PaPIConfig' in self.ProtocolConfig:
            if 'ToCreate' in self.ProtocolConfig['PaPIConfig']:
                cfg = self.ProtocolConfig['PaPIConfig']['ToCreate']
            if 'ToSub' in self.ProtocolConfig['PaPIConfig']:
                subs = self.ProtocolConfig['PaPIConfig']['ToSub']
            if 'ToControl' in self.ProtocolConfig['PaPIConfig']:
                paras = self.ProtocolConfig['PaPIConfig']['ToControl']
            if 'ToClose' in self.ProtocolConfig['PaPIConfig']:
                close = self.ProtocolConfig['PaPIConfig']['ToClose']
        return cfg, subs, paras, close

    def extract_config_elements(self, configuration):
        plToCreate   = {}
        subscriptions  = {}
        paraConnections = {}
        plToClose = {}
        ORTDSources = {}
        ORTDParameters = {}
        activeTab = 'PaPI-Tab'

        if 'PaPIConfig' in configuration:
            if 'ToCreate' in configuration['PaPIConfig']:
                plToCreate = configuration['PaPIConfig']['ToCreate']

            if 'ToSub' in configuration['PaPIConfig']:
                subscriptions = configuration['PaPIConfig']['ToSub']

            if 'ToControl' in configuration['PaPIConfig']:
                paraConnections = configuration['PaPIConfig']['ToControl']

            if 'ToClose' in configuration['PaPIConfig']:
                plToClose = configuration['PaPIConfig']['ToClose']

            if 'ActiveTab' in configuration['PaPIConfig']:
                activeTab = configuration['PaPIConfig']['tab']

        if 'SourcesConfig' in configuration:
            ORTDSources = configuration['SourcesConfig']

        if 'ParametersConfig' in configuration:
            ORTDParameters = configuration['ParametersConfig']

        return ORTDSources, ORTDParameters, plToCreate, plToClose, subscriptions, paraConnections, activeTab

