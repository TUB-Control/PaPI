PaPI v. 1.0.0
==================

Plugin based Process Interaction

Introduction
------
PaPI is a tool to interact with data generating processes. It can be used to get data stream of experiments or devices
like oscilloscopes.

PaPI is based on a strong plugin architecture. Therefore it is easy to expand to new environments.

PaPi will make heavily use of multi-core systems.

Installation
------
Basic installation on Ubuntu 14.04 64Bit, using python 3.4

`sudo apt-get install git`

`sudo apt-get install python3.4 python3-numpy python3-pip`

`sudo apt-get install python3-pyqt5`

`sudo apt-get install python3-pyqt5.qtwebkit` (just needed for the HTMLViewer plugin) [optional]

`sudo apt-get installl python3-pyqt5.qtsvg` (just needed for the export feature of the Plot plugin) [optional]

`sudo pip3 install tornado` (just needed for the Human plugin) [optional]

`git clone https://github.com/TUB-Control/PaPI.git PaPI`

`cd PaPI`

`python3.4 main.py`

Tip:
If python3.4 interpreter cannot find or locate the installed packages (PyQt5 or numpy), please make sure that the right
python interpreter is called (in case there are multiple installed).

Contribution
------

To get started, <a href="https://www.clahub.com/agreements/TUB-Control/PaPI">sign the Contributor License Agreement</a>.

Documentation
------

Sphinx doc on GitHub: https://tub-control.github.io/PaPI/

PaPI wiki on GitHub: https://github.com/TUB-Control/PaPI/wiki

Embedded Packages
------

Yapsy 1.10.423 published under BSD-License, http://yapsy.sourceforge.net/#license

pyqtgraph-0.9.11 [unreleased] published under MIT-License

Used icon-set
------

fatcow-hosting-icons-3.9.2, License: http://creativecommons.org/licenses/by/3.0/us/, Provided by: http://www.fatcow.com/
