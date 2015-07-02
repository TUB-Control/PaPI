# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/gui/qt_new/create.ui'
#
# Created: Thu Jul  2 15:35:55 2015
#      by: PyQt5 UI code generator 5.2.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Create(object):
    def setupUi(self, Create):
        Create.setObjectName("Create")
        Create.resize(800, 601)
        self.centralwidget = QtWidgets.QWidget(Create)
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
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 385, 532))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout.setObjectName("verticalLayout")
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        self.formLayout.setObjectName("formLayout")
        self.nameLabel = QtWidgets.QLabel(self.scrollAreaWidgetContents)
        self.nameLabel.setObjectName("nameLabel")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.nameLabel)
        self.authorLabel = QtWidgets.QLabel(self.scrollAreaWidgetContents)
        self.authorLabel.setObjectName("authorLabel")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.authorLabel)
        self.pathLabel = QtWidgets.QLabel(self.scrollAreaWidgetContents)
        self.pathLabel.setObjectName("pathLabel")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.pathLabel)
        self.descriptionLabel = QtWidgets.QLabel(self.scrollAreaWidgetContents)
        self.descriptionLabel.setObjectName("descriptionLabel")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.descriptionLabel)
        self.descriptionText = QtWidgets.QTextEdit(self.scrollAreaWidgetContents)
        self.descriptionText.setObjectName("descriptionText")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.descriptionText)
        self.nameEdit = QtWidgets.QLineEdit(self.scrollAreaWidgetContents)
        self.nameEdit.setObjectName("nameEdit")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.nameEdit)
        self.authorEdit = QtWidgets.QLineEdit(self.scrollAreaWidgetContents)
        self.authorEdit.setObjectName("authorEdit")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.authorEdit)
        self.pathEdit = QtWidgets.QLineEdit(self.scrollAreaWidgetContents)
        self.pathEdit.setObjectName("pathEdit")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.pathEdit)
        self.modulesLabel = QtWidgets.QLabel(self.scrollAreaWidgetContents)
        self.modulesLabel.setObjectName("modulesLabel")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.LabelRole, self.modulesLabel)
        self.modulesList = QtWidgets.QListWidget(self.scrollAreaWidgetContents)
        self.modulesList.setObjectName("modulesList")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.FieldRole, self.modulesList)
        self.verticalLayout.addLayout(self.formLayout)
        self.createButton = QtWidgets.QPushButton(self.scrollAreaWidgetContents)
        self.createButton.setObjectName("createButton")
        self.verticalLayout.addWidget(self.createButton)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.horizontalLayout.addWidget(self.scrollArea)
        self.horizontalLayout_2.addLayout(self.horizontalLayout)
        Create.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(Create)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 25))
        self.menubar.setObjectName("menubar")
        Create.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(Create)
        self.statusbar.setObjectName("statusbar")
        Create.setStatusBar(self.statusbar)

        self.retranslateUi(Create)
        QtCore.QMetaObject.connectSlotsByName(Create)

    def retranslateUi(self, Create):
        _translate = QtCore.QCoreApplication.translate
        Create.setWindowTitle(_translate("Create", "MainWindow"))
        self.nameLabel.setText(_translate("Create", "Name"))
        self.authorLabel.setText(_translate("Create", "Author"))
        self.pathLabel.setText(_translate("Create", "Path"))
        self.descriptionLabel.setText(_translate("Create", "Description"))
        self.modulesLabel.setText(_translate("Create", "Missing\n"
"Modules"))
        self.createButton.setText(_translate("Create", "Create Plugin"))

