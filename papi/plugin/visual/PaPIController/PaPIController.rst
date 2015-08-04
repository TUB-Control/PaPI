
PaPIController
===============


.. topic:: General description

    This plugin is used as a central instance for other plugins to create/control plugins. Was especially created for the external PaPI interface.

Configuration
----------------------
The plugin uses this specific configuration.

.. list-table:: Plugin configuration
    :widths: 15 10 10 50
    :header-rows: 1

    * - Name
      - Type
      - Example
      - Description
    * - UDP_Plugin_uname
      - String
      - UDPlugin
      - Uname to use for UDP plugin instance.
    * - 1:address
      - IP
      - 127.0.0.1
      - Listen IP
    * - 2:source_port
      - Int
      - 20000
      - Local port.
    * - 3:out_port
      - Int
      - 20001
      - Remote port.
    * - SendOnReceivePort
      - Bool
      - (0|1)
      - Use same port for send and receive.
    * - UseSocketIO
      - Bool
      - (0|1)
      - Use the Socket IO
    * - OnlyInitialConfig
      - Bool
      - (0|1)
      - Use only first configuration, ignore further configurations.

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
    * - ProgressValue
      - None
      - None
      - None
