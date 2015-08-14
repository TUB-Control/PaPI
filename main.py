#!/usr/bin/python3
# -*- coding: latin-1 -*-

"""
Copyright (C) 2014 Technische Universität Berlin,
Fakultät IV - Elektrotechnik und Informatik,
Fachgebiet Regelungssysteme,
Einsteinufer 17, D-10587 Berlin, Germany

This file is part of PaPI.

PaPI is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

PaPI is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with PaPI.  If not, see <http://www.gnu.org/licenses/>.

Contributors
Sven Knuth
"""

__author__ = 'control'

from papi.core              import Core
from papi.gui.default.main   import GUI, run_gui_in_own_process

import papi.constants as pc

import platform
import sys
import os
import argparse
parser = argparse.ArgumentParser(epilog="Documentation can be found here: http://github.com/TUB-Control/PaPI")

parser.add_argument("-c", "--config",  dest = "config", default = "", help="Configuration file loaded after startup.")
parser.add_argument("-u", "--user_config", dest = "user_config", default='0', help="Loads a user specific configuration")
parser.add_argument("-v", "--version", dest = "version", action="store_true", default=False, help="Prints current PaPI version.")
parser.add_argument("-d", "--debug_level", dest = "debug_level", default='0', help="Sets debug level.")

args = parser.parse_args()

def start_PaPI(args=None):
    print('Plattform of the system running PaPI: ' + platform.system())

    if args:
        if args.version:
            print("Current PaPI version: " + pc.CORE_PAPI_VERSION)
            return

    # start on PaPI on system running Linux
    if platform.system() == 'Linux':
        path = os.path.dirname(pc.PAPI_USER_CFG)
        if not os.path.exists(path):
            os.mkdir(path)

        core = Core(run_gui_in_own_process, is_parent=True, use_gui=True, args=args)
        core.run()
        return

    # start on PaPI on system running Windows
    if platform.system() == 'Windows':
        print('Windows port is NOT ready')
        raise Exception('Windows is not supported yet')
        return

    # start on PaPI on system running Mac OS X
    if platform.system() == 'Darwin':
        path = os.path.dirname(pc.PAPI_USER_CFG)
        if not os.path.exists(path):
            os.mkdir(path)
        core = Core(run_gui_in_own_process, is_parent=True, use_gui=True, args=args)
        core.run()
        return
        # app = QApplication(sys.argv)
        # gui = GUI(is_parent=True)
        # gui.run()
        # gui.show()
        # app.exec_()
        # return

    raise Exception('Seems like the os you are using is not supported by PaPI')

if __name__ == '__main__':

    sys.exit(start_PaPI(args=args))
