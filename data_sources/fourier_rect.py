#!/usr/bin/python3
# -*- coding: latin-1 -*-

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

import socketserver

import time
import math
import numpy
import os
import pickle


class MyUDPHandler(socketserver.BaseRequestHandler):
    """
    This class works similar to the TCP handler class, except that
    self.request consists of a pair of data and client socket, and since
    there is no connection the client address must be given explicitly
    when sending data back via sendto().
    """

    max_approx = 20
    amax = 20

    t = 0

    def start_init(self):


        print(['Fourier: process id: ',os.getpid()] )
        return True

    def calculate_data(self):

        vec = numpy.ones(self.amax* ( self.max_approx + 1) )

        amax = MyUDPHandler.amax
        amplitude = 1
        max_approx = MyUDPHandler.max_approx
        freq = 1

        for i in range(amax):
            vec[i] = MyUDPHandler.t
            for k in range(1, max_approx + 1):
                vec[i+amax*k] = 4*amplitude / math.pi * math.sin((2*k - 1)*math.pi*freq*MyUDPHandler.t)/(2*k - 1)
            MyUDPHandler.t += 0.001

        return vec

    def handle(self):
        data = self.request[0]
        socket = self.request[1]
#        print("{} wrote:".format(self.client_address[0]))


        vec = self.calculate_data()

        socket.sendto(pickle.dumps(vec), self.client_address)


if __name__ == "__main__":
    HOST, PORT = "0.0.0.0", 9999
    server = socketserver.UDPServer((HOST, PORT), MyUDPHandler)
    server.t = 0
    server.serve_forever()
