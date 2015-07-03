Design Guide Plugin development
===============================

How to ...
----------

... start
~~~~~~~~~

It is recommended to use a given template as entry point for the
development of an own plugin. The template files can be found in
``papi/plugin/templates``.

-  ``IOP_DPP_template.py`` - template for the development of IO-Plugins
   or Data Processing Plugin.
-  ``visual_template.py`` - template for the development of visual
   Plugins.

The plugins are written in python 3.4. For the development you can use
this tools:

   - Editor with syntax highlighting
   - PyCharm


... create a Block
~~~~~~~~~~~~~~~~~~

Blocks are used to collect all signals created by the same source. An
entire block and or a single signal can be subscribed by other plugins
e.g. a plot.

It is necessary to imports this objects:

.. code:: python

    from papi.data.DPlugin import DBlock
    from papi.data.DSignal import DSignal

In the following we gonna create a Block with the name ``Source``. In
the next step a signal named ``Step`` is created and added to the
previous created Block. At the end the PaPI-backend will be informed and
the Block can be used by other plugins. It is **very important** to know
that the PaPI-backend only knows the last blocks sent by
``send_new_block_list``. Previous sent block will be deleted.

.. code:: python

    def start_init(self, config=None):
       self.block = DBlock('Source')
       signal = DSignal('Step')
       self.block.add_signal(signal)
       self.send_new_block_list([block])

... create Parameter
~~~~~~~~~~~~~~~~~~~~

Parameters are used to enable an external control of a running plugin.

It is necessary to imports this object:

.. code:: python

    from papi.data.DParameter import DParameter

At first three parameters are created and the PaPI-backend gets
informed. To limit possible user entries at the frontend for the third parameter a regex
was defined

.. code:: python

    def start_init(self, config=None):
       self.para1 = DParameter('ParameterName1',default=0)
       self.para2 = DParameter('ParameterName2',default=0)
       self.para3 = DParameter('ParameterName3',default=0, Regex='^(1|0){1}$')
       self.send_new_parameter_list([self.para1, self.para2, self.para2])

... process new data
~~~~~~~~~~~~~~~~~~~~

The function ``execute`` is called by the PaPI backend with a currently
received data set. Data is a dictionary with an entry 't' which contains
the time vector. The other entries are data vectors. To determine the
data source the corresponding block\_name is given for a single execute
step.

.. code:: python

    def execute(self, Data=None, block_name = None, plugin_uname = None):
       time = Data['t']

       for key in Data:
          if key != 't':
             data = Data[key]

... to react to parameter changes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``set_parameter`` is always called when a parameter is changed. To
determine the modified parameter the parameter's name is given as
``name``, of course the new value is also given as ``value``. The value
is always from type ``string`` that means it may be necessary to cast
the string as float, or int.

.. code:: python

    def set_parameter(self, name, value):
       if name == 'ParameterName1':
          print(name + " --> " + str(value));

       if name == 'ParameterName2':
          new_int = int(float(value))
          print(name + " --> " + str(new_int))

       if name == 'ParameterName3':
          if int(float(value)) == int('1'):
             print(name + " --> " + " True ")
          else:
             print(name + " --> " + " False ")

...to create a configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

It is possible to set a default configuration for every plugin which can
be modified by the user during the creation process.

.. code:: python

    def get_plugin_configuration(self):
       config = {
          'flag': {
             'value': "0",
             'regex': '^(1|0)$',
             'type': 'bool',
             'display_text': 'Flag',
             'tooltip' : 'Checkable checkbox'
          }, 
          'color': {
             'value': "(123,123,123)",
             'regex': '^\(\d+\s*,\s*\d+\s*,\s*\d+\)$',
             'type': 'color',   
             'advanced': '1',
             'display_text': 'Color'
          }, 
          'file': {
             'value': "",
             'advanced': '1',
             'type' : 'file',
             'display_text': 'Needed File',
             'tooltip' : 'File needed by the plugin'
          }, 
          'text': {
             'value': 'Wert',
             'advanced': '1',
             'display_text': 'Erweiterter Wert'
          }
       }
       return config

As you can see it is possible to describe a single configuration attribute in a detailed way but only the key ``value`` is mandatory.

The other keys are used to provided a comfortable change of the attribute during the creation process.

.. list-table:: Possible keys for an attribute
    :widths: 3 10
    :header-rows: 1

    * - Key
      - Description
    * - value
      - Mandatory key !!
    * - regex
      - used to limit the possible user entries in a textfield by the use of a regular expression.
    * - type
      - enables additional gui elements in the creation dialog.
    * - advanced
      - is used display this attribute on an additional tab in the creation dialog.
    * - display_text
      - sets the name of the attribute as it is seen by the user.
    * - tooltip
      - used to define a tooltip triggered by a mouse hover.

PaPI supports currently only the following types.

.. list-table:: Supported types
    :widths: 3 10 3
    :header-rows: 1

    * - Type
      - Description
      - Value
    * - color
      - Opens a color picker
      - (r,g,b)
    * - file
      - Opens a file dialog
      - ~/config/File.xml
    * - bool
      - Checkbox
      - (0|1)

In case of an unknown type or none type was defined a simple textfield is used.

What happens if the user triggers ...
--------------------------------------

... pause?
~~~~~~~~~~~~~~~~~~~~~~~~

The PaPI framework executes this functions

.. code:: python

    def pause(self):
        """
        Function pause

        :return:
        """
        pass

This enables the developer to handle a users wish to break the plugin. PaPI will also stop to call the ``execute(Data, block_name, plugin_uname)`` function.

... resume?
~~~~~~~~~~~~~~~~~~~~~~~~

The PaPI framework executes this functions

.. code:: python

    def resume(self):
        """
        Function resume

        :return:
        """
        pass

This enables the developer to handle a users wish to resume the plugin. PaPI will start again to call the ``execute(Data, block_name, plugin_uname)`` function if necessary.

... quit?
~~~~~~~~~~~~~~~~~~~~~~~~

The PaPI framework executes this functions

.. code:: python

    def quit(self):
        """
        Function quit

        :return:
        """
        pass

When this function was exectuted PaPI will stop and remove the plugin.
