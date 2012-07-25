from shader import ShaderProgram
import shader
from PySide import QtCore
from PySide.QtCore import *
from OpenGL.GL import *
import numpy
from math import pi, cos, sin
import os


class SphereImposterShaderProgram(ShaderProgram):
    def __init__(self):
        ShaderProgram.__init__(self)
        this_dir, this_filename = os.path.split(__file__)
        self.vertex_shader = open(os.path.join(this_dir, "shaders/sphere_vtx.glsl")).read()
        self.fragment_shader = open(os.path.join(this_dir, "shaders/sphere_frg.glsl")).read()
        self.atom_scale = 1.0
        
    def __enter__(self):
        ShaderProgram.__enter__(self)
        # print self.zNear, type(self.zNear), self.shader_program, glGetUniformLocation(self.shader_program, "zNear")
        glUniform1f(glGetUniformLocation(self.shader_program, "zNear"), self.zNear)
        glUniform1f(glGetUniformLocation(self.shader_program, "zFar"), self.zFar)
        glUniform1f(glGetUniformLocation(self.shader_program, "eye_shift"), self.eye_shift)
        bg = self.background_color
        glUniform4f(glGetUniformLocation(self.shader_program, "background_color"), 
                    bg[0], bg[1], bg[2], bg[3])
        glUniform1f(glGetUniformLocation(self.shader_program, "atom_scale"), self.atom_scale)
        return self


sphereImposterShaderProgram = SphereImposterShaderProgram()

cylinderImposterShaderProgram = shader.GreenShaderProgram()


class VertexArrayTest:
    def __init__(self):
        # self.vertex_array = numpy.array([1.0,1.0,0.0,1.0, -1.0,1.0,0.0,1.0, -1.0,-1.0,0.0,1.0], dtype='float32')
        self.vertex_array = numpy.array([0.0,0.0,0.0,1.0, 0.0,0.0,0.0,1.0, 0.0,0.0,0.0,1.0], dtype='float32')
        self.normal_array = numpy.array([1.0,1.0,1.0, -1.0,1.0,1.0, -1.0,-1.0,1.0], dtype='float32')
        self.color_array = numpy.array([0.0,1.0,0.0,1.0, 0.0,1.0,0.0,1.0, 0.0,1.0,0.0,1.0], dtype='float32')
        self.index_array = numpy.array([0, 1, 2], dtype='uint32')
        
    def init_gl(self):
        glPushClientAttrib(GL_CLIENT_VERTEX_ARRAY_BIT)
        # Vertices
        self.vertex_buffer = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vertex_buffer)
        glBufferData(GL_ARRAY_BUFFER, self.vertex_array, GL_STATIC_DRAW)
        # Normals
        self.normal_buffer = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.normal_buffer)
        glBufferData(GL_ARRAY_BUFFER, self.normal_array, GL_STATIC_DRAW)
        # Colors
        self.color_buffer = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.color_buffer)
        glBufferData(GL_ARRAY_BUFFER, self.color_array, GL_STATIC_DRAW)
        # Vertex indices
        self.index_buffer = glGenBuffers(1)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.index_buffer)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, self.index_array, GL_STATIC_DRAW)
        glPopClientAttrib()
        
    def paint_gl(self):
        with sphereImposterShaderProgram:
            glPushClientAttrib(GL_CLIENT_VERTEX_ARRAY_BIT)
            # Vertices
            glBindBuffer(GL_ARRAY_BUFFER, self.vertex_buffer)
            glEnableClientState(GL_VERTEX_ARRAY)
            glVertexPointer(4, GL_FLOAT, 0, None)
            # Normals
            glBindBuffer(GL_ARRAY_BUFFER, self.normal_buffer)
            glEnableClientState(GL_NORMAL_ARRAY)
            glNormalPointer(GL_FLOAT, 0, None)
            # Colors
            glBindBuffer(GL_ARRAY_BUFFER, self.color_buffer)
            glEnableClientState(GL_COLOR_ARRAY)
            glColorPointer(4, GL_FLOAT, 0, None)
            # Vertex indices
            glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.index_buffer)
            glColor3f(1,0,0)
            glDrawElements(GL_TRIANGLES, 3, GL_UNSIGNED_INT, None)
            # glDrawArrays(GL_TRIANGLES, 0, 3)
            glPopClientAttrib()
            

class ImposterQuadArray:
    def __init__(self):
        self.vertex_count = 4 # one quadrilateral per sphere
        self.triangle_count = self.vertex_count - 2
    
    
class SphereImposterArray(QObject):
    def __init__(self, spheres):
        self.vertex_count = 4 # one quadrilateral per sphere
        self.triangle_count = self.vertex_count - 2
        self.normal_offsets = []
        # Compute unit offsets from center of sphere to imposter polygon vertices
        # Scaled so apothem length is 1.0
        angle = 0.0
        d_angle = 2.0 * pi / self.vertex_count # to next vertex of polygon
        apothem_length = 1.0
        R = circumradius_length = apothem_length / cos(pi/self.vertex_count)
        for v in range(self.vertex_count):
            n = [R * cos(angle), R * sin(angle)]
            self.normal_offsets.append(n, )
            angle += d_angle
        self.vertex_array = numpy.array(list(self._vertex_generator(spheres)), dtype='float32')
        self.normal_array = numpy.array(list(self._normal_generator(spheres)), dtype='float32')
        self.color_array = numpy.array(list(self._color_generator(spheres)), dtype='float32')
        self.index_array = numpy.array(list(self._index_generator(spheres)), dtype='uint32')
        self.vertex_buffer = 0
        self.color_buffer = 0
        self.normal_buffer = 0
        self.index_buffer = 0
        self.is_initialized = False
        
    def __del__(self):
        glDeleteBuffers(1, self.vertex_buffer)
        glDeleteBuffers(1, self.color_buffer)
        glDeleteBuffers(1, self.index_buffer)
        glDeleteBuffers(1, self.normal_buffer)
        
    def init_gl(self):
        if self.is_initialized:
            return
        glPushClientAttrib(GL_CLIENT_VERTEX_ARRAY_BIT)
        # Vertices
        self.vertex_buffer = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vertex_buffer)
        glBufferData(GL_ARRAY_BUFFER, self.vertex_array, GL_STATIC_DRAW)
        # Normals
        self.normal_buffer = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.normal_buffer)
        glBufferData(GL_ARRAY_BUFFER, self.normal_array, GL_STATIC_DRAW)
        # Colors
        self.color_buffer = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.color_buffer)
        glBufferData(GL_ARRAY_BUFFER, self.color_array, GL_STATIC_DRAW)
        # Vertex indices
        self.index_buffer = glGenBuffers(1)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.index_buffer)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, self.index_array, GL_STATIC_DRAW)
        glPopClientAttrib()
        self.is_initialized = True
                
    def paint_gl(self):
        with sphereImposterShaderProgram:
            if not self.is_initialized:
                self.init_gl()
            glPushClientAttrib(GL_CLIENT_VERTEX_ARRAY_BIT)
            # Vertices
            glBindBuffer(GL_ARRAY_BUFFER, self.vertex_buffer)
            glEnableClientState(GL_VERTEX_ARRAY)
            glVertexPointer(4, GL_FLOAT, 0, None)
            # Normals
            glBindBuffer(GL_ARRAY_BUFFER, self.normal_buffer)
            glEnableClientState(GL_NORMAL_ARRAY)
            glNormalPointer(GL_FLOAT, 0, None)
            # Colors
            glBindBuffer(GL_ARRAY_BUFFER, self.color_buffer)
            glEnableClientState(GL_COLOR_ARRAY)
            glColorPointer(3, GL_FLOAT, 0, None)
            # Vertex indices
            glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.index_buffer)
            glDrawElements(GL_TRIANGLES, len(self.vertex_array), GL_UNSIGNED_INT, None)
            glPopClientAttrib()
        
    def _vertex_generator(self, spheres):
        for sphere in spheres:
            p = sphere.center
            # Every vertex has the sphere center as its main coordinate
            for v in range(self.vertex_count):
                yield p[0]
                yield p[1]
                yield p[2]
                yield 1.0
            
    def _color_generator(self, spheres):
        for sphere in spheres:
            p = sphere.color
            for v in range(self.vertex_count):
                yield p[0]
                yield p[1]
                yield p[2]
                # yield 1.0
            
    def _normal_generator(self, spheres):
        for sphere in spheres:
            r = sphere.radius
            # normal contains unit offset from center in x,y, and radius in z
            for v in range(self.vertex_count):
                yield self.normal_offsets[v][0] # x offset from center
                yield self.normal_offsets[v][1] # y offset from center
                yield r # sphere radius
                
    def _index_generator(self, spheres):
        "triangle vertex indices"
        vertex_offset = 0
        for sphere in spheres:
            v0 = vertex_offset + 0 # index of first vertex in polygon
            vn = vertex_offset + self.vertex_count - 1 # index of final vertex in polygon
            for t in range(self.triangle_count):
                yield v0 + t
                yield v0 + t + 1
                yield vn
            vertex_offset += self.vertex_count


class CylinderImposterShaderProgram(ShaderProgram):
    pass # TODO


class CylinderImposterArray:
    def __init__(self, cylinders):
        self.cylinders = cylinders
    
    def init_gl(self):
        cylinderImposterShaderProgram.init_gl()

    def paint_gl(self):
        with cylinderImposterShaderProgram:
            for c in self.cylinders:
                glBegin(GL_TRIANGLES)
                glVertex3f(c.radius,0,-c.height/2.0)
                glVertex3f(-c.radius,0, c.height/2.0)
                glVertex3f(c.radius,0, c.height/2.0)
                glVertex3f(c.radius,0,-c.height/2.0)
                glVertex3f(-c.radius,0, -c.height/2.0)
                glVertex3f(-c.radius,0, c.height/2.0)
                # TODO
                glEnd()
   
