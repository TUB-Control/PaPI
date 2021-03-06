
Textfield
===============


.. topic:: General description

    The textfield is used to set a parameter. If there exists a regex for the parameter this regex will be used.


.. figure:: _static/Textfield.png
    :alt: Picture of the plugin Textfield

Configuration
----------------------
The plugin uses this specific configuration.

.. list-table:: Plugin configuration
    :widths: 15 10 30
    :header-rows: 1

    * - Name
      - Type
      - Description
    * - value_init
      - Float
      - Used to set an initial value.

Parameter
----------------------
A plugin instance can be manipulated by the following parameter.

.. list-table:: Provided parameter
    :widths: 15 10 30
    :header-rows: 1

    * - Name
      - Type
      - Description
    * - None
      - None
      - None

Events
----------------------
A plugin instance provides this events which can be used to manipulated parameters of other plugins.

.. list-table:: Provided events
    :widths: 15 10 30
    :header-rows: 1

    * - Name
      - Type
      - Description
    * - Change
      - Float
      - Sent when slider was moved.
