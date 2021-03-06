
ToMAT
===============


.. topic:: General description

    This plugin is used save subscribed signals in a matlab file.

.. code:: bash

    sudo apt-get install python3-scipy

Configuration
----------------------
The plugin uses this specific configuration.

.. list-table:: Plugin configuration
    :widths: 15 10 50
    :header-rows: 1

    * - Name
      - Type
      - Description
    * - file
      - String
      - Name of the matlab file.

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
    * - start_saving
      - Bool
      - (0|1)
      - Triggers the save process.
    * - save_data_for_x_ms
      - Int
      - 1000
      - The plugins saves all incoming data for x ms.
    * - file
      - String
      - PaPI.mat
      - Used to set the name of the matlab file.

Example
----------------------

An example configuration can be found here: :download:`example_config.xml <_static/example_config.xml>`
