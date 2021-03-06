
Button
===============


.. topic:: General description

    This button is used to switch between two given values which are defined by two different states.
    It is also possible to set a name for each state.

.. figure:: _static/Button.png
    :alt: Picture of the plugin button

Event
----------------------
The plugin generates one event for the 'click action' of the user.
Every time the button is pressed, the state changes and the event is triggered.

Parameter
----------------------
There are no parameter.

Events
----------------------
A plugin instance provides this events which can be used to manipulated parameters of other plugins.

.. list-table:: Provided events
    :widths: 10 10 30
    :header-rows: 1

    * - Name
      - Type
      - Description
    * - Click
      - Float
      - Sent on every click on the button.
