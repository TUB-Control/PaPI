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
import pickle

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
                'value': 'papi/plugin/io/ORTD_UDP/DataSourceExample/ProtocollConfig.json',
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
        self.separate = int(config['SeparateSignals']['value'])

        # SOCK_DGRAM is the socket type to use for UDP sockets
        self.sock_parameter = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock_parameter.setblocking(1)

        # Load protocol config.
        path = config['Cfg_Path']['value']
        f = open(path, 'r')
        self.ProtocolConfig = json.load(f)

        self.Sources = self.ProtocolConfig['SourcesConfig']
        self.Parameters = self.ProtocolConfig['ParametersConfig']



        # For each group:: loop through all sources (=signals) in the group and register the signals
        # Register signals


        if self.separate == 1:

            self.blocks = {}

            # sort hash keys for usage in right order!
            keys = list(self.Sources.keys())
            #keys.sort()
            for key in keys:
                Source = self.Sources[key]
                block = DBlock('SourceGroup' + str(key))
                block.add_signal(DSignal(Source['SourceName']))
                self.blocks[int(key)] = block


            self.send_new_block_list(list(self.blocks.values()))

        else:
            self.block1 = DBlock('SourceGroup0')

            keys = list(self.Sources.keys())
            #keys.sort()
            for key in keys:
                Source = self.Sources[key]
                sig_name = Source['SourceName']
                self.block1.add_signal(DSignal(sig_name))



            #self.block1 = DBlock(None, 1, 2, 'SourceGroup0', names)
            self.send_new_block_list([self.block1])



        # Register parameters
        self.Parameter_List = []

        for Pid in self.Parameters:
            Para = self.Parameters[Pid]
            para_name = Para['ParameterName']
            val_count = Para['NValues']
            opt_object = OptionalObject(Pid, val_count)
            Parameter = DParameter('', para_name, 0, 0, OptionalObject=opt_object)
            self.Parameter_List.append(Parameter)

        self.send_new_parameter_list(self.Parameter_List)

        self.t = 0

        self.set_event_trigger_mode(True)

        self.sock_recv = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock_recv.bind((self.HOST, self.SOURCE_PORT))
        self.sock_recv.settimeout(1)

        self.thread_goOn = True
        self.lock = threading.Lock()
        # self.thread = threading.Thread(target=self.thread_execute, args=(self.HOST, self.SOURCE_PORT) )
        self.thread = threading.Thread(target=self.thread_execute)
        self.thread.start()

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

            # check if thread should go on
            self.lock.acquire()
            goOn = self.thread_goOn
            self.lock.release()
        # Thread ended
        self.sock_recv.close()

    def execute(self, Data=None, block_name=None):
        raise Exception('Should not be called!')

    def set_parameter(self, name, value):
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