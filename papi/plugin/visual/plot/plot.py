#!/usr/bin/python3
#-*- coding: latin-1 -*-

"""

"""

from papi.plugin.visual_base import visual_base
from papi.PapiEvent import PapiEvent
import time
__author__ = 'knuths'


class Plot(visual_base):

    def start_init(self):
        pass

    def pause(self):
        pass


    def resume(self):
        pass

    def execute(self,Data):
        #print(Data)

        l = len(Data)

        t = Data[0:l/2]
        y = Data[l/2:l]

        self.add_data(t, y)

        self.update()

    def set_parameter(self):
        pass

    def get_type(self):
        return "ViP"

    def get_output_sizes(self):
        return [0,0]

    def start_init(self):
        pass

    def quit(self):
        print('Plot: will quit')