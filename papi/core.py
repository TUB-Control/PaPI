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

version = '0.1'

from papi.plugin.plot import Plot


class Core:


    def init(foo, bar=True):
        """
        Function used to initialize PaPI.

        :param foo: used to foo
        :type foo: String
        :param bar: used to bar
        :type bar: bool
        :rtype bool:
        """

        print("initialize PaPI - Plugin based Process Interaction")

        plot = Plot('SuperPlot')
        plot.max(4)


        print(plot.name)
        print(plot.description)

        return True


    def create(foo, bar=True):
        """
        Function used to create something.

        :param foo: used to foo
        :type foo: String
        :param bar: used to bar
        :type bar: bool
        :rtype bool:
        """

        print("initialize PaPI - Plugin based Process Interaction")
        return True

