import cinemol.cinemol_globals as cinemol_globals
from cinemol_ui import Ui_MainWindow
from size_dialog import SizeDialog
from atom_size_dialog import AtomSizeDialog
from cinemol.gui.console import Console
# from cinemol.imposter import sphereImposterShaderProgram
from cinemol.movie import Movie, KeyFrame
from cinemol.console_context import cm as command
import recent_file
import cinemol.stereo3d as stereo3d
from cinemol.model import model
from PySide import QtCore
from PySide.QtGui import *
from PySide.QtCore import *
from math import pi
import re
import platform
import os

class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.console = Console()
        if platform.system() == "Darwin":
            self.ui.menubar.setParent(None) # Show menu on mac
        self.bookmarks = Movie()
        stereoActionGroup = QActionGroup(self)
        stereoActionGroup.addAction(self.ui.actionMono_None)
        stereoActionGroup.addAction(self.ui.actionRight_Left_cross_eye)
        stereoActionGroup.addAction(self.ui.actionLeft_Right_parallel)
        stereoActionGroup.addAction(self.ui.actionLeft_eye_view)
        stereoActionGroup.addAction(self.ui.actionRight_eye_view)
        stereoActionGroup.addAction(self.ui.actionRed_Cyan_anaglyph)
        stereoActionGroup.addAction(self.ui.actionGreen_Magenta_anaglyph)
        stereoActionGroup.addAction(self.ui.actionQuadro_120_Hz)
        stereoActionGroup.addAction(self.ui.actionRow_interleaved)
        stereoActionGroup.addAction(self.ui.actionColumn_interleaved)
        stereoActionGroup.addAction(self.ui.actionChecker_interleaved)
        # representations
        repActionGroup = QActionGroup(self)
        repActionGroup.addAction(self.ui.actionWireframe)
        repActionGroup.addAction(self.ui.actionSpacefill)
        # size dialog
        self.size_dialog = SizeDialog(self)
        self.size_dialog.size_changed.connect(self.resize_canvas)
        self.size_dialog.ui.comboBox.activated[str].connect(self.parse_size_box_string)
        # print QImageWriter.supportedImageFormats()
        self.atom_size_dialog = AtomSizeDialog(self)
        self.atom_size_dialog.value_changed.connect(self.set_atom_scale)
        self.recent_files = recent_file.RecentFileList(
                self.load_pdb_file, 
                "input_pdb_files", 
                self.ui.menuLoad_recent)
        self.setAcceptDrops(True)

    def closeEvent(self, event):
        self.console.close()
        QMainWindow.closeEvent(self, event)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()
        
    def dropEvent(self, event):
        for url in event.mimeData().urls():
            s = url.toString()
            self.load_pdb_file(s)
        
    @property
    def camera(self):
        return self.ui.glCanvas.renderer.camera_position

    @QtCore.Slot(float)
    def set_atom_scale(self, s):
        cinemol_globals.atom_scale = s
        self.ui.glCanvas.update()

    @QtCore.Slot(bool)
    def on_actionReset_center_triggered(self, checked):
        command.center("*")
        command.refresh()
        
    @QtCore.Slot(bool)
    def on_actionAtom_size_triggered(self, checked):
        dialog = self.atom_size_dialog
        old_scale = dialog.value()
        dialog.exec_()
        if dialog.result() == QDialog.Accepted:
            pass # keep this size
        else:
            dialog.set_value(old_scale)
        
    @QtCore.Slot(bool)
    def on_actionShow_console_triggered(self, checked):
        self.console.setVisible(checked)
    
    @QtCore.Slot(bool)
    def on_actionWireframe_triggered(self, checked):
        if len(model.selected_atoms) < 1:
            command.select("*")
        command.spacefill(False)
        command.wireframe()
        command.refresh()

    @QtCore.Slot(bool)
    def on_actionSpacefill_triggered(self, checked):
        if len(model.selected_atoms) < 1:
            command.select("*")
        command.wireframe(False)
        command.spacefill()
        command.refresh()
        
    @QtCore.Slot(bool)
    def on_actionLoad_movie_script_triggered(self, checked):
        self.bookmarks.clear()
        file_name = QFileDialog.getOpenFileName(self, 
                                                "Open movie script file",
                                                None, # TODO directory
                                                self.tr("XML files (*.xml)"))[0]
        if file_name == "":
            return
        print file_name;
        script_file = QFile(file_name)
        if script_file.open(QIODevice.ReadOnly):
            reader = QXmlStreamReader(script_file)
            while (not reader.atEnd()) and (not reader.hasError()):
                token = reader.readNext()
                if token == QXmlStreamReader.StartElement:
                    if reader.name() == "cinemol_movie_script":
                        self.bookmarks.read_xml(reader)
            if reader.hasError():
                print "Error reading xml file"
            else:
                self.statusBar().showMessage("Loaded movie script file" + file_name, 5000)
            script_file.close()
    
    @QtCore.Slot(bool)
    def on_actionSave_movie_script_triggered(self, checked):
        if len(self.bookmarks) < 1:
            QMessageBox.warning(self, "No key frames found", 
                                """You must create some bookmarks(key frames)
before you can save a movie script.""")
            return
        file_name = QFileDialog.getSaveFileName(
                self, 
                "Save movie script file", 
                None,
                self.tr("XML files (*.xml)"))[0]
        if file_name == "":
            return
        script_file = QFile(file_name)
        if script_file.open(QIODevice.WriteOnly):
            writer = QXmlStreamWriter(script_file)
            writer.setAutoFormatting(True)
            writer.setAutoFormattingIndent(2)
            writer.writeStartDocument()
            self.bookmarks.write_xml(writer)
            writer.writeEndDocument()
            script_file.close()
            self.statusBar().showMessage("Saved movie script file" + file_name, 5000)
        
    @QtCore.Slot(bool)
    def on_actionMeasure_fps_triggered(self, checked):
        self.ui.glCanvas.renderer.restart_fps()
        for frame in self.bookmarks.play(real_time=False):
            self.camera.state = frame.camera_state
            # self.ui.glCanvas.update()
            self.ui.glCanvas.repaint()
            # QCoreApplication.processEvents() # To avoid locking up the application
        fps = self.ui.glCanvas.renderer.fps()
        self.statusBar().showMessage("Frames per second = %f" % fps, 0)
    
    @QtCore.Slot(bool)
    def on_actionQuit_triggered(self, checked):
        self.close()
        
    @QtCore.Slot(int, int)
    def resize_canvas(self, w, h):
        dx = w - self.ui.glCanvas.width()
        dy = h - self.ui.glCanvas.height()
        x2 = self.width() + dx
        y2 = self.height() + dy
        self.resize(x2, y2)
        
    @QtCore.Slot(str)
    def parse_size_box_string(self, value):
        match = re.search('(\d+)x(\d+)', value)
        if match:
            w = int(match.group(1))
            h = int(match.group(2))
            self.size_dialog.ui.widthBox.setValue(w)
            self.size_dialog.ui.heightBox.setValue(h)
        
    @QtCore.Slot(bool)
    def on_actionPlay_movie_triggered(self, checked):
        for frame in self.bookmarks.play(real_time=True):
            self.camera.state = frame.camera_state
            self.statusBar().showMessage("Bookmark " + 
                                         str(frame.key_frame_number) + 
                                         "; movie frame " + 
                                         str(frame.frame_number),
                                         500)
            self.ui.glCanvas.update()
        self.statusBar().showMessage("Finished playing movie", 
                                     1000)

    @QtCore.Slot(bool)
    def on_actionAdd_new_bookmark_triggered(self, checked):
        self.bookmarks.append(KeyFrame(self.camera.state))
        self.statusBar().showMessage("Added bookmark number " 
                                     + str(self.bookmarks.current_key_frame_index + 1), 
                                     4000)

    @QtCore.Slot(bool)
    def on_actionGo_to_previous_bookmark_triggered(self, checked):
        if len(self.bookmarks) < 1:
            return
        self.bookmarks.decrement()
        self.camera.state = self.bookmarks.current_key_frame.camera_state
        self.ui.glCanvas.update()
        self.statusBar().showMessage("Back to bookmark " 
                                     + str(self.bookmarks.current_key_frame_index + 1), 
                                     1000)
        
    @QtCore.Slot(bool)
    def on_actionGo_to_next_bookmark_triggered(self, checked):
        if len(self.bookmarks) < 1:
            return
        self.bookmarks.increment()
        self.camera.state = self.bookmarks.current_key_frame.camera_state
        self.ui.glCanvas.update()
        self.statusBar().showMessage("Forward to bookmark " 
                                     + str(self.bookmarks.current_key_frame_index + 1), 
                                     1000)
        
    @QtCore.Slot(bool)
    def on_actionClear_all_bookmarks_triggered(self, checked):
        self.bookmarks.clear()
        self.statusBar().showMessage("All bookmarks deleted!",
                                     5000)
        
    @QtCore.Slot(bool)
    def on_actionSet_size_triggered(self, checked):
        old_size = self.ui.glCanvas.size()
        dialog = self.size_dialog
        dialog.blockSignals(True)
        dialog.ui.widthBox.setValue(old_size.width())
        dialog.ui.heightBox.setValue(old_size.height())
        dialog.blockSignals(False)
        dialog.exec_()
        if dialog.result() == QDialog.Accepted:
            pass # keep this size
            # print "Accepted"
        else:
            self.resize_canvas(old_size.width(), old_size.height())

    @QtCore.Slot(bool)
    def on_actionSave_movie_triggered(self, checked):
        if len(self.bookmarks) < 1:
            QMessageBox.warning(self, "No key frames found", 
                                """You must create some bookmarks(key frames)
before you can save a movie.""")
            return
        base_file_name = QFileDialog.getSaveFileName(
                self, 
                "Save movie frame images", 
                None, 
                # PNG format silently does not work
                self.tr("images(*.ppm *.tif *.jpg)"))[0]
        if base_file_name == "":
            return
        frame_number = 0
        froot, fext = os.path.splitext(base_file_name)
        for frame in self.bookmarks.play(real_time=False):
            num_string = '_%03d' % (frame_number + 1)
            file_name = froot + num_string + fext
            self.camera.state = frame.camera_state
            # TODO - potential OpenGL thread problems
            self.ui.glCanvas.update()
            self.ui.glCanvas.repaint()
            QCoreApplication.processEvents() # To avoid locking up the application
            image = self.ui.glCanvas.grabFrameBuffer()
            self.statusBar().showMessage("Saving frame " + file_name,
                                         500)
            image.save(file_name)
            frame_number += 1
        self.statusBar().showMessage("Done saving movie frames.",
                                     5000)
        
    @QtCore.Slot(bool)
    def on_actionSave_Lenticular_Series_triggered(self, checked):
        file_name = QFileDialog.getSaveFileName(
                self, 
                "Save lenticular series", 
                None, 
                # PNG format silently does not work
                self.tr("images(*.tif)"))[0]
        if file_name == "":
            return
        self.ui.glCanvas.save_lenticular_series(file_name=file_name, 
                                                angle=15.0*pi/180.0, 
                                                count=18)
        self.statusBar().showMessage("Done saving lenticular series.",
                                     5000)
        
    def set_stereo_mode(self, mode, checked):
        if checked:
            self.ui.glCanvas.renderer.stereo_mode = mode
        else:
            # Turn off one stereo mode, turn on Mono
            self.ui.glCanvas.renderer.stereo_mode = stereo3d.Mono()
            self.ui.actionMono_None.setChecked(True)
        self.ui.glCanvas.update()
        
    @QtCore.Slot(bool)
    def on_actionMono_None_triggered(self, checked):
        # If the user clicks on Mono, always use mono, even if it was already checked
        self.set_stereo_mode(stereo3d.Mono(), checked)

    @QtCore.Slot(bool)
    def on_actionRight_Left_cross_eye_triggered(self, checked):
        print "right left", checked
        self.set_stereo_mode(stereo3d.RightLeft(), checked)

    @QtCore.Slot(bool)
    def on_actionLeft_Right_parallel_triggered(self, checked):
        self.set_stereo_mode(stereo3d.LeftRight(), checked)

    @QtCore.Slot(bool)
    def on_actionLeft_eye_view_triggered(self, checked):
        self.set_stereo_mode(stereo3d.Left(), checked)

    @QtCore.Slot(bool)
    def on_actionRight_eye_view_triggered(self, checked):
        self.set_stereo_mode(stereo3d.Right(), checked)

    @QtCore.Slot(bool)
    def on_actionRed_Cyan_anaglyph_triggered(self, checked):
        self.set_stereo_mode(stereo3d.RedCyan(), checked)

    @QtCore.Slot(bool)
    def on_actionGreen_Magenta_anaglyph_triggered(self, checked):
        self.set_stereo_mode(stereo3d.GreenMagenta(), checked)

    @QtCore.Slot(bool)
    def on_actionSwap_Eyes_triggered(self, checked):
        self.camera.swap_eyes = checked
        self.ui.glCanvas.update()

    @QtCore.Slot(bool)
    def on_actionSave_image_triggered(self, checked):
        print "save image"
        file_name = QFileDialog.getSaveFileName(
                self, 
                "Save screen shot", 
                None, 
                # PNG format silently does not work
                self.tr("images(*.jpg *.tif)"))[0]
        if file_name == "":
            return
        self.ui.glCanvas.save_image(file_name)

    @QtCore.Slot(str)
    def load_pdb_file(self, file_name):
        try:
            self.statusBar().showMessage("Loading PDB file " 
                             + file_name
                             + "...",
                             0)
            command.zap()
            command.load(file_name)
            self.statusBar().showMessage("Finished loading PDB file " 
                             + file_name,
                             2000)   
            command.refresh()     
            self.recent_files.add_file(file_name)
        except:
            self.statusBar().showMessage("Error loading PDB file " 
                             + file_name,
                             2000)   
            raise     
        
    @QtCore.Slot()
    def on_actionOpen_triggered(self):
        settings = QSettings()
        search_dir = None
        if settings.contains("pdb_input_dir"):
            search_dir = settings.value("pdb_input_dir")
        file_name = QFileDialog.getOpenFileName(
                self, 
                "Open PDB file", 
                search_dir,
                self.tr("PDB Files(*.pdb *.pdb.gz)"))[0]
        if file_name == "":
            return
        try:
            self.load_pdb_file(file_name)
            # Remember the directory where we found this
            pdb_input_dir = QFileInfo(file_name).absoluteDir().canonicalPath()
            settings.setValue("pdb_input_dir", pdb_input_dir)
        except:
            QMessageBox.warning(self, "Problem opening file", 
                                file_name)
            raise

            