
Sine
===============


.. topic:: General description

    This plugin is used as simple data source of different sine signals.

Output
-----------
This plugin outputs different sine wave signals with static and variable frequencies.


Dependencies
-----------
Python3 numpy is required to run this plugin.

Configuration
----------------------
The plugin uses this specific configuration.

.. list-table:: Plugin configuration
    :widths: 15 10 50
    :header-rows: 1

    * - Name
      - Type
      - Description
    * - amax
      - Int
      - Name of the signal whose first value is used to set the current value for the progress bar.
    * - f
      - Float
      - Frequency, currently not used.

Parameter
----------------------
A plugin instance can be manipulated by the following parameter.

.. list-table:: Provided parameter
    :widths: 15 10 10 50
    :header-rows: 1

    * - Name
      - Type
      - Example
      - Description
    * - Frequenz Block SinMit_f3
      - Float
      - 0.3
      - Sets the frequency of the sine signal f3.