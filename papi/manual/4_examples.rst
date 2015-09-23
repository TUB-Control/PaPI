Examples
============

Fourier
-------

Navigate to your PaPI folder:

``cd PaPI``

Start a small server on port 9999 by the following command

``python3.4 data_sources/fourier_rect.pt``

Start PaPI and load the ExampleFourier Configuration

``python3.4 main.py``

``cfg_collection/ExampleFourier.xml``

This configuration will load the *Add*-Plugin, two *Plot*-Plugins and
the *Fourier*\ rect\_-Plugin

Wizard
------

Navigate to your PaPI folder:

``cd PaPI``

The visual plugin ``ExampleWizard`` can be used to get a first
impression on the way wizards may be implemented. This plugin can be
manually created or the following configuration can be used:

``cfg_collection/ExampleWizard.xml``
