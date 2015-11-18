PaPI v. 1.x
===========

Plugin based Process Interaction

Introduction
------------

PaPI is a tool to interact with real-time targets or sources for 
measured data. It provides a plugin-based framework that allows to 
read streaming data form targets and allows to set parameters.
Several plugins for data visualization (plots, bars, meters, html-animations ...)
as well as GUI-elements for entering parameters (textfields, sliders, ...).
User customized plugins can be easily created using a given Python-API.

Opening and closing of all GUI-elements can be controlled by real-time target
programs and hence it is possible to implement GUI-logic using state-machines
inside the target programs. Have a look at https://youtu.be/9B2BISXaPdo
to get an impression of what is currently possible.

PaPI spans across several processes to benefit form multi-core systems.

Installation
------------

Basic installation on Ubuntu 14.04 64Bit, using python 3.4

``sudo apt-get install git``

``sudo apt-get install python3.4 python3-numpy python3-pip``

``sudo apt-get install python3-pyqt5``

``sudo apt-get install python3-pyqt5.qtwebkit`` (just needed for the
HTMLViewer plugin) [optional]

``sudo apt-get install python3-pyqt5.qtsvg`` (just needed for the
export feature of the Plot plugin) [optional]

``sudo pip3 install socketio_client`` (required for ORTD_UDP) [optional]

``sudo pip3 install tornado`` (just needed for the Human plugin)
[optional]

``git clone https://github.com/TUB-Control/PaPI.git PaPI``

``cd PaPI``

``python3.4 main.py``

Tip: If python3.4 interpreter cannot find or locate the installed
packages (PyQt5 or numpy), please make sure that the right python
interpreter is called (in case there are multiple installed).

Real-time target systems currently supported
--------------------------------------------

  * OpenRTDynamics.sf.net
  * Simulink

Examples for both Frameworks are contained within: https://github.com/TUB-Control/PaPI/tree/development/data_sources

A demo video that shows how graphical interfaces you create using PaPI may look like: https://youtu.be/9B2BISXaPdo


Contribution
------------

To get started, sign the Contributor License Agreement.

Documentation
-------------

Sphinx doc on GitHub: https://tub-control.github.io/PaPI/

PaPI wiki on GitHub: https://github.com/TUB-Control/PaPI/wiki

Embedded Packages
-----------------

Yapsy 1.10.423 published under BSD-License,
http://yapsy.sourceforge.net/#license

pyqtgraph-0.9.11 [unreleased] published under MIT-License
https://github.com/pyqtgraph/pyqtgraph

JSONlab 1.1 published under BSD-License and GPLv3
https://github.com/fangq/jsonlab

Used icon-set
-------------

fatcow-hosting-icons-3.9.2, License:
http://creativecommons.org/licenses/by/3.0/us/, Provided by:
http://www.fatcow.com/
