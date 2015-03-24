Changelog
------

v.1.XX
---
 * [fix]: core will check plugin state before routing, so data to paused plugins will not be routed (#19)
 * [fix]: oboslete parameter in send_parameter_change was removed (#21)
 * [fix]: clean up of DParameter (#18)
 * [fix]: renamed some variables of ownProcess_base to be private
 * [fix]: fixed memory leak of gui event processing timer loop (#25)
 * [fix]: fixed memory leak due to recall of the plugin manager collection function
 * [improvement]: changed the demux function to in improve performance
 * [improvement]: improved core performance while processing new data (see #20)
 * [improvement]: huge changes in the plotting plugin with performance benefits
 * [feature]: modified PaPI gui to have tabs. User can organise visual plugins in tabs, remove tabs, rename tabs.
 * [plugin]: added a new visual plugin: ProgressBar
 * [plugin]: Minor changes in LCDDisplay and Slider
 * [improvement]: shifted some control logic from gui to core to increase speed when changing cfgs incl. subscriptions
 * 
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


