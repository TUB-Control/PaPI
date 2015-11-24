Installation
============

Ubuntu 14.04
------------

Basic installation on Ubuntu 14.04 64Bit, using python 3.4

``sudo apt-get install python3.4 git python3-pyside python3-numpy python3-pip``

``sudo pip3 install tornado``

``git clone https://github.com/TUB-Control/PaPI.git PaPI``

``cd PaPI``

``python3.4 main.py``

Tip: If python3.4 interpreter cannot find or locate the installed
packages (pyside or numpy), please make sure that the right python
interpreter is called (in case there are multiple installed).

Windows 7 (not supported)
-------------------------

Python 3.4
~~~~~~~~~~

Install python3.4 from here: https://www.python.org/downloads/

The python.exe should be added to the PATH variable -> could be done
during the installation

PySide & Numpy
~~~~~~~~~~~~~~

Open a command line (maybe as administrator, depends on the installation
directory of python3.4)

``pip install -U PySide``

Download and install numpy for python3.4 from here :
http://sourceforge.net/projects/numpy/files/NumPy/1.9.2/

Get PaPI
~~~~~~~~

Download and unzip PaPI from here: https://github.com/TUB-Control/PaPI

**OR**

Download with git
``git clone https://github.com/TUB-Control/PaPI.git PaPI``