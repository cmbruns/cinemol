# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'console.ui'
#
# Created: Sun Jul 22 20:15:05 2012
#      by: pyside-uic 0.2.14 running on PySide 1.1.1
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_ConsoleWindow(object):
    def setupUi(self, ConsoleWindow):
        ConsoleWindow.setObjectName("ConsoleWindow")
        ConsoleWindow.resize(666, 278)
        self.centralwidget = QtGui.QWidget(ConsoleWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtGui.QGridLayout(self.centralwidget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.plainTextEdit = QtGui.QPlainTextEdit(self.centralwidget)
        font = QtGui.QFont()
        font.setFamily("Courier New")
        font.setPointSize(12)
        self.plainTextEdit.setFont(font)
        self.plainTextEdit.setObjectName("plainTextEdit")
        self.gridLayout.addWidget(self.plainTextEdit, 0, 0, 1, 1)
        ConsoleWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(ConsoleWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 666, 21))
        self.menubar.setObjectName("menubar")
        self.menuEdit = QtGui.QMenu(self.menubar)
        self.menuEdit.setObjectName("menuEdit")
        self.menuFile = QtGui.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        ConsoleWindow.setMenuBar(self.menubar)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuEdit.menuAction())

        self.retranslateUi(ConsoleWindow)
        QtCore.QMetaObject.connectSlotsByName(ConsoleWindow)

    def retranslateUi(self, ConsoleWindow):
        ConsoleWindow.setWindowTitle(QtGui.QApplication.translate("ConsoleWindow", "Cinemol command window", None, QtGui.QApplication.UnicodeUTF8))
        self.menuEdit.setTitle(QtGui.QApplication.translate("ConsoleWindow", "Edit", None, QtGui.QApplication.UnicodeUTF8))
        self.menuFile.setTitle(QtGui.QApplication.translate("ConsoleWindow", "File", None, QtGui.QApplication.UnicodeUTF8))

