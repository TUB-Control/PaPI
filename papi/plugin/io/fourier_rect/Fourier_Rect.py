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

__author__ = 'knuths'

from papi.plugin.plugin_base import plugin_base
from papi.data.DPlugin import DBlock
from papi.data.DParameter import DParameter

import time
import numpy
import os

import socket
import pickle


class Fourier_Rect(plugin_base):
    max_approx = 300
    amax = 20
    def start_init(self):
        self.t = 0
        self.amax = Fourier_Rect.amax
        self.amplitude = 1
        self.max_approx = Fourier_Rect.max_approx
        self.freq = 1
        self.vec = numpy.ones(self.amax* ( self.max_approx + 1) )

        print(['Fourier: process id: ',os.getpid()] )


        self.HOST = "130.149.155.73"
        self.PORT = 9999
        # SOCK_DGRAM is the socket type to use for UDP sockets
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setblocking(0)


        names = []
        for i in range(0,self.max_approx):
            names.append('rect'+str(i))

        self.block1 = DBlock(None,300,10,'Rect1',names)
        self.send_new_block_list([self.block1])

        return True

    def pause(self):
        pass

    def resume(self):
        pass

    def execute(self):
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
            self.send_new_data(data,'Rect1')
        data = pickle.loads(received)


        for i in range(self.max_approx):
            vec[i, 0:self.amax] = data[i*self.amax:(i+1)*self.amax]

        self.send_new_data(vec,'Rect1')

        time.sleep(0.001*self.amax )

    def set_parameter(self):
        pass

    def quit(self):
        print('Fourier_Rect: will quit')

    def get_output_sizes(self):
        return [1, int( Fourier_Rect.amax*(Fourier_Rect.max_approx + 1) ) ]

    def get_type(self):
        return 'IOP'
