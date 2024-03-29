'''
Created on Jun 19, 2012

@author: brunsc
'''

from cinemol.model import model
import stereo3d
from skybox import SkyBox
# from imposter import sphereImposterShaderProgram
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
        # self.shader = sphereImposterShaderProgram
        self.background_color = [0.8, 0.8, 1.0, 0.0] # sky blue
        self.stereo_mode = stereo3d.Mono()
        self.sky_box = SkyBox()
        # direction to skybox sun
        self.light_direction = [0.352, 0.812, 0.465, 0.0]
        
    def init_gl(self):
        # print "init_gl"
        bPrintGLInfo = False
        if bPrintGLInfo:
            print "GL Vendor:", glGetString(GL_VENDOR)
            print "GL Renderer:", glGetString(GL_RENDERER)
            print "GL Version (string):", glGetString(GL_VERSION)
            # print glGetInteger(GL_MINOR_VERSION) # exception!?!?
            # print "GL Version (number):", "%d.%d" % (glGetInteger(GL_MAJOR_VERSION), glGetInteger(GL_MINOR_VERSION))
            print "GLSL Version:", glGetString(GL_SHADING_LANGUAGE_VERSION)
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
        glLightfv(GL_LIGHT0, GL_POSITION, self.light_direction)
        glLightfv(GL_LIGHT0, GL_DIFFUSE, [0.8, 0.8, 0.8, 1.0])
        glLightfv(GL_LIGHT0, GL_SPECULAR, [1.0, 1.0, 1.0, 1.0])
        glLightModelfv(GL_LIGHT_MODEL_AMBIENT, [0.15, 0.15, 0.15, 0.0])
        glEnable(GL_CULL_FACE)
        self.sky_box.init_gl()
        for actor in self.actors:
            actor.init_gl()
        for rep in model.representations.values():
            # print "init_gl on a representation"
            rep.init_gl()
        # self.shader.init_gl()
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
        self.sky_box.paint_gl(camera)
        """
        self.shader.zNear = camera.zNear
        self.shader.zFar = camera.zFar
        self.shader.zFocus = camera.zFocus
        self.shader.background_color = self.background_color
        self.shader.eye_shift = camera.eye_shift_in_ground
        """
        glEnable(GL_DEPTH_TEST)
        # glDepthFunc(GL_LEQUAL)
        glDepthMask(True)
        glClear(GL_DEPTH_BUFFER_BIT)
        for actor in self.actors:
            actor.paint_gl(camera, self)
        for rep in model.representations.values():
            rep.paint_gl(camera, self)

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
