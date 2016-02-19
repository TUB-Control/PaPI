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
(at your option) any later version.b

PaPI is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with PaPI.  If not, see <http://www.gnu.org/licenses/>.

Contributors
Stefan Ruppin
"""

from papi.plugin.base_classes.iop_base import iop_base
import time

class CPU_Load(iop_base):
    def cb_initialize_plugin(self):
        self.t = 0
        self.delta_t = 0.01

        # creates Block for CPU load
        block1 = self.pl_create_DBlock('CPUload')
        signal = self.pl_create_DSignal('load_in_percent')
        block1.add_signal(signal)
        self.pl_send_new_block_list([block1])

        # sets update interval
        self.INTERVAL = 0.1

        return True

    def cb_pause(self):
        pass

    def cb_resume(self):
        pass

    def cb_execute(self, Data=None, block_name = None, plugin_uname = None):
        # get load
        cpuload = self.getCpuLoad()
        # increment time stamp
        self.t += self.delta_t
        # send data to core
        self.pl_send_new_data('CPUload', [self.t*10], {'load_in_percent': [cpuload*100]})
        # wait
        time.sleep(self.delta_t)

    def cb_set_parameter(self, name, value):
        pass

    def cb_quit(self):
        pass

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

    def cb_plugin_meta_updated(self):
        pass

    def cb_get_plugin_configuration(self):
        return {}