
PaPIController
===============


.. topic:: General description

    This plugin is used as a central instance for other plugins to create/control plugins. Was especially created for the external PaPI interface.
    Usage example:
    When the PaPI Controller starts, it will start an UDP Plugin. Then, the UDP plugin can connect to an external target.
    After a connection is established, the target can send a PaPI config. This config is passed to the PaPI Controller.
    Then, the controller will apply the config to PaPI.

Dependencies
----------------------
Only the dependencies of the UDP Plugin. See its documentation for info.

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
