# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'console.ui'
#
# Created: Tue Aug 07 00:26:14 2012
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
        self.menuOpen_recent = QtGui.QMenu(self.menuFile)
        self.menuOpen_recent.setObjectName("menuOpen_recent")
        ConsoleWindow.setMenuBar(self.menubar)
        self.actionRun_script = QtGui.QAction(ConsoleWindow)
        self.actionRun_script.setObjectName("actionRun_script")
        self.actionRun_recent = QtGui.QAction(ConsoleWindow)
        self.actionRun_recent.setObjectName("actionRun_recent")
        self.actionFoo = QtGui.QAction(ConsoleWindow)
        self.actionFoo.setObjectName("actionFoo")
        self.menuFile.addAction(self.actionRun_script)
        self.menuFile.addAction(self.menuOpen_recent.menuAction())
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuEdit.menuAction())

        self.retranslateUi(ConsoleWindow)
        QtCore.QMetaObject.connectSlotsByName(ConsoleWindow)

    def retranslateUi(self, ConsoleWindow):
        ConsoleWindow.setWindowTitle(QtGui.QApplication.translate("ConsoleWindow", "Cinemol command window", None, QtGui.QApplication.UnicodeUTF8))
        self.menuEdit.setTitle(QtGui.QApplication.translate("ConsoleWindow", "Edit", None, QtGui.QApplication.UnicodeUTF8))
        self.menuFile.setTitle(QtGui.QApplication.translate("ConsoleWindow", "File", None, QtGui.QApplication.UnicodeUTF8))
        self.menuOpen_recent.setTitle(QtGui.QApplication.translate("ConsoleWindow", "Run recent", None, QtGui.QApplication.UnicodeUTF8))
        self.actionRun_script.setText(QtGui.QApplication.translate("ConsoleWindow", "Run script...", None, QtGui.QApplication.UnicodeUTF8))
        self.actionRun_recent.setText(QtGui.QApplication.translate("ConsoleWindow", "Run recent", None, QtGui.QApplication.UnicodeUTF8))
        self.actionFoo.setText(QtGui.QApplication.translate("ConsoleWindow", "Foo", None, QtGui.QApplication.UnicodeUTF8))

