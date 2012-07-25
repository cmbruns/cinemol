'''
Created on Jul 24, 2012

@author: cmbruns
'''

from atom_size_dialog_ui import Ui_AtomSizeDialog
from PySide.QtGui import QDialog
from PySide import QtCore
import math

class AtomSizeDialog(QDialog):
    '''
    Dialog for setting relative atom size
    '''

    def __init__(self, parent=None):
        '''
        Constructor
        '''
        QDialog.__init__(self, parent)
        self.ui = Ui_AtomSizeDialog()
        self.ui.setupUi(self)
        self.old_dial_value = self.ui.dial.value()
        self._value = self.ui.doubleSpinBox.value()

    value_changed = QtCore.Signal(float)

    def value(self):
        return self._value
    
    @QtCore.Slot(float)
    def set_value(self, v):
        if self._value == v:
            return
        self._value = v
        self.ui.doubleSpinBox.setValue(self._value)
        self.value_changed.emit(self._value)

    @QtCore.Slot(int)
    def on_dial_valueChanged(self, v):
        diff = v - self.old_dial_value
        vmax = self.ui.dial.maximum()
        while diff > vmax/2.0:
            diff -= vmax
        while diff < -vmax/2.0:
            diff += vmax
        scale_factor = math.pow(2.0, diff / 100.0)
        self.set_value(scale_factor * self.value())
        self.old_dial_value = v
        
    @QtCore.Slot(float)
    def on_doubleSpinBox_valueChanged(self, v):
        if abs(self._value - v) > 0.009:
            self._value = v
            self.value_changed.emit(self._value)
    