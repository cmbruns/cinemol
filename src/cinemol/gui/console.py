'''
Created on Jul 22, 2012

@author: cmbruns
'''

from console_ui import Ui_ConsoleWindow
from PySide import QtCore
from PySide.QtCore import *
from PySide.QtGui import *
from traceback import print_exc
import sys


class ConsoleStderrStream(object):
    def __init__(self, text_edit):
        self.text_edit = text_edit
        sys.stderr = self
        
    def __del__(self):
        sys.stderr = sys.__stderr__
        
    def write(self, text):
        sys.__stderr__.write(text)
        cursor = self.text_edit.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertText(text)
        self.text_edit.setTextCursor(cursor)
        self.text_edit.ensureCursorVisible()


class ConsoleStdoutStream(object):
    def __init__(self, text_edit):
        self.text_edit = text_edit
        sys.stdout = self
        
    def __del__(self):
        sys.stdout = sys.__stdout__
        
    def write(self, text):
        sys.__stdout__.write(text)
        cursor = self.text_edit.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertText(text)
        self.text_edit.setTextCursor(cursor)


class Console(QMainWindow):
    '''
    Command window for interactive python commands
    '''
    def __init__(self, parent=None):
        '''
        Constructor
        '''
        QMainWindow.__init__(self, parent)
        self.ui = Ui_ConsoleWindow()
        self.ui.setupUi(self)
        self.prompt = ">>> "
        QApplication.clipboard().dataChanged.connect(self.on_clipboard_data_changed)
        self.te = self.ui.plainTextEdit
        self.te.selectionChanged.connect(self.on_selection_changed)
        self.te.cursorPositionChanged.connect(self.on_cursor_position_changed)
        self.append("Welcome to the Cinemol python console!")
        # This header text is intended to look just like the standard python banner
        self.append("Python " + sys.version + " on " + sys.platform)
        self.append('Type "help", "copyright", "credits" or "license" for more information.')
        self.append("") # Need return before prompt
        self.place_new_prompt()
        # make cursor about the size of a letter
        cursor_size = QFontMetrics(self.te.font()).width("m")
        if cursor_size > 0:
            self.te.setCursorWidth(cursor_size)
        else:
            self.te.setCursorWidth(1)
        self.command_ring = CommandRing()
        self.multiline_command = ""
        self.te.installEventFilter(self)
        self.te.viewport().installEventFilter(self)
        self.stdout = ConsoleStdoutStream(self.te)
        self.stderr = ConsoleStderrStream(self.te)
        
    def show_previous_command(self):
        pass # TODO
    
    def show_next_command(self):
        pass # TODO

    def cursor_is_in_editing_region(self, cursor):
        # Want to be to the right of the prompt...
        if cursor.positionInBlock() < len(self.prompt):
            return False
        # ... and in the final line.
        if cursor.blockNumber() != self.te.blockCount() - 1:
            return False
        if cursor.anchor() != cursor.position():
            # Anchor might be outside of editing region
            anchorCursor = QTextCursor(cursor)
            anchorCursor.setPosition(cursor.anchor())
            if anchorCursor.positionInBlock() < len(self.prompt):
                return False
            if anchorCursor.blockNumber() != self.te.blockCount() - 1:
                return False
        return True

    def eventFilter(self, watched, event):
        if event.type() == QEvent.MouseButtonPress:
            # On unix, we want to update cursor position on middle
            # button press, before deciding whether editing is possible.
            mouseEvent = event
            # Qt 4.6 has only "MidButton", not "MiddleButton"
            if mouseEvent.buttons() == Qt.MidButton:
                newCursor = self.te.cursorForPosition(mouseEvent.pos())
                self.te.setTextCursor(newCursor)
        elif event.type() == QEvent.KeyPress:
            keyEvent = event
            # CONTROL-keystrokes
            key = keyEvent.key()
            if keyEvent.modifiers() & Qt.ControlModifier:
                # Ctrl-p and Ctrl-n for command history
                if key == Qt.Key_P:
                    self.show_previous_command()
                    return True
                elif key == Qt.Key_N:
                    self.show_next_command()
                    return True
            elif keyEvent.modifiers() & Qt.AltModifier:
                pass
            elif keyEvent.modifiers() & Qt.MetaModifier:
                pass
            else: # non-Ctrl keystrokes
                # Use up and down arrows for history
                if key == Qt.Key_Up:
                    self.show_previous_command()
                    return True
                elif key == Qt.Key_Down:
                    self.show_next_command()
                    return True
                # Prevent left arrow from leaving editing area
                elif (key == Qt.Key_Left) or (key == Qt.Key_Backspace):
                    # Qt 4.6 lacks QTextCursor.positionInBlock
                    if (self.te.textCursor().positionInBlock() == len(self.prompt)) and self.cursor_is_in_editing_region(self.te.textCursor()):
                        return True # no moving left into prompt with arrow key
                # Trigger command execution with <Return>
                elif (key == Qt.Key_Return) or (key == Qt.Key_Enter):
                    self.run_console_command()
                    return True # Consume event.  We will take care of inserting the newline.
                # If this is a printing character, make sure the editing console is activated
                if len(keyEvent.text()) > 0:
                    if not self.cursor_is_in_editing_region(self.te.textCursor()):
                        self.te.setTextCursor(self.latestGoodCursorPosition)
        return QMainWindow.eventFilter(self, watched, event)

    def run_console_command(self):
        # Clear undo/redo buffer, we don't want prompts and output in there.
        self.te.setUndoRedoEnabled(False)
        # Scroll down after command, if and only if bottom is visible now.
        end_is_visible = self.te.document().lastBlock().isVisible()
        command = self.get_current_command()    
        self.command_ring.add_history(command)
        if len(self.multiline_command) > 0:
            # multi-line command can only be ended with a blank line.
            if len(command) == 0:
                command = self.multiline_command # execute it now
            else:
                self.multiline_command = self.multiline_command + command + "\n"
                command = "" # skip execution until next time
        # Add carriage return, so output will appear on subsequent line.
        # (It would be too late if we waited for plainTextEdit
        #  to process the <Return>)
        self.te.moveCursor(QTextCursor.End)
        self.append("")  # We consumed the key event, so we have to add the newline.
        if len(command) > 0:
            try:
                result = eval(command)
                print result
            except:
                try:
                    exec command in globals()
                except: # Exception e:
                    print_exc()
        self.place_new_prompt(end_is_visible)

    def get_current_command(self):
        cursor = self.te.textCursor()
        cursor.setPosition(self.current_command_start_position, QTextCursor.MoveAnchor)
        cursor.movePosition(QTextCursor.End, QTextCursor.KeepAnchor)
        command = cursor.selectedText()
        cursor.clearSelection()
        return command
        
    def place_new_prompt(self, make_visible=True):
        self.te.setUndoRedoEnabled(False)
        self.te.moveCursor(QTextCursor.End)
        self.te.insertPlainText(self.prompt)
        self.te.moveCursor(QTextCursor.End)
        if make_visible:
            self.te.ensureCursorVisible()
        self.latest_good_cursor = self.te.textCursor()
        self.current_command_start_position = self.latest_good_cursor.position()
        self.te.setUndoRedoEnabled(True)
    
    def append(self, message):
        self.ui.plainTextEdit.appendPlainText(message)

    @QtCore.Slot()
    def on_clipboard_data_changed(self):
        pass
        
    @QtCore.Slot()
    def on_selection_changed(self):
        pass
    
    @QtCore.Slot()
    def on_cursor_position_changed(self):
        pass

class CommandRing:
    "Stores command history"
    def __init__(self, ring_size=50):
        self._commands = ring_size * [None]
        self.newest_command_index = None
        self.oldest_command_index = None
        self.current_command_index = None
        self.stored_provisional_command = ""
    
    def add_history(self, command):
        if 0 == len(command):
            return False # don't store empty commands
        if self.newest_command_index is None:
            self.newest_command_index = 0
            self.oldest_command_index = 0
            self.current_command_index = None
            self._commands[self.newest_command_index] = command
            return True
        previous_command = self._commands[self.newest_command_index]
        if previous_command == command:
            self.current_command_index = None
            return False # don't store repeated commands
        self.newest_command_index = self._increment(self.newest_command_index)
        if (self.oldest_command_index == self.newest_command_index):
            self.oldest_command_index = self._increment(self.oldest_command_index)
        self.current_command_index = None
        self._commands[self.newest_command_index] = command
        return True
        
    def _increment(self, val):
        "circular increment"
        return (val+1) % len(self._commands)
    
    def _decrement(self, val):
        return (val + len(self._commands) - 1) % len(self._commands)
