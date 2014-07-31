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
        return True

    def pause(self):
        pass


    def resume(self):
        pass

    def execute(self):
        vec = numpy.zeros(20)
        for i in range(10):
                vec[i] = self.t
                vec[i+10] = math.sin(2*math.pi*0.01*self.t)
                self.t += 0.1

        self.__shared_memory__=vec
        event = PapiEvent(self.__id__,0,'data_event','new_data','')
        self._Core_event_queue__.put(event)

    def set_parameter(self):
        pass

    def quit(self):
        print('Sinus: will quit')

    def get_type(self):
        return 'IOP'