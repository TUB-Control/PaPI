Changelog
------

v.0.9
---
 * New ContextMenu for Plot
 * Plot Plugin: Speedup by use of downsampling, more useable parameter, more dynamic legend
 * Signals are now stored and managed as object 
 * Support of configuration types [file, ]
 * Unsubscription of single signals became possible
 * Use of pyqtgraph 0.9.10
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


