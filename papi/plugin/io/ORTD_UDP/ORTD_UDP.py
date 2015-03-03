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
(at your option) any later version.b

PaPI is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Lesser General Public License for more details.

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

import socket

import struct
import json


class OptionalObject(object):
    def __init__(self, ORTD_par_id, nvalues):
        self.ORTD_par_id = ORTD_par_id
        self.nvalues = nvalues


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
            }
        }

        return config

    def start_init(self, config=None):
        print('ORTD', self.__id__, ':process id', os.getpid())

        # open UDP
        self.HOST = config['address']['value']
        self.SOURCE_PORT = int(config['source_port']['value'])
        self.OUT_PORT = int(config['out_port']['value'])
        #self.separate = int(config['SeparateSignals']['value'])

        # SOCK_DGRAM is the socket type to use for UDP sockets
        self.sock_parameter = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock_parameter.setblocking(1)

        # Load protocol config.
        #path = config['Cfg_Path']['value']
        #f = open(path, 'r')
        #self.ProtocolConfig = json.load(f)
        #self.Sources = self.ProtocolConfig['SourcesConfig']
        #self.Parameters = self.ProtocolConfig['ParametersConfig']


        # For each group:: loop through all sources (=signals) in the group and register the signals
        # Register signals


        # if self.separate == 1:
        #
        #     self.blocks = {}
        #
        #     # sort hash keys for usage in right order!
        #     keys = list(self.Sources.keys())
        #     #keys.sort()
        #     for key in keys:
        #         Source = self.Sources[key]
        #         block = DBlock('SourceGroup' + str(key))
        #         block.add_signal(DSignal(Source['SourceName']))
        #         self.blocks[int(key)] = block
        #
        #
        #     self.send_new_block_list(list(self.blocks.values()))
        #
        # else:
        #     self.block1 = DBlock('SourceGroup0')
        #
        #     keys = list(self.Sources.keys())
        #     #keys.sort()
        #     for key in keys:
        #         Source = self.Sources[key]
        #         sig_name = Source['SourceName']
        #         self.block1.add_signal(DSignal(sig_name))





            # self.ControlBlock = DBlock('ControllerSignals')
            # self.ControlBlock.add_signal(DSignal('ControlSignalReset'))
            # self.ControlBlock.add_signal(DSignal('ControlSignalCreate'))
            # self.ControlBlock.add_signal(DSignal('ControlSignalSub'))
            # self.ControlBlock.add_signal(DSignal('ControllerSignalParameter'))
            # self.ControlBlock.add_signal(DSignal('ControllerSignalClose'))
            #
            # #self.block1 = DBlock(None, 1, 2, 'SourceGroup0', names)
            # self.send_new_block_list([self.block1, self.ControlBlock])

        # Register parameters
        #self.Parameter_List = []
        #
        # for Pid in self.Parameters:
        #     Para = self.Parameters[Pid]
        #     para_name = Para['ParameterName']
        #     val_count = Para['NValues']
        #     opt_object = OptionalObject(Pid, val_count)
        #     Parameter = DParameter(para_name, default=0, OptionalObject=opt_object)
        #     self.Parameter_List.append(Parameter)
        #
        # self.ControlParameter = DParameter('triggerConfiguration',default=0)
        # self.Parameter_List.append(self.ControlParameter)

        #self.send_new_parameter_list(self.Parameter_List)

        self.t = 0

        self.set_event_trigger_mode(True)

        self.sock_recv = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock_recv.bind((self.HOST, self.SOURCE_PORT))
        self.sock_recv.settimeout(1)

        self.thread_goOn = True
        self.lock = threading.Lock()
        self.thread = threading.Thread(target=self.thread_execute)
        self.thread.start()

        #self.process_received_package(None)



        return True

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
        goOn = True
        signal_values = {}
        while goOn:
            try:
                rev = self.sock_recv.recv(1600)
            except socket.timeout:
                # print('timeout')
                pass
            except socket.error:
                print('ORTD got socket error')
            else:
                self.process_received_package(rev)

            # check if thread should go on
            self.lock.acquire()
            goOn = self.thread_goOn
            self.lock.release()
        # Thread ended
        self.sock_recv.close()

    def process_received_package(self, rev):
        SenderId, Counter, SourceId = struct.unpack_from('<iii', rev)
        signal_values = {}
        print(SenderId, Counter, SourceId)

        if SourceId == -1:
            # data stream finished
            #self.process_finished_action(SourceId, rev, signal_values)
            #signal_values = {}
            pass

        if SourceId >= 0:
            # got data stream
            #self.process_data_stream(SourceId, rev, signal_values)
            pass

        if SourceId == -2:
            # new config in ORTD available
            # send trigger to get new config
            print('newcfg')
            Counter = 1
            data = struct.pack('<iiid', 12, Counter, int(-3), float(0))
            self.sock_parameter.sendto(data, (self.HOST, self.OUT_PORT))
            Counter = 1
            data = struct.pack('<iiid', 12, Counter, int(-3), float(0))
            self.sock_parameter.sendto(data, (self.HOST, self.OUT_PORT))

        if SourceId == -4:
            # new configItem
            # receive new config item and execute cfg in PaPI

            print(rev)
            print(len(rev))

            #SenderId, Counter, SourceId = struct.unpack_from('<iii', rev)
            unp = struct.unpack_from('<s',rev,17)[0]
            unp = str(unp)
            print(unp)

            i = 17
            unp = ''
            while i < len(rev):
                unp = unp + str(struct.unpack_from('<s',rev,i)[0])[2]


                i += 1

            print(unp)


            # config completely received
            # extract new configuration
            #cfg = {}
            #ORTDSources, ORTDParameters, plToCreate, \
            #plToClose, subscriptions, paraConnections = self.extract_config_elements(cfg)



    def update_parameter_list(self, ORTDParameter):
        oldParameterToDelete = self.Parameter_List

        newParameterList = []
        namesOfNewParameters = []
        for Pid in ORTDParameter:
            Para = ORTDParameter[Pid]
            para_name = Para['ParameterName']
            val_count = Para['NValues']
            opt_object = OptionalObject(Pid, val_count)
            Parameter = DParameter(para_name, default=0, OptionalObject=opt_object)
            newParameterList.append(Parameter)
            namesOfNewParameters.append(para_name)

        print(namesOfNewParameters)

        for parameter in oldParameterToDelete:
            print(parameter.name)
            if parameter.name in namesOfNewParameters:
                oldParameterToDelete.remove(parameter)

        return newParameterList, oldParameterToDelete

    def update_block_list(self,ORTDSources):
        return
        self.block1 = DBlock('SourceGroup0')

        keys = list(self.Sources.keys())
        #keys.sort()
        for key in keys:
            Source = self.Sources[key]
            sig_name = Source['SourceName']
            self.block1.add_signal(DSignal(sig_name))



    def process_data_stream(self, SourceId, rev, signal_values):
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

            signal_values[SourceId] = val
        else:
            print('ORTD_PLUGIN - '+self.dplugin_info.uname+': received data with an unknown id ('+str(SourceId)+')')

    def process_finished_action(self, SourceId, rev, signal_values):
        if SourceId == -1:
            # unpack group ID
            # GroupId = struct.unpack_from('<i', rev, 3 * 4)[0]
            self.t += 1.0

            keys = list(signal_values.keys())
            keys.sort()                    # REMARK: Die liste keys nur einmal sortieren; bei initialisierung

            if self.separate == 1:
                for key in keys:
                    # signals_to_send.append(signal_values[key])
                    Source = self.Sources[str(key)]
                    NValues = int(Source['NValues_send'])
                    n = len(signal_values[key])
                    t = np.linspace(self.t, self.t + 1 - 1 / NValues, NValues)
                    # flush data to papi
                    sig_name = self.Sources[str(key)]['SourceName']
                    self.send_new_data(self.blocks[key].name, t, {sig_name:signal_values[key]})
            else:
                signals_to_send = {}
                for key in keys:
                    sig_name = self.Sources[str(key)]['SourceName']
                    signals_to_send[sig_name] = signal_values[key]

                self.send_new_data('SourceGroup0', [self.t], signals_to_send )

    def thread_executeBackUP(self):
        goOn = True

        signal_values = {}
        while goOn:
            try:
                rev = self.sock_recv.recv(1600)
            except socket.timeout:
                # print('timeout')
                pass
            except socket.error:
                print('ORTD got socket error')
            else:
                # unpack header
                SenderId, Counter, SourceId = struct.unpack_from('<iii', rev)
                if SourceId == -1:
                    # unpack group ID
                    GroupId = struct.unpack_from('<i', rev, 3 * 4)[0]
                    self.t += 1.0

                    keys = list(signal_values.keys())
                    keys.sort()                           # REMARK: Die liste keys nur einmal sortieren; bei initialisierung

                    if self.separate == 1:
                        for key in keys:
                            # signals_to_send.append(signal_values[key])
                            Source = self.Sources[str(key)]
                            NValues = int(Source['NValues_send'])
                            n = len(signal_values[key])
                            t = np.linspace(self.t, self.t + 1 - 1 / NValues, NValues)
                            # flush data to papi
                            sig_name = self.Sources[str(key)]['SourceName']
                            self.send_new_data(self.blocks[key].name, t, {sig_name:signal_values[key]})
                    else:
                        signals_to_send = {}
                        for key in keys:
                            sig_name = self.Sources[str(key)]['SourceName']
                            signals_to_send[sig_name] = signal_values[key]

                        self.send_new_data('SourceGroup0', [self.t], signals_to_send )

                    signal_values = {}
                else:
                    # Received a data packet
                    # Lookup the Source behind the given SourceId
                    if str(SourceId) in self.Sources:
                        Source = self.Sources[str(SourceId)]
                        NValues = int(Source['NValues_send'])

                        # Read NVales from the received packet
                        val = []
                        for i in range(NValues):
                            # TODO: why try except?
                            try:
                                val.append(struct.unpack_from('<d', rev, 3 * 4 + i * 8)[0])
                            except:
                                val.append(0)

                        signal_values[SourceId] = val
                    else:
                        print('ORTD_PLUGIN - '+self.dplugin_info.uname+': received data with an unknown id ('+str(SourceId)+')')

            # check if thread should go on
            self.lock.acquire()
            goOn = self.thread_goOn
            self.lock.release()
        # Thread ended
        self.sock_recv.close()

    def execute(self, Data=None, block_name=None):
        raise Exception('Should not be called!')

    def set_parameter(self, name, value):
        if name == 'triggerConfiguration':
            if value == '1':
                cfg, subs, para, close = self.plconf()
                self.send_new_data('ControllerSignals', [1], {'ControlSignalReset':0,
                                                              'ControlSignalCreate':cfg,
                                                              'ControlSignalSub':subs,
                                                              'ControllerSignalParameter':para,
                                                              'ControllerSignalClose':close})
            if value == '2':
                self.send_new_data('ControllerSignals', [1], {'ControlSignalReset': 1,
                                                              'ControlSignalCreate':None,
                                                              'ControlSignalSub':None,
                                                              'ControllerSignalParameter':None,
                                                              'ControllerSignalClose':None})

        else:
            for para in self.Parameter_List:
                if para.name == name:
                    Pid = para.OptionalObject.ORTD_par_id
                    Counter = 111
                    data = struct.pack('<iiid', 12, Counter, int(Pid), float(value))
                    self.sock_parameter.sendto(data, (self.HOST, self.OUT_PORT))

    def quit(self):
        self.lock.acquire()
        self.thread_goOn = False
        self.lock.release()
        self.thread.join()
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
        ORTDSources = {
    "0" : { "SourceName" : "X" , "NValues_send" : "1", "datatype" : "257"  } ,
    "1" : { "SourceName" : "V" , "NValues_send" : "1", "datatype" : "257"  } }
        ORTDParameters = {
    "0" : { "ParameterName" : "Oscillator input" , "NValues" : "1", "datatype" : "257"  } ,
    "1" : { "ParameterName" : "A vectorial parameter" , "NValues" : "10", "datatype" : "257"  } ,
    "2" : { "ParameterName" : "Test" , "NValues" : "2", "datatype" : "257"  }  }

        if 'PaPIConfig' in configuration:
            if 'ToCreate' in configuration['PaPIConfig']:
                plToCreate = configuration['PaPIConfig']['ToCreate']

            if 'ToSub' in configuration['PaPIConfig']:
                subscriptions = configuration['PaPIConfig']['ToSub']

            if 'ToControl' in configuration['PaPIConfig']:
                paraConnections = configuration['PaPIConfig']['ToControl']

            if 'ToClose' in configuration['PaPIConfig']:
                plToClose = configuration['PaPIConfig']['ToClose']

        if 'SourcesConfig' in configuration:
            ORTDSources = configuration['SourcesConfig']

        if 'ParametersConfig' in configuration:
            ORTDParameters = configuration['ParametersConfig']

        return ORTDSources, ORTDParameters, plToCreate, plToClose, subscriptions, paraConnections


