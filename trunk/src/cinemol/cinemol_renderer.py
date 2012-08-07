'''
Created on Jun 19, 2012

@author: brunsc
'''

import stereo3d
from skybox import SkyBox
from imposter import sphereImposterShaderProgram
from camera import CameraPosition
from rotation import Rotation
import glrenderer
from PySide import QtCore
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GL.ARB.seamless_cube_map import *
from OpenGL.raw.GL.EXT.framebuffer_sRGB import glInitFramebufferSrgbEXT
from OpenGL.GL.EXT.framebuffer_sRGB import *
from OpenGL.GL.EXT.texture_sRGB import *

class CinemolRenderer(glrenderer.GlRenderer):
    def __init__(self):
        glrenderer.GlRenderer.__init__(self)
        self.camera_position = CameraPosition()
        self.actors = []
        self.shader = sphereImposterShaderProgram
        self.background_color = [0.8, 0.8, 1.0, 0.0] # sky blue
        self.stereo_mode = stereo3d.Mono()
        self.sky_box = SkyBox()
        
    def init_gl(self):
        # print "init_gl"
        if glInitSeamlessCubeMapARB():
            glEnable(GL_TEXTURE_CUBE_MAP_SEAMLESS)
        if glInitFramebufferSrgbEXT():
            glEnable(GL_FRAMEBUFFER_SRGB_EXT)
        # print glGetString(GL_EXTENSIONS)

        glEnable(GL_DEPTH_TEST)
        bg = self.background_color
        glClearColor(bg[0], bg[1], bg[2], bg[3])
        glShadeModel(GL_SMOOTH)
        glEnable(GL_COLOR_MATERIAL)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glMaterialfv(GL_FRONT, GL_SPECULAR, [1.0, 1.0, 1.0, 1.0])
        glMaterialfv(GL_FRONT, GL_SHININESS, [100.0])
        glLightfv(GL_LIGHT0, GL_POSITION, [222.0, 512.0, 293.0, 0.0])
        glLightfv(GL_LIGHT0, GL_DIFFUSE, [0.8, 0.8, 0.8, 1.0])
        glLightfv(GL_LIGHT0, GL_SPECULAR, [1.0, 1.0, 1.0, 1.0])
        glLightModelfv(GL_LIGHT_MODEL_AMBIENT, [0.15, 0.15, 0.15, 0.0])
        glEnable(GL_CULL_FACE)
        self.sky_box.init_gl()
        for actor in self.actors:
            actor.init_gl()
        self.shader.init_gl()
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    def resize_gl(self, w, h):
        self.camera_position.set_window_size_in_pixels(w, h)
        self.update()
        
    def render_background(self):
        glDrawBuffer(GL_BACK)
        glColorMask(True, True, True, True)
        glClear(GL_COLOR_BUFFER_BIT)
        
    def render_scene(self, camera):
        glClear(GL_DEPTH_BUFFER_BIT)
        self.sky_box.paint_gl(camera)
        self.shader.zNear = camera.zNear
        self.shader.zFar = camera.zFar
        self.shader.zFocus = camera.zFocus
        self.shader.background_color = self.background_color
        self.shader.eye_shift = camera.eye_shift_in_ground
        for actor in self.actors:
            actor.paint_gl()

    def paint_gl(self):
        self.render_background()
        for camera in self.stereo_mode.views(self.camera_position):
            self.render_scene(camera)
                
    @QtCore.Slot(float)
    def increment_zoom(self, ratio):
        self.camera_position.increment_zoom(ratio)
        self.update()

    @QtCore.Slot(Rotation)
    def increment_rotation(self, r):
        self.camera_position.increment_rotation(r)
        self.update()
        
    @QtCore.Slot(int, int, int)
    def center_pixel(self, x, y, z):
        self.camera_position.center_pixel(x, y, z)
        self.update()
        
    @QtCore.Slot(int, int, int)
    def translate_pixel(self, x, y, z):
        self.camera_position.translate_pixel(x, y, z)
        self.update()