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

from papi.buffer.group import Group
from multiprocessing import Array

class Manager:
    header_size = 3

    def __init__(self, shared_array):
        self.groups = {}
        i = -1
        state = 'size'
        bg = None

        while i < len(shared_array):
            i += 1
            # Found new group
            if state == 'size':
                bg = Group()
                bg.size = shared_array[i]
                bg.offset = i
                state = 'count'
                continue

            if state == 'count':
                bg.count = shared_array[i]
                state = 'position'
                continue

            if state == 'position':
                bg.position = shared_array[i]
                state = 'vectors'
                continue

            if state == 'vectors':
                i = bg.size*bg.count
                self.groups[bg.id] = bg
                bg = None
                state == 'size'
                continue


    def get_all_groups(self):
        return self.groups

    @staticmethod
    def get_array_size(desc):
        """

        :param desc:
        :return:
        :rtype Array:
        """

        array_size = 0
        count_buffer_groups = len(desc)
        array_size += count_buffer_groups * Manager.header_size

        if desc[0][0] is None:
            return None

        for i in range(len(desc)):
            count_vector = desc[i][0]
            freq = desc[i][1]
            array_size += count_vector * freq * 10

        shared_Arr = Array('d',array_size,lock=True)

        for i in range(len(desc)):
            count_vector = desc[i][0]
            freq = desc[i][1]
            shared_Arr[i * count_vector + 0] = freq * 10
            shared_Arr[i * count_vector + 1] = count_vector

        return shared_Arr

    def add_data(self, buffer_group, data):
        """

        :param buffer_group:
        :param data:
        :return:
        """


        pass

    def get_data(self, buffer_group):
        """

        :param buffer_group:
        :return:
        """
        pass
