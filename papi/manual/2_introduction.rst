Introduction
============

PaPI stands for Plugin based Process Interaction.

The idea of PaPI was to create a program which can visualize data from
external processes by using a plugin based architecture. The main
development reason for PaPI was to replace QRtaiLab.

PaPI's architecture should try to utilize the power of multi-processor
systems by using more than just one core. While the choice of using
Python as programming language leads to a slightly slower execution
speed, it allows a fast and easy development of new plugins.

Architecture
----------

We divided PaPI in three main parts: \* PaPI Core \* PaPI GUI \* Plugin
processes

.. figure:: _static/introduction/PaPIStructureWithArrows.png
   :alt: 

Due to the fact that the PaPI Core was realized in python, simple
multi-threading is not improving the performance (see python global
interpreter lock). That is why PaPI is using a message based
communication over multiple processes to increase performance.

Please note that process boundaries result in separated memory of the
parts.

The PaPI Core will create and manage a database with all open plugins
and the data routes.

New plugins that generate data will send them to the PaPI Core. The core
will do a look up in the routing table and redirect the message if there
is a subscriber. For processes to get messages, they need to subscribe
signals of PaPI plugins.

PaPI Plugins
============

Types
-----

PaPI divided the plugin structure in 4 types of plugins: \* IO
Plugin(IOP): Input-Output Plugins, runs in separate process, generates
new data for PaPI, e.g. UDP Receiver, ORTD

-  DP Plugin(DPP): Data Processing Plugins, runs in separate process,
   process data in PaPI, get data from PapI, generate new data for PaPI,
   e.g. adding signals

-  VI Plugin(VIP): Visual Plugin, runs in GUI process, used to display
   data, e.g. Plot

-  PC Plugin(PCP): Parameter Control Plugin, runs in GUI process, used
   to be a control element for setting paramter of other plugins, e.g.
   Slider

Signal, Blocks and Parameters
-----------------------------

A PaPI Plugin can offer several signals to PaPI for other plugins to
use. Each signal is owned by a signal block. A block in PaPI is a
collection of signals that will be always synchronized. One could say
that all signals of one block have the same sample time for PaPI and are
send united. That means that signals of one block are always synchronous
in their samples but two different blocks cannot be easily related to
each other in respect to their samples.

One Plugin can offer multiple blocks and every block can offer an
arbitrary number of signals.

Additionally to blocks and signals, plugins can offer parameters to
PaPI. Parameter can be changed using the GUI or PCPs.

Plugin Architecture
-------------------

PaPI uses a flag based plugin interaction. That means that plugins that
want to be integrated in PaPI need to implement a list of callback
functions. These callback functions will be called by PaPI to use the
plugin. There are some functions that must be implemented and some
functions that are optional.

Mandatory to implement are: \* ``start_init(self, config=None)`` [for
IOP/DPP], ``initiate_layer_0(self, config=None)`` [for VIP/PCP] \*
``execute(self, Data=None, block_name = None, plugin_uname = None)`` \*
``quit(self)``

These three functions defines the core functionality of a plugin. To see
more detailed information on how to create a plugin, refer to: `Design
guide plugin <DesignPlugin>`__

Plugin init
~~~~~~~~~~~

When creating a plugin the function start\_init\ *layer*\ 0 will be
called. These functions can be used to do all basic initialization
needed for the plugin to run, e.g. open widgets or open network
connections. It is mandatory that this function returns true at the end
otherwise the plugin will not be started! One important part of the init
method is to define the signals this plugin will offer to PaPI.

This function should in simple cases also be used to create parameters,
blocks and signals.

plugin execution
~~~~~~~~~~~~~~~~

When a plugin is started the normal operation loop will call the execute
function of a block. That means all the execution logic of a plugin
needs to be integrated in the execute function. It is important to note
that the execute function is not allowed to block. When a blocking
functionality is needed one can achieve that by using a thread. In this
function new data can be sent to PaPI using a PaPI function.

plugin quit
~~~~~~~~~~~

When a plugins is deleted, stopped or PaPI will end operation, the
``quit()`` function will be called to enable the plugin developer to
clean things up, e.g. to close network connections or file handlers.

Additional functions
~~~~~~~~~~~~~~~~~~~~

For additional functions and deeper understanding or programming
examples, please take a look at `Design guide plugin <DesignPlugin>`__