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

You should have received a copy of the GNU Lesser General Public License
along with PaPI.  If not, see <http://www.gnu.org/licenses/>.

Contributors
Sven Knuth
"""



from papi.plugin.base_classes.iop_base import iop_base
from papi.data.DPlugin import DBlock
from papi.data.DSignal import DSignal

import time
import numpy
import os

import socket
import pickle


class Fourier_Rect(iop_base):
    max_approx = 20
    amax = 20


    def start_init(self, config=None):

        self.t = 0
        self.amax = Fourier_Rect.amax
        self.amplitude = 1
        self.max_approx = Fourier_Rect.max_approx
        self.freq = 1
        self.vec = numpy.ones(self.amax* ( self.max_approx + 1) )


        print(['Fourier: process id: ',os.getpid()] )


        self.HOST = config['host']['value']
        self.PORT = int( config['port']['value'] )

        # SOCK_DGRAM is the socket type to use for UDP sockets
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setblocking(0)


        self.block1 = DBlock('Rectangle')
        for i in range(1,self.max_approx):
            self.block1.add_signal(DSignal('rect'+str(i)))

        self.send_new_block_list([self.block1])

        return True

    def pause(self):
        pass

    def resume(self):
        pass

    def execute(self, Data=None, block_name = None, plugin_uname = None):
        # amount of elements per vector: self.amax
        # amount of vectors : self.max_approx+1
        vec = numpy.zeros( (self.max_approx,  (self.amax) ))

#        print("Amax: " + str(self.amax+1))
#        print("Max_Approx"  + str(self.max_approx))

        # As you can see, there is no connect() call; UDP has no connections.
        # Instead, data is directly sent to the recipient via sendto().
        self.sock.sendto(b'GET', (self.HOST, self.PORT) )


        try:
            received = self.sock.recv(60000)
        except socket.error:
            pass
        else:
            data = pickle.loads(received)

            vech = {}
            t = data[0*self.amax:(0+1)*self.amax]

            for i in range(self.max_approx):
                vech['rect'+str(i)] = data[i*self.amax:(i+1)*self.amax]

            self.send_new_data('Rectangle', t, vech)

        time.sleep(0.001*self.amax )

    def set_parameter(self, name, value):
        pass

    def quit(self):
        print('Fourier_Rect: will quit')

    def get_plugin_configuration(self):
        config = {
            'name': {
                    'value': 'Fourier'
                    },
            'host': {
                     'value': "130.149.155.73",
                     'regex': '\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}',
                     'advanced' : '1'
            },
            'port': {
                    'value': 9999,
                    'regex': '\d{1,5}',
                     'advanced' : '1'
            }}
        return config

    def plugin_meta_updated(self):
        pass

