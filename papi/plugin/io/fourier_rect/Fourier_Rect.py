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

from papi.plugin.plugin_base import plugin_base
from papi.PapiEvent import PapiEvent
import time
import math
import numpy

__author__ = 'knuths'


class Fourier_Rect(plugin_base):
    max_approx = 23
    amax = 1
    def start_init(self):
        self.t = 0
        self.amax = Fourier_Rect.amax
        self.amplitude = 1
        self.max_approx = Fourier_Rect.max_approx
        self.freq = 1

        return True

    def pause(self):
        pass


    def resume(self):
        pass

    def execute(self):
        vec = numpy.zeros(self.amax* ( self.max_approx + 1) )

        for i in range(self.amax):
                vec[i] = self.t
                pre_value = 0
                for k in range(1, self.max_approx + 1):
                    vec[i+self.amax*k] = 4*self.amplitude / math.pi * math.sin((2*k - 1)*math.pi*self.freq*self.t)/(2*k - 1) + pre_value
                    pre_value = vec[i+self.amax*k]

                self.t += 0.02

        self.__shared_memory__[:]=vec
        event = PapiEvent(self.__id__, 0, 'data_event', 'new_data', vec)
        self._Core_event_queue__.put(event)

        time.sleep(0.02 * self.amax)

    def set_parameter(self):
        pass

    def quit(self):
        print('Fourier_Rect: will quit')

    def get_output_sizes(self):
        return [1, int( Fourier_Rect.amax*(Fourier_Rect.max_approx + 1) / 2) ]

    def get_type(self):
        return 'IOP'
