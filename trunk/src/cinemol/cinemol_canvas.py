'''
Created on Jun 19, 2012

@author: brunsc
'''

from trackball import Trackball
from rotation import Vec3, Rotation
from PySide.QtOpenGL import QGLWidget
from PySide.QtCore import *
from PySide.QtGui import *
from PySide import QtCore

class CinemolCanvas(QGLWidget):
    # Singleton thread for all OpenGL actions
    
    def __init__(self, parent=None):
        QGLWidget.__init__(self, parent)
        self.setAutoBufferSwap(False)
        self.resize(640, 480)
        self.opengl_thread = QThread()
        QCoreApplication.instance().aboutToQuit.connect(self.clean_up_before_quit)
        self.trackball = Trackball()
        self.preferredSize = None
        self.setFocusPolicy(Qt.WheelFocus)
        
    # delegate opengl tasks to separate non-qt-gui Renderer object
    def set_gl_renderer(self, renderer):
        self.renderer = renderer
        self.renderer.set_gl_widget(self)
        bUseSeparateOpenGLThread = False
        if bUseSeparateOpenGLThread:
            self.renderer.moveToThread(self.opengl_thread)
            self.opengl_thread.start()
        self.trackball.rotation_incremented.connect(self.renderer.increment_rotation)
        self.trackball.zoom_incremented.connect(self.renderer.increment_zoom)
        self.trackball.pixel_translated.connect(self.renderer.translate_pixel)
        self.trackball.pixel_centered.connect(self.renderer.center_pixel)

    def paintEvent(self, event):
        self.doneCurrent()
        self.paint_requested.emit()
        
    def resizeEvent(self, event):
        self.doneCurrent()
        sz = event.size()
        self.resize_requested.emit(sz.width(), sz.height())
        
    def sizeHint(self):
        if self.preferredSize is None:
            return QGLWidget.sizeHint(self)
        return self.preferredSize
        
    @QtCore.Slot(int, int)
    def special_resize(self, w, h):
        self.preferredSize = QSize(w, h)
        self.resize(w, h)

    @QtCore.Slot()
    def clean_up_before_quit(self):
        self.opengl_thread.quit()
        self.opengl_thread.wait()

    paint_requested = QtCore.Signal()
    resize_requested = QtCore.Signal(int, int)
    save_image_requested = QtCore.Signal(str)
    save_lenticular_series_requested = QtCore.Signal(str, float, int)
    
    def save_image(self, file_name):
        self.save_image_requested.emit(file_name)
        
    def save_lenticular_series(self, file_name, angle, count=18):
        self.save_lenticular_series_requested.emit(file_name, angle, count)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Left:        
            r = Rotation().set_from_angle_about_unit_vector(-0.05, [0, 0, -1])
            self.trackball.rotation_incremented.emit(r)
        elif event.key() == Qt.Key_Right:
            r = Rotation().set_from_angle_about_unit_vector( 0.05, [0, 0, -1])
            self.trackball.rotation_incremented.emit(r)
        elif event.key() == Qt.Key_Up:
            self.trackball.pixel_translated.emit(0, 0, 50);
        elif event.key() == Qt.Key_Down:
            self.trackball.pixel_translated.emit(0, 0, -50);
        QGLWidget.keyPressEvent(self, event) # not my event
        
    # Delegate mouse events to trackball class
    def mouseMoveEvent(self, event):
        self.trackball.mouseMoveEvent(event, self.size())
        
    def mousePressEvent(self, event):
        self.trackball.mousePressEvent(event)
        
    def mouseReleaseEvent(self, event):
        self.trackball.mouseReleaseEvent(event)
        
    def mouseDoubleClickEvent(self, event):
        self.trackball.mouseDoubleClickEvent(event, self.size())
        
    def wheelEvent(self, event):
        self.trackball.wheelEvent(event)
