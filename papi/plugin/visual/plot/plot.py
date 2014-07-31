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

    def execute(self):
        print('Sinus: execute')
        time.sleep(1)

    def set_parameter(self):
        pass

    def quit(self):
        print('Sinus: will quit')