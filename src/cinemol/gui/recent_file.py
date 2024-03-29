'''
Created on Aug 5, 2012

@author: cmbruns
'''

from PySide.QtGui import QAction
from PySide.QtCore import QSettings
from PySide import QtCore


class RecentFile(QAction):
    "QAction that reopens a previously opened file"
    def __init__(self, file_name, open_file_slot, parent=None):
        QAction.__init__(self, parent)
        self.file_name = file_name
        self.triggered.connect(self.on_triggered)
        self.open_file_requested.connect(open_file_slot)
        self.setText(file_name)
        
    def __eq__(self, rhs):
        return self.file_name == rhs.file_name
    
    open_file_requested = QtCore.Signal(str)
    
    @QtCore.Slot()
    def on_triggered(self):
        # print "triggered", self.file_name
        self.open_file_requested.emit(self.file_name)


class RecentFileList(list):
    "Memorized collection of recently opened files"
    def __init__(self, open_file_slot, key, menu):
        self.open_file_slot = open_file_slot
        self.settings_key = key
        self.menu = menu
        settings = QSettings()
        file_list = settings.value(key)
        if file_list is not None:
            for file_name in file_list:
                self.append(RecentFile(file_name, self.open_file_slot))
        self.update()
        
    def add_file(self, file_name):
        item = RecentFile(file_name, self.open_file_slot)
        if (len(self) > 0) and (self[0] == item):
            return # No action; it's already there
        if item in self:
            self.remove(item) # it might be later in the list
        self.insert(0, item) # make it the first in this list
        if len(self) > 10:
            self[:] = self[:10]
        # List changed, so save it to the registry
        settings = QSettings()
        file_list = [x.file_name for x in self]
        settings.setValue(self.settings_key, file_list)
        self.update()
        
    def update(self):
        if len(self) > 0:
            self.menu.clear()
            for a in self:
                self.menu.addAction(a)
            self.menu.menuAction().setVisible(True)
        else:
            self.menu.menuAction().setVisible(False)        
        

