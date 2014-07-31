#!/usr/bin/python3
#-*- coding: latin-1 -*-

"""

"""

from papi.plugin.plugin_base import plugin_base
from papi.PapiEvent import PapiEvent
import time
__author__ = 'ruppins'

class TestPl1(plugin_base):

    def start_init(self):
        pass

    def pause(self):
        pass


    def resume(self):
        pass

    def execute(self):
        print('TestPL1: execute')
        time.sleep(1)

    def set_parameter(self):
        pass

    def quit(self):
        print('TestPL1: will quit')

    def get_type(self):
        return 'IOP'