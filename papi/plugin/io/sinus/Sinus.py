#!/usr/bin/python3
#-*- coding: latin-1 -*-

"""

"""

from papi.plugin.plugin_base import plugin_base
from papi.PapiEvent import PapiEvent
import time
import math
import numpy

__author__ = 'knuths'


class Sinus(plugin_base):

    def start_init(self):
        self.t = 0
        self.amax = 50
        return True

    def pause(self):
        pass


    def resume(self):
        pass

    def execute(self):
        vec = numpy.zeros(self.amax*2)
        for i in range(self.amax):
                vec[i] = self.t
                vec[i+self.amax] = math.sin(2*math.pi*0.01*self.t)
                self.t += 0.1


        event = PapiEvent(self.__id__,0,'data_event','new_data',vec)
        self._Core_event_queue__.put(event)
        time.sleep(0.02)

    def set_parameter(self):
        pass

    def quit(self):
        print('Sinus: will quit')

    def get_type(self):
        return 'IOP'

    def get_output_sizes(self):
        return [2,50]
