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

import numpy as np

class BufferManager:
    header_size = 3
    def __init__(self):
        pass

    @staticmethod
    def get_array_size(desc :np.array ):

        dim =desc.shape[0]

        print(dim)
        return
        array_size = 0

        count_buffer_groups = len(desc)

        array_size += count_buffer_groups * BufferManager.header_size;

        if desc[0][0] == None:
            return None


        for i in range(len(desc)):
            count_vector = desc[i][0]
            freq = desc[i][1]
            array_size += count_vector * freq * 10

        return array_size