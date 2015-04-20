# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/gui/qt_new/main.ui'
#
# Created: Mon Apr 20 15:47:05 2015
#      by: PyQt4 UI code generator 4.10.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_QtNewMain(object):
    def setupUi(self, QtNewMain):
        QtNewMain.setObjectName(_fromUtf8("QtNewMain"))
        QtNewMain.resize(693, 600)
        self.centralwidget = QtGui.QWidget(QtNewMain)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.centralwidget)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.loadButton = QtGui.QPushButton(self.centralwidget)
        self.loadButton.setObjectName(_fromUtf8("loadButton"))
        self.horizontalLayout.addWidget(self.loadButton)
        self.saveButton = QtGui.QPushButton(self.centralwidget)
        self.saveButton.setObjectName(_fromUtf8("saveButton"))
        self.horizontalLayout.addWidget(self.saveButton)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.verticalLayout_2.addLayout(self.verticalLayout)
        self.widgetTabs = QtGui.QTabWidget(self.centralwidget)
        self.widgetTabs.setContextMenuPolicy(QtCore.Qt.DefaultContextMenu)
        self.widgetTabs.setObjectName(_fromUtf8("widgetTabs"))
        self.verticalLayout_2.addWidget(self.widgetTabs)
        QtNewMain.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(QtNewMain)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 693, 25))
        self.menubar.setDefaultUp(False)
        self.menubar.setNativeMenuBar(False)
        self.menubar.setObjectName(_fromUtf8("menubar"))
        self.menuPaPI = QtGui.QMenu(self.menubar)
        self.menuPaPI.setObjectName(_fromUtf8("menuPaPI"))
        self.menuPlugin = QtGui.QMenu(self.menubar)
        self.menuPlugin.setObjectName(_fromUtf8("menuPlugin"))
        self.menuView = QtGui.QMenu(self.menubar)
        self.menuView.setObjectName(_fromUtf8("menuView"))
        self.menuHelp = QtGui.QMenu(self.menubar)
        self.menuHelp.setObjectName(_fromUtf8("menuHelp"))
        QtNewMain.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(QtNewMain)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        QtNewMain.setStatusBar(self.statusbar)
        self.actionLoad = QtGui.QAction(QtNewMain)
        self.actionLoad.setObjectName(_fromUtf8("actionLoad"))
        self.actionSave = QtGui.QAction(QtNewMain)
        self.actionSave.setObjectName(_fromUtf8("actionSave"))
        self.actionOverview = QtGui.QAction(QtNewMain)
        self.actionOverview.setObjectName(_fromUtf8("actionOverview"))
        self.actionCreate = QtGui.QAction(QtNewMain)
        self.actionCreate.setObjectName(_fromUtf8("actionCreate"))
        self.actionExit = QtGui.QAction(QtNewMain)
        self.actionExit.setObjectName(_fromUtf8("actionExit"))
        self.actionReloadConfig = QtGui.QAction(QtNewMain)
        self.actionReloadConfig.setObjectName(_fromUtf8("actionReloadConfig"))
        self.actionResetPaPI = QtGui.QAction(QtNewMain)
        self.actionResetPaPI.setObjectName(_fromUtf8("actionResetPaPI"))
        self.actionRunMode = QtGui.QAction(QtNewMain)
        self.actionRunMode.setObjectName(_fromUtf8("actionRunMode"))
        self.actionSetBackground = QtGui.QAction(QtNewMain)
        self.actionSetBackground.setObjectName(_fromUtf8("actionSetBackground"))
        self.actionPaPI_Wiki = QtGui.QAction(QtNewMain)
        self.actionPaPI_Wiki.setObjectName(_fromUtf8("actionPaPI_Wiki"))
        self.actionPaPI_Doc = QtGui.QAction(QtNewMain)
        self.actionPaPI_Doc.setObjectName(_fromUtf8("actionPaPI_Doc"))
        self.actionAbout = QtGui.QAction(QtNewMain)
        self.actionAbout.setObjectName(_fromUtf8("actionAbout"))
        self.actionAbout_Qt = QtGui.QAction(QtNewMain)
        self.actionAbout_Qt.setObjectName(_fromUtf8("actionAbout_Qt"))
        self.actionAbout_PySide = QtGui.QAction(QtNewMain)
        self.actionAbout_PySide.setObjectName(_fromUtf8("actionAbout_PySide"))
        self.actionReload_Plugin_DB = QtGui.QAction(QtNewMain)
        self.actionReload_Plugin_DB.setObjectName(_fromUtf8("actionReload_Plugin_DB"))
        self.menuPaPI.addAction(self.actionLoad)
        self.menuPaPI.addAction(self.actionSave)
        self.menuPaPI.addAction(self.actionReloadConfig)
        self.menuPaPI.addAction(self.actionResetPaPI)
        self.menuPaPI.addSeparator()
        self.menuPaPI.addAction(self.actionExit)
        self.menuPlugin.addAction(self.actionOverview)
        self.menuPlugin.addAction(self.actionCreate)
        self.menuPlugin.addSeparator()
        self.menuPlugin.addAction(self.actionReload_Plugin_DB)
        self.menuView.addAction(self.actionRunMode)
        self.menuHelp.addAction(self.actionPaPI_Wiki)
        self.menuHelp.addAction(self.actionPaPI_Doc)
        self.menuHelp.addSeparator()
        self.menuHelp.addAction(self.actionAbout)
        self.menuHelp.addAction(self.actionAbout_Qt)
        self.menubar.addAction(self.menuPaPI.menuAction())
        self.menubar.addAction(self.menuPlugin.menuAction())
        self.menubar.addAction(self.menuView.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())

        self.retranslateUi(QtNewMain)
        self.widgetTabs.setCurrentIndex(-1)
        QtCore.QObject.connect(self.actionExit, QtCore.SIGNAL(_fromUtf8("triggered()")), QtNewMain.close)
        QtCore.QMetaObject.connectSlotsByName(QtNewMain)

    def retranslateUi(self, QtNewMain):
        QtNewMain.setWindowTitle(_translate("QtNewMain", "MainWindow", None))
        self.loadButton.setText(_translate("QtNewMain", "Load", None))
        self.saveButton.setText(_translate("QtNewMain", "Save", None))
        self.menuPaPI.setTitle(_translate("QtNewMain", "PaPI", None))
        self.menuPlugin.setTitle(_translate("QtNewMain", "Plugin", None))
        self.menuView.setTitle(_translate("QtNewMain", "View", None))
        self.menuHelp.setTitle(_translate("QtNewMain", "Help", None))
        self.actionLoad.setText(_translate("QtNewMain", "Load", None))
        self.actionSave.setText(_translate("QtNewMain", "Save", None))
        self.actionOverview.setText(_translate("QtNewMain", "Overview", None))
        self.actionCreate.setText(_translate("QtNewMain", "Create", None))
        self.actionExit.setText(_translate("QtNewMain", "Exit", None))
        self.actionReloadConfig.setText(_translate("QtNewMain", "ReloadConfig", None))
        self.actionResetPaPI.setText(_translate("QtNewMain", "ResetPaPI", None))
        self.actionRunMode.setText(_translate("QtNewMain", "RunMode", None))
        self.actionSetBackground.setText(_translate("QtNewMain", "SetBackground", None))
        self.actionPaPI_Wiki.setText(_translate("QtNewMain", "PaPI Wiki", None))
        self.actionPaPI_Doc.setText(_translate("QtNewMain", "PaPI Doc", None))
        self.actionAbout.setText(_translate("QtNewMain", "About", None))
        self.actionAbout_Qt.setText(_translate("QtNewMain", "About Qt", None))
        self.actionAbout_PySide.setText(_translate("QtNewMain", "About PySide", None))
        self.actionReload_Plugin_DB.setText(_translate("QtNewMain", "Reload DB", None))

