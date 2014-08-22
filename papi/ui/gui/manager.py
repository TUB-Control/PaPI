# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/gui/manager.ui'
#
# Created: Fri Aug 22 15:18:11 2014
#      by: pyside-uic 0.2.15 running on PySide 1.2.1
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_Manager(object):
    def setupUi(self, Manager):
        Manager.setObjectName("Manager")
        Manager.resize(791, 495)
        self.centralwidget = QtGui.QWidget(Manager)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayoutWidget = QtGui.QWidget(self.centralwidget)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(10, 10, 641, 431))
        self.horizontalLayoutWidget.setObjectName("horizontalLayoutWidget")
        self.horizontalLayout = QtGui.QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.treePlugin = QtGui.QTreeWidget(self.horizontalLayoutWidget)
        self.treePlugin.setObjectName("treePlugin")
        self.treePlugin.header().setVisible(True)
        self.treePlugin.header().setCascadingSectionResizes(False)
        self.treePlugin.header().setDefaultSectionSize(70)
        self.treePlugin.header().setHighlightSections(True)
        self.treePlugin.header().setMinimumSectionSize(30)
        self.treePlugin.header().setSortIndicatorShown(False)
        self.treePlugin.header().setStretchLastSection(True)
        self.horizontalLayout.addWidget(self.treePlugin)
        self.formLayout = QtGui.QFormLayout()
        self.formLayout.setObjectName("formLayout")
        self.createButton = QtGui.QPushButton(self.horizontalLayoutWidget)
        self.createButton.setObjectName("createButton")
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.createButton)
        self.subscribeButton = QtGui.QPushButton(self.horizontalLayoutWidget)
        self.subscribeButton.setObjectName("subscribeButton")
        self.formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.subscribeButton)
        self.target_id = QtGui.QLineEdit(self.horizontalLayoutWidget)
        self.target_id.setObjectName("target_id")
        self.formLayout.setWidget(1, QtGui.QFormLayout.FieldRole, self.target_id)
        self.block_name = QtGui.QLineEdit(self.horizontalLayoutWidget)
        self.block_name.setObjectName("block_name")
        self.formLayout.setWidget(2, QtGui.QFormLayout.FieldRole, self.block_name)
        self.horizontalLayout.addLayout(self.formLayout)
        Manager.setCentralWidget(self.centralwidget)
        self.statusbar = QtGui.QStatusBar(Manager)
        self.statusbar.setObjectName("statusbar")
        Manager.setStatusBar(self.statusbar)

        self.retranslateUi(Manager)
        QtCore.QMetaObject.connectSlotsByName(Manager)

    def retranslateUi(self, Manager):
        Manager.setWindowTitle(QtGui.QApplication.translate("Manager", "MainWindow", None, QtGui.QApplication.UnicodeUTF8))
        self.treePlugin.headerItem().setText(0, QtGui.QApplication.translate("Manager", "Plugin", None, QtGui.QApplication.UnicodeUTF8))
        self.treePlugin.headerItem().setText(1, QtGui.QApplication.translate("Manager", "Type", None, QtGui.QApplication.UnicodeUTF8))
        self.treePlugin.headerItem().setText(2, QtGui.QApplication.translate("Manager", "ID", None, QtGui.QApplication.UnicodeUTF8))
        self.treePlugin.headerItem().setText(3, QtGui.QApplication.translate("Manager", "Path", None, QtGui.QApplication.UnicodeUTF8))
        self.createButton.setText(QtGui.QApplication.translate("Manager", "CreatePlugin", None, QtGui.QApplication.UnicodeUTF8))
        self.subscribeButton.setText(QtGui.QApplication.translate("Manager", "Subscribe", None, QtGui.QApplication.UnicodeUTF8))

