# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/gui/default/PluginCreateMenu.ui'
#
# Created: Wed Sep  9 15:39:31 2015
#      by: PyQt5 UI code generator 5.2.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_PluginCreateMenu(object):
    def setupUi(self, PluginCreateMenu):
        PluginCreateMenu.setObjectName("PluginCreateMenu")
        PluginCreateMenu.resize(742, 629)
        self.centralwidget = QtWidgets.QWidget(PluginCreateMenu)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.pluginTree = QtWidgets.QTreeView(self.centralwidget)
        self.pluginTree.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectItems)
        self.pluginTree.setObjectName("pluginTree")
        self.pluginTree.header().setCascadingSectionResizes(True)
        self.horizontalLayout.addWidget(self.pluginTree)
        self.scrollArea = QtWidgets.QScrollArea(self.centralwidget)
        self.scrollArea.setEnabled(False)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 367, 585))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout.setObjectName("verticalLayout")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.pathLabel = QtWidgets.QLabel(self.scrollAreaWidgetContents)
        self.pathLabel.setObjectName("pathLabel")
        self.gridLayout.addWidget(self.pathLabel, 2, 0, 1, 1)
        self.modulesList = QtWidgets.QListWidget(self.scrollAreaWidgetContents)
        self.modulesList.setObjectName("modulesList")
        self.gridLayout.addWidget(self.modulesList, 4, 1, 1, 1)
        self.modulesLabel = QtWidgets.QLabel(self.scrollAreaWidgetContents)
        self.modulesLabel.setObjectName("modulesLabel")
        self.gridLayout.addWidget(self.modulesLabel, 4, 0, 1, 1)
        self.descriptionLabel = QtWidgets.QLabel(self.scrollAreaWidgetContents)
        self.descriptionLabel.setObjectName("descriptionLabel")
        self.gridLayout.addWidget(self.descriptionLabel, 3, 0, 1, 1)
        self.pathEdit = QtWidgets.QLineEdit(self.scrollAreaWidgetContents)
        self.pathEdit.setObjectName("pathEdit")
        self.gridLayout.addWidget(self.pathEdit, 2, 1, 1, 1)
        self.authorLabel = QtWidgets.QLabel(self.scrollAreaWidgetContents)
        self.authorLabel.setObjectName("authorLabel")
        self.gridLayout.addWidget(self.authorLabel, 1, 0, 1, 1)
        self.nameEdit = QtWidgets.QLineEdit(self.scrollAreaWidgetContents)
        self.nameEdit.setObjectName("nameEdit")
        self.gridLayout.addWidget(self.nameEdit, 0, 1, 1, 1)
        self.descriptionText = QtWidgets.QTextEdit(self.scrollAreaWidgetContents)
        self.descriptionText.setObjectName("descriptionText")
        self.gridLayout.addWidget(self.descriptionText, 3, 1, 1, 1)
        self.nameLabel = QtWidgets.QLabel(self.scrollAreaWidgetContents)
        self.nameLabel.setObjectName("nameLabel")
        self.gridLayout.addWidget(self.nameLabel, 0, 0, 1, 1)
        self.authorEdit = QtWidgets.QLineEdit(self.scrollAreaWidgetContents)
        self.authorEdit.setObjectName("authorEdit")
        self.gridLayout.addWidget(self.authorEdit, 1, 1, 1, 1)
        self.createButton = QtWidgets.QPushButton(self.scrollAreaWidgetContents)
        self.createButton.setObjectName("createButton")
        self.gridLayout.addWidget(self.createButton, 5, 1, 1, 1)
        self.helpButton = QtWidgets.QPushButton(self.scrollAreaWidgetContents)
        self.helpButton.setObjectName("helpButton")
        self.gridLayout.addWidget(self.helpButton, 5, 0, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.horizontalLayout.addWidget(self.scrollArea)
        self.horizontalLayout_2.addLayout(self.horizontalLayout)
        PluginCreateMenu.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(PluginCreateMenu)
        self.statusbar.setObjectName("statusbar")
        PluginCreateMenu.setStatusBar(self.statusbar)

        self.retranslateUi(PluginCreateMenu)
        QtCore.QMetaObject.connectSlotsByName(PluginCreateMenu)

    def retranslateUi(self, PluginCreateMenu):
        _translate = QtCore.QCoreApplication.translate
        PluginCreateMenu.setWindowTitle(_translate("PluginCreateMenu", "MainWindow"))
        self.pathLabel.setText(_translate("PluginCreateMenu", "Path"))
        self.modulesLabel.setText(_translate("PluginCreateMenu", "Missing\n"
"Modules"))
        self.descriptionLabel.setText(_translate("PluginCreateMenu", "Description"))
        self.authorLabel.setText(_translate("PluginCreateMenu", "Author"))
        self.nameLabel.setText(_translate("PluginCreateMenu", "Name"))
        self.createButton.setText(_translate("PluginCreateMenu", "Create Plugin"))
        self.helpButton.setText(_translate("PluginCreateMenu", "Help"))

