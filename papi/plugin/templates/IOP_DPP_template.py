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
(at your option) any later version.

PaPI is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with PaPI.  If not, see <http://www.gnu.org/licenses/>.

Contributors:
<Stefan Ruppin, Sven Knuth
"""


# Default PaPI imports used to create a plugin!
# Please remember that this template will only show the default PaPI imports and not any imports of example lines of Code
from papi.data.DPlugin import DBlock                            # for creating Blocks
from papi.data.DSignal import DSignal                           # for signal creation
from papi.data.DParameter import DParameter                     # for Parameter creation
import papi.constants as pconst                                 # for PaPI constants like some Regex or Time Signal Name

# One of them is not needed!
# Delete the line when you decided for iop or dpp
from papi.plugin.base_classes.iop_base import iop_base          # Needed for a IOP Plugin
from papi.plugin.base_classes.dpp_base import dpp_base          # Needed for a IOP Plugin

# Template Class for a Plugin running in a separate process.
# A Plugin running in separate processes needs to inherent from iop_base or dpp_base!
# RENAME CLASS TO PLUGIN NAME
class IOP_DPP_template(iop_base):
    # OBLIGATORY function to implement!
    # Will initialize the plugin in context of PaPI and the plugin developer!
    def cb_initialize_plugin(self):
        # --------------------------------
        # Step 1: Read configuration items (startup cfg)
        # OPTIONAL
        # --------------------------------
        #  Please read the Documentation of pl_get_config_element() to understand what is happening here.
        #  e.g. a configuration item named 'offset' is read.
        offset = self.pl_get_config_element('offset')
        offset = float(offset) if offset is not None else 0

        # --------------------------------
        # Step 2:Define blocks for output signals and define signals of blocks!
        # OPTIONAL
        # --------------------------------
        # Here: block called CPU_LOAD with 2 signals for Core1 and Core2
        blockLoad = DBlock('CPU_LOAD')
        sig_core1 = DSignal('Load_C1')
        sig_core2 = DSignal('Load_C2')

        blockLoad.add_signal(sig_core1)
        blockLoad.add_signal(sig_core2)

        self.pl_send_new_block_list([blockLoad])

        # --------------------------------
        # Step 3: Define parameter that are offered to PaPI
        # OPTIONAL
        # Sub-Step 1: Create Parameter Object
        # Sub-Step 2: Send list of Parameter Objects created to PaPI
        # --------------------------------
        #   use self. to remember the parameter object in this class/context for own usage!
        #   e.g. parameter named parameterName1 is created!
        #   Refer to the Doc of DParameter to read about advanced usages!
        self. parameter1 = DParameter('parameterName1')
        self. parameter2 = DParameter('parameterName2')
        self.pl_send_new_parameter_list([self.parameter1, self.parameter1])

        # --------------------------------
        # Step 4: Set the plugin trigger mode
        # OPTIONAL
        # In most cases for IOP you will leave it default, for DPP you will set it to true
        # Default will mean, that PaPI will decide on it.
        # --------------------------------
        self.pl_set_event_trigger_mode('default')

        # --------------------------------
        # Step 5: Developer and Plugin specific configuration
        # OPTIONAL
        # --------------------------------

        # --------------------------------
        # Step 6: Return Value
        # OBLIGATORY
        # Return True if the everything is alright!
        # False will lead to PaPI not starting this Plugin!
        # --------------------------------
        return True

    # OBLIGATORY function to implement!
    # Will be called by PaPI before the Plugin will close!
    # This is a clean-up callback function!
    def cb_quit(self):
        # clean up!
        # e.g. close files or sockets, or free memory ....
        pass

    # OPTIONAL function to implement!
    # Will be called by PaPI whenever a signal arrived with this plugin as destination!
    # This is a callback function that will only need to be implemented if you want to react to signals (NOT PARAMETER)
    # For most of the plugins like plots or displays the main work of changing the visualisation will be done!
    def cb_execute(self, Data=None, block_name = None, plugin_uname = None):
        # Arguments of this function can be looked up in detail in the Doc.
        # Data: dict of data
        # block_name: name of the block the data belongs to   (SOURCE)
        # plugin_name: name of the plugin the data belongs to (SOURCE)
        # Data could have multiple types stored in it e.a. Data['d1'] = int, Data['d2'] = []

        # e.g. send data for a signal to PaPI, remember to always send all signals of a block in one step!
        self.pl_send_new_data('CPU_LOAD',time.time(), {'Load_C1': 0, 'Load_C2': 0} )


    # OPTIONAL function to implement!
    # Will be called by PaPI whenever a parameter of this plugin was changed!
    # This callback function enables the developer to react to these changes!
    def cb_set_parameter(self, name, value):
        # Attention: value is a string and need to be processed/casted !
        # e.g. react to change in parameter1, printing the value!
        if name == self.parameter1.name:
            print(value)

    # OPTIONAL function to implement!
    # All plugins have a plugin configuration that is defined by PaPI and extended by the plugin developer.
    # This function will represent the extended part of the configuration.
    # If it is not implemented, just the PaPI defined base configuration will be used, otherwise a merge will happen!
    # See Doc for details!
    # But remember: This cfg part should include all items addressed with pl_get_config_element()!
    def cb_get_plugin_configuration(self):
        # return has to be a dict of a special structure!
        # Info: online regex tool: http://utilitymill.com/utility/Regex_For_Range

        # e.g. for our offset configuration item
        ex_config = {
            'offset': {
                    'value': '0',
                    'tooltip': 'Used to offset displayed value',
                    'regex': '-?\d+(\.?\d+)?',
                    'advanced': '1'
            }
        }
        return ex_config

