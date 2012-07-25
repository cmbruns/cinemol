# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'atom_size_dialog.ui'
#
# Created: Wed Jul 25 01:25:33 2012
#      by: pyside-uic 0.2.14 running on PySide 1.1.1
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_AtomSizeDialog(object):
    def setupUi(self, AtomSizeDialog):
        AtomSizeDialog.setObjectName("AtomSizeDialog")
        AtomSizeDialog.resize(225, 115)
        self.verticalLayout = QtGui.QVBoxLayout(AtomSizeDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.widget = QtGui.QWidget(AtomSizeDialog)
        self.widget.setObjectName("widget")
        self.horizontalLayout = QtGui.QHBoxLayout(self.widget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtGui.QLabel(self.widget)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.doubleSpinBox = QtGui.QDoubleSpinBox(self.widget)
        self.doubleSpinBox.setMinimum(0.01)
        self.doubleSpinBox.setSingleStep(0.05)
        self.doubleSpinBox.setProperty("value", 1.0)
        self.doubleSpinBox.setObjectName("doubleSpinBox")
        self.horizontalLayout.addWidget(self.doubleSpinBox)
        self.dial = QtGui.QDial(self.widget)
        self.dial.setWrapping(True)
        self.dial.setObjectName("dial")
        self.horizontalLayout.addWidget(self.dial)
        self.verticalLayout.addWidget(self.widget)
        self.buttonBox = QtGui.QDialogButtonBox(AtomSizeDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(AtomSizeDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), AtomSizeDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), AtomSizeDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(AtomSizeDialog)

    def retranslateUi(self, AtomSizeDialog):
        AtomSizeDialog.setWindowTitle(QtGui.QApplication.translate("AtomSizeDialog", "Adjust atom size", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("AtomSizeDialog", "Atom size factor", None, QtGui.QApplication.UnicodeUTF8))
        self.doubleSpinBox.setSuffix(QtGui.QApplication.translate("AtomSizeDialog", " X", None, QtGui.QApplication.UnicodeUTF8))

