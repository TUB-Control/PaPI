Changelog
------

v.1.X:
---
 * [major-change] Switched from PySide to PyQt and upgraded to use Qt5 (also switched to develop branch of pyqtgraph)
 * [plugin]: Added a new visual plugin: RehaStimGUI: Used to describe channel attributes for different states
 * [plugin]: Added a new pcplugin: Textfield
 * [feature]: Added a simulink block which enables the communication between PaPI and Simulink
 * [doc]: Added support for plugin documentation based on ReStructuredText.
 
v.1.1: LAST RELEASE WITH PYSIDE
---
 * [fix]: Core will check plugin state before routing, so data to paused plugins will not be routed (#19)
 * [fix]: Obsolete parameter in send_parameter_change was removed (#21)
 * [fix]: Clean up of DParameter (#18)
 * [fix]: Renamed some variables of ownProcess_base to be private
 * [fix]: Fixed memory leak of gui event processing timer loop (#25)
 * [fix]: Fixed memory leak due to recall of the plugin manager collection function
 * [fix]: Tab position and active tab will now be saved to xml
 * [improvement]: Changed the demux function to in improve performance
 * [improvement]: Improved core performance while processing new data (see #20)
 * [improvement]: Huge changes in the plotting plugin with performance benefits
 * [improvement]: Shifted some control logic from gui to core to increase speed when changing cfgs incl. subscriptions
 * [improvement]: ORTD can now receive its configuration via udp in multiple packages
 * [feature]: Modified PaPI gui to have tabs. User can organise visual plugins in tabs, remove tabs, rename tabs.
 * [feature]: PaPI now supports Mac OS X based on Darwin.
 * [plugin]: Added a new visual plugin: ProgressBar
 * [plugin]: Minor changes in LCDDisplay and Slider
 * [plugin]: Added a new pcp plugin: Radiobutton

v.1.0
---

v.0.9
---
 * Plot Plugin: Speedup by use of downsampling, more useable parameter, more dynamic legend, new ContextMenu
 * Signals are now stored and managed as object 
 * Support of configuration types [file, ]
 * Unsubscription of single signals became possible
 * Use of pyqtgraph 0.9.10 -> removed dependency for scipy
 * Sorting in the overview menu is enabled
 * First pictures for plugins
 * Error Dialogs pops up if a plugin error occurs -> Whole GUI wont die anymore
 * [fix] in configloader due to invalid xml messages
 * [fix] minor bug fixes in general

v.0.8.1
---
 * New minor feature: PaPI will save a cfg on close. One is able to load this cfg after startup using 'ReloadConfig'
 * Big bugfix: signal and signal name relation had an order bug. There is now a new back end structure handling signals
 * Signal unsubscribe is now possible using the gui
 * Signals, parameter and plugins in overview are sorted now

v.0.8
---

* Use plugin as wizards for configurations
* Use ESC and RETURN for window interaction
* New file dialog to avoid performance issues
* [fix] signal names instead of id in overview
* Run/Edit mode
* Set/load background and save it to config
* [fix] When plugin in gui crashs, gui stays alive and plugin will be stopped


