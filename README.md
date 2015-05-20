PaPI v. 1.1.0
==================

Plugin based Process Interaction

NOTE: This will be the last release which uses PySide as a Qt integration and therfore the last release under LGPL.

Introduction
------
PaPI is a tool to interact with data generating processes. It can be used to get data stream of experiments or devices
like oscilloscopes.

PaPI is based on a strong plugin architecture. Therefore it is easy to expand to new environments.

PaPi will make heavily use of multi-core systems.

Installation
------
Basic installation on Ubuntu 14.04 64Bit, using python 3.4

`sudo apt-get install python3.4 git python3-pyside python3-numpy python3-pip`

`sudo pip3 install tornado`

`git clone https://github.com/TUB-Control/PaPI.git PaPI`

`cd PaPI`

`python3.4 main.py`

Tip:
If python3.4 interpreter cannot find or locate the installed packages (pyside or numpy), please make sure that the right
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

pyqtgraph-0.9.10 published under MIT-License

Used icon-set
------

fatcow-hosting-icons-3.9.2, License: http://creativecommons.org/licenses/by/3.0/us/, Provided by: http://www.fatcow.com/
