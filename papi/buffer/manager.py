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
from papi.ConsoleLog import ConsoleLog
import numpy


class Manager:
    header_size = 3

    def __init__(self, shared_array):
        self.__groups = {}
        self.__shared_array = shared_array
        self.msg_lvl = 2
        self.__debugLevel__ = 1
        self.__debug_var = ''
        self.log = ConsoleLog(self.msg_lvl,'BufferManager: ')

        i = -1
        state = 'attributes'
        bg = None

        group_id = 1

        while i < len(shared_array)-1:
            i += 1

            # Found new group
            if state == 'attributes':
                bg = Group()
                bg.size = shared_array[i]
                bg.offset = i
                bg.id = group_id
                group_id += 1

                bg.count = shared_array[i+1]
                bg.position = shared_array[i+2]
                bg.position_reader = bg.position
                state = 'vectors'

            if state == 'vectors':
                i += int(bg.size*bg.count) + 2

                self.__groups[bg.id] = bg
                bg = None
                state = 'attributes'

    def get_all_groups(self):
        return self.__groups

    @staticmethod
    def get_shared_array(desc):
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

        shared_array = Array('d', array_size, lock=True)

        next_offset = 0

        for i in range(len(desc)):

            count_vector = desc[i][0]
            freq = desc[i][1]
            current_offset = next_offset
            pos_s = current_offset + 0
            pos_c = current_offset + 1
            pos_p = current_offset + 2

            shared_array[pos_s] = freq * 10
            shared_array[pos_c] = count_vector
            shared_array[pos_p] = 0

            next_offset = current_offset + 10 * count_vector * freq + 3

        return shared_array

    def add_data(self, bg_id, data):
        """

        :param bg_id:
        :param data:
        :return:
        """

        if bg_id in self.__groups:
            bg = self.__groups[bg_id]
        else:
            #unknown buffer group
            return False

        self.__check_for_position_change(bg)

        if len(data) != bg.count:
            #more/less elements to write than it has to
            return False

        for i in range(len(data)):
            ele = data[i]
            write_index = int(bg.offset + 3 + (i * bg.size) + bg.position)
            self.__shared_array[write_index] = ele

        bg.position += 1
        if not bg.position % bg.size:
            bg.position = 0

        return True

    def get_data(self, bg_id):
        """

        :param buffer_group:
        :return []:
        """

        bg = None

        # is there a group with this id?
        if bg_id in self.__groups:
            bg = self.__groups[bg_id]
        else:
            return None

        self.__check_for_position_change(bg)

        # are there already new data?

        #if bg.position_reader <

        data = numpy.zeros(bg.count)

        for i in range(int(bg.count)):
            read_index = int(bg.offset + 3 + i*bg.size + bg.position_reader)
            data[i] = self.__shared_array[read_index]

        bg.position_reader += 1
        if not bg.position_reader % bg.size:
            bg.position_reader = 0

        return data

    def get_all_data(self, buffer_group):
        """

        :param buffer_group:
        :return:
        """

        pass

    def __check_for_position_change(self, bg):

        pass