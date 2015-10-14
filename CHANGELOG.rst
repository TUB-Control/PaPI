Changelog
---------

v.1.x:
------

-  **feature**: A new run-mode is available. Prevents Plugins resize and move.
-  **feature**: Added ability to define favourite plugins
-  **feature**: Added ability to define custom categories of plugins by using custom subfolders in the plugin folder
-  **feature**: PaPI Configuration can be saved in a json format. The resulting file can be used by the PaPI Simulink block
-  **feature**: Auto-Scale of background images
-  **feature**: Background image will be the same after dock / detach
-  **improvement**: Cleaned up the plugin developers API
-  **doc**: Added documentation for the main window
-  **doc**: Added documentation for shortcuts
-  **simulink**: Added Checkbox to control if the UDPServer should be started in the initial phase
-  **gui**: Added search bar for overview menu and create menu
-  **gui**: Added shortcut features to search bar and tree in overview menu and create menu
-  **gui**: Added shortcuts for actions of the main window for example: save, load
-  **fix**: The connection between a PCP and a parameter will now be correctly restored.
-  **fix**: 'PreviousParameter' from cfg will now be restored correctly
-  **fix**: Removed old references to previous used license.
-  **fix**: Various not mentionable bug fixes, see Github issue tracker.
-  **plugin**: Plot plugin will now save zoom modifications done by scrolling
-  **plugin**: Added prefix (cb\_/pl\_) for functions provided by plugins which can be used by plugin developer.
-  **plugin**: Renamed ownProcess\_base to base\_ownProcess.

v.1.2:
------

-  **major-change** Switched from PySide to PyQt and upgraded to use Qt5
   (also switched to develop branch of pyqtgraph)
-  **minor-change** GUI: Removed buttons, added toolbar, icons to distinguish between Events and Blocks.
-  **plugin**: Added a new visual plugin: RehaStimGUI: Used to describe
   channel attributes for different states
-  **plugin**: Added a new pcplugin: Textfield
-  **plugin**: Changed Slider event to 'Change' (previous 'SliderBlock')
-  **plugin**: Changed Button event to 'Click' (previous 'Click_event')
-  **plugin**: A visual plugin can now be opened maximized.
-  **plugin**: Added a new visual plugin: Console. Mainly used to control scilab in connection with ORTD.
-  **feature**: Added a simulink block which enables the communication
   between PaPI and simulink
-  **feature**: Added commandline options
-  **feature**: Added ability to stop PaPI in the right manner by use of CTRL+C
-  **feature**: Added DEvent as a new object to provide the ability to change parameters.
-  **feature**: A single tab can be opened in an extra window.
-  **feature**: Added 'help' button in the create plugin menu which opens the documentation for this plugin.
-  **doc**: Added support for plugin documentation based on
   ReStructuredText.
-  **doc**: Moved from github-wiki to ReStructedText
-  **doc**: Improved documentation.
-  **fix**: Fixed change of yRange by context menu (#38)
-  **fix**: An error occurred if the slider was changed without controlling a parameter (#43)

v.1.1: LAST RELEASE WITH PYSIDE
-------------------------------

-  **fix**: Core will check plugin state before routing, so data to
   paused plugins will not be routed (#19)
-  **fix**: Obsolete parameter in send\_parameter\_change was removed
   (#21)
-  **fix**: Clean up of DParameter (#18)
-  **fix**: Renamed some variables of ownProcess\_base to be private
-  **fix**: Fixed memory leak of gui event processing timer loop (#25)
-  **fix**: Fixed memory leak due to recall of the plugin manager
   collection function
-  **fix**: Tab position and active tab will now be saved to xml
-  **improvement**: Changed the demux function to in improve performance
-  **improvement**: Improved core performance while processing new data
   (see #20)
-  **improvement**: Huge changes in the plotting plugin with performance
   benefits
-  **improvement**: Shifted some control logic from gui to core to
   increase speed when changing cfgs incl. subscriptions
-  **improvement**: ORTD can now receive its configuration via udp in
   multiple packages
-  **feature**: Modified PaPI gui to have tabs. User can organise visual
   plugins in tabs, remove tabs, rename tabs.
-  **feature**: PaPI now supports Mac OS X based on Darwin.
-  **plugin**: Added a new visual plugin: ProgressBar
-  **plugin**: Minor changes in LCDDisplay and Slider
-  **plugin**: Added a new pcp plugin: Radiobutton

v.1.0
-----

v.0.9
-----

-  Plot Plugin: Speedup by use of downsampling, more useable parameter,
   more dynamic legend, new ContextMenu
-  Signals are now stored and managed as object
-  Support of configuration types (file)
-  Unsubscription of single signals became possible
-  Use of pyqtgraph 0.9.10 -> removed dependency for scipy
-  Sorting in the overview menu is enabled
-  First pictures for plugins
-  Error Dialogs pops up if a plugin error occurs -> Whole GUI wont die
   anymore
-  **fix** in configloader due to invalid xml messages
-  **fix** minor bug fixes in general

v.0.8.1
-------

-  New minor feature: PaPI will save a cfg on close. One is able to load
   this cfg after startup using 'ReloadConfig'
-  Big bugfix: signal and signal name relation had an order bug. There
   is now a new back end structure handling signals
-  Signal unsubscribe is now possible using the gui
-  Signals, parameter and plugins in overview are sorted now

v.0.8
-----

-  Use plugin as wizards for configurations
-  Use ESC and RETURN for window interaction
-  New file dialog to avoid performance issues
-  **fix** signal names instead of id in overview
-  Run/Edit mode
-  Set/load background and save it to config
-  **fix** When plugin in gui crashs, gui stays alive and plugin will be
   stopped

