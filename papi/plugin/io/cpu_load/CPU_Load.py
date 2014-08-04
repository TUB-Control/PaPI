#!/usr/bin/python3
#-*- coding: latin-1 -*-

"""

"""

from papi.plugin.plugin_base import plugin_base
from papi.PapiEvent import PapiEvent
import time
import math
import numpy
import time
__author__ = 'knuths'


class CPU_Load(plugin_base):
    INTERVAL = 0.1
    def start_init(self):
        self.t = 0
        return True

    def pause(self):
        pass


    def resume(self):
        pass

    def execute(self):
        vec = numpy.zeros(2)

        vec[0] = self.t
        vec[1] = self.getCpuLoad() * 100

        print(vec)
        self.t += 0.1

        event = PapiEvent(self.__id__,0,'data_event','new_data',vec)
        self._Core_event_queue__.put(event)
        time.sleep(0.04)

    def set_parameter(self):
        pass

    def quit(self):
        print('Sinus: will quit')

    def get_type(self):
        return 'IOP'

    def get_output_sizes(self):
        return [1,10]

    def getTimeList(self):
        """
        Fetches a list of time units the cpu has spent in various modes
        Detailed explanation at http://www.linuxhowtos.org/System/procstat.htm
        """
        cpuStats = open("/proc/stat", "r").readline()
        columns = cpuStats.replace("cpu", "").split(" ")
        return map(int, filter(None, columns))

    def deltaTime(self, interval):
        """
        Returns the difference of the cpu statistics returned by getTimeList
        that occurred in the given time delta
        """
        timeList1 = self.getTimeList()
        time.sleep(interval)
        timeList2 = self.getTimeList()
        return [(t2-t1) for t1, t2 in zip(timeList1, timeList2)]

    def getCpuLoad(self):
        """
        Returns the cpu load as a value from the interval [0.0, 1.0]
        """
        dt = list(self.deltaTime(self.INTERVAL))
        idle_time = float(dt[3])
        total_time = sum(dt)
        load = 1-(idle_time/total_time)
        return load


