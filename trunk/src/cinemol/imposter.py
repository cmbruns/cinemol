
from shader import ShaderProgram
import shader
from PySide import QtCore
from PySide.QtCore import *
from OpenGL.GL import *
import numpy
import itertools
from math import pi, cos, sin
import os


class SphereImposterShaderProgram(ShaderProgram):
    def __init__(self):
        ShaderProgram.__init__(self)
        this_dir = os.path.split(__file__)[0]
        self.vertex_shader = open(os.path.join(this_dir, "shaders/sphere_vtx.glsl")).read()
        self.fragment_shader = open(os.path.join(this_dir, "shaders/sphere_frg.glsl")).read()
        # experimental geometry shader
        self.geometry_shader = """
        #version 120
        #extension GL_EXT_geometry_shader4 : enable
         
        void main() {
          for(int i = 0; i < gl_VerticesIn; ++i) {
            gl_FrontColor = gl_FrontColorIn[i];
            gl_Position = gl_PositionIn[i];
            EmitVertex();
          }
        }
        """
        self.atom_scale = 1.0
        
    def __enter__(self):
        if not self.is_initialized:
            self.init_gl()
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
    
    def init_gl(self):
        self.gs = glCreateShader(GL_GEOMETRY_SHADER)
        glShaderSource(self.gs, self.geometry_shader)
        glCompileShader(self.gs)
        log = glGetShaderInfoLog(self.gs)
        if log:
            print "Geometry Shader:", log
        self.shader_program = glCreateProgram()
        # glAttachShader(self.shader_program, self.gs)
        ShaderProgram.init_gl(self)


# sphereImposterShaderProgram = SphereImposterShaderProgram()

cylinderImposterShaderProgram = shader.GreenShaderProgram()

passThroughShaderProgram = shader.ShaderProgram()

class ImposterQuadArray:
    def __init__(self):
        self.vertex_count = 4 # one quadrilateral per sphere
        self.triangle_count = self.vertex_count - 2
    
    
class SphereImposterArray(QObject):
    def __init__(self, spheres):
        # print "SphereImposterArray()", len(spheres)
        self.vertex_count = 4 # one quadrilateral per sphere
        self.triangle_count = self.vertex_count - 2
        self.normal_offsets = []
        self.spheres = []
        self.spheres[:] = spheres[:]
        # Compute unit offsets from center of sphere to imposter polygon vertices
        # Scaled so apothem length is 1.0
        angle = 0.0
        d_angle = 2.0 * pi / self.vertex_count # to next vertex of polygon
        apothem_length = 1.0
        circumradius_length = apothem_length / cos(pi/self.vertex_count)
        R = circumradius_length
        for v in range(self.vertex_count):
            n = [R * cos(angle), R * sin(angle)]
            self.normal_offsets.append(n, )
            angle += d_angle
        self.vertex_array = numpy.array(list(self._vertex_generator(spheres)), dtype='float32')
        self.normal_array = numpy.array(list(self._normal_generator(spheres)), dtype='float32')
        self.color_array = numpy.array(list(self._color_generator(spheres)), dtype='float32')
        self.index_array = numpy.array(list(self._index_generator(spheres)), numpy.uint32)
        # self.index_array = list(self._index_generator(spheres))
        self.vertex_buffer = 0
        self.color_buffer = 0
        self.normal_buffer = 0
        self.index_buffer = 0
        self.shader = SphereImposterShaderProgram()
        self.is_initialized = False
        
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
                
    def paint_gl(self, camera=None, renderer=None):
        # with passThroughShaderProgram:
        self.shader.zNear = camera.zNear
        self.shader.zFar = camera.zFar
        self.shader.zFocus = camera.zFocus
        self.shader.background_color = renderer.background_color
        self.shader.eye_shift = camera.eye_shift_in_ground
        with self.shader:
            if not self.is_initialized:
                self.init_gl()
            glPushClientAttrib(GL_CLIENT_VERTEX_ARRAY_BIT)
            # Colors
            glBindBuffer(GL_ARRAY_BUFFER, self.color_buffer)
            glEnableClientState(GL_COLOR_ARRAY)
            glColorPointer(3, GL_FLOAT, 0, None)
            # Vertices
            glBindBuffer(GL_ARRAY_BUFFER, self.vertex_buffer)
            glEnableClientState(GL_VERTEX_ARRAY)
            glVertexPointer(4, GL_FLOAT, 0, None)
            # Normals
            glBindBuffer(GL_ARRAY_BUFFER, self.normal_buffer)
            glEnableClientState(GL_NORMAL_ARRAY)
            glNormalPointer(GL_FLOAT, 0, None)
            # Vertex indices
            glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.index_buffer)
            glDrawElements(GL_TRIANGLES, len(self.vertex_array), GL_UNSIGNED_INT, None)
            glPopClientAttrib()

    def update_atom_colors(self):
        ix = 0
        for sphere in self.spheres:
            color = sphere.color
            for vertex in range(self.vertex_count):
                for rgb in range(3):
                    self.color_array[ix] = color[rgb]
                    ix += 1
        if self.is_initialized:
            # print "updating atom colors"
            glPushClientAttrib(GL_CLIENT_VERTEX_ARRAY_BIT)
            glBindBuffer(GL_ARRAY_BUFFER, self.color_buffer)
            glBufferData(GL_ARRAY_BUFFER, self.color_array, GL_STATIC_DRAW)
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
                # print p
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


class SharedGLBufferObjects(QObject):
    """
    Opengl buffer objects to be shared between representations
        One list of atom center positions
        One list of atom colors
        One list of atom van der Waals radii
    """
    def __init__(self, atoms):
        self.center_array = numpy.array(list(itertools.chain.from_iterable(
                [atom.center for atom in atoms])), dtype='float32')
        self.color_array = numpy.array(list(itertools.chain.from_iterable(
                [atom.color for atom in atoms])), dtype='float32')
        self.vdw_array = numpy.array(list(itertools.chain.from_iterable(
                [[atom.radius, atom.radius, atom.radius] for atom in atoms])), dtype='float32')
        self.center_buffer = 0
        self.color_buffer = 0;
        self.vdw_buffer = 0;
        self.is_initialized = False
        self.atoms = atoms
        
    def init_gl(self):
        if self.is_initialized:
            return
        glPushClientAttrib(GL_CLIENT_VERTEX_ARRAY_BIT)
        # Atom center positions
        self.center_buffer = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.center_buffer)
        glBufferData(GL_ARRAY_BUFFER, self.center_array, GL_STATIC_DRAW)
        # van der Waals radii in normals
        self.vdw_buffer = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vdw_buffer)
        glBufferData(GL_ARRAY_BUFFER, self.vdw_array, GL_STATIC_DRAW)
        # Colors
        self.color_buffer = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.color_buffer)
        glBufferData(GL_ARRAY_BUFFER, self.color_array, GL_STATIC_DRAW)
        #
        glPopClientAttrib()
        self.is_initialized = True
        
    def paint_gl(self):
        if not self.is_initialized:
            self.init_gl()
        # Colors
        glBindBuffer(GL_ARRAY_BUFFER, self.color_buffer)
        glEnableClientState(GL_COLOR_ARRAY)
        glColorPointer(3, GL_FLOAT, 0, None)
        # Vertices
        glBindBuffer(GL_ARRAY_BUFFER, self.center_buffer)
        glEnableClientState(GL_VERTEX_ARRAY)
        glVertexPointer(4, GL_FLOAT, 0, None)
        # van der Waals radii stuffed into normals
        glBindBuffer(GL_ARRAY_BUFFER, self.vdw_buffer)
        glEnableClientState(GL_NORMAL_ARRAY)
        glNormalPointer(GL_FLOAT, 0, None)
        
    def update_atom_colors(self, atoms):
        self.color_array = numpy.array(
                [atom.color for atom in atoms], dtype='float32')
        if self.is_initialized:
            # print "updating atom colors"
            glPushClientAttrib(GL_CLIENT_VERTEX_ARRAY_BIT)
            glBindBuffer(GL_ARRAY_BUFFER, self.color_buffer)
            glBufferData(GL_ARRAY_BUFFER, self.color_array, GL_STATIC_DRAW)
            glPopClientAttrib()


class NewSphereShader(object):
    def __init__(self):
        this_dir = os.path.split(__file__)[0]
        self.vertex_shader_string = open(os.path.join(
                this_dir,
                "shaders/sphere2_vrtx.glsl")).read()
        self.geometry_shader_string = open(os.path.join(
                this_dir,
                "shaders/sphere2_geom.glsl")).read()
        self.fragment_shader_string = open(os.path.join(
                this_dir,
                "shaders/sphere2_frag.glsl")).read()
        self.shader_program = 0
        self.previous_program = 0
        self.radius_scale = 1.0
        self.radius_offset = 0.0
        self.imposter_edge_count = 4
        self.is_initialized = False
        
    def __enter__(self):
        if not self.is_initialized:
            self.init_gl()
        self.previous_program = glGetIntegerv(GL_CURRENT_PROGRAM)
        glUseProgram(self.shader_program)
        print self.shader_program
        print self.vs
        print self.fs
        glUniform1i(glGetUniformLocation(self.shader_program, "imposter_edge_count"), self.imposter_edge_count)
        glUniform1f(glGetUniformLocation(self.shader_program, "radius_offset"), self.radius_offset)
        loc1 = glGetUniformLocation(self.shader_program, "radius_scale")
        glUniform1f(loc1, self.radius_scale)
        return self
        
    def __exit__(self, type, value, tb):
        glUseProgram(self.previous_program)

    def _init_shader(self, string, shader_type):
        shader = glCreateShader(shader_type)
        glShaderSource(shader, string)
        glCompileShader(shader)
        log = glGetShaderInfoLog(shader)
        if log:
            print "Shader error:", log
        return shader
    
    def init_gl(self):
        if self.is_initialized:
            return
        self.vs = self._init_shader(
                    self.vertex_shader_string, GL_VERTEX_SHADER)
        self.gs = self._init_shader(
                    self.geometry_shader_string, GL_GEOMETRY_SHADER)
        self.fs = self._init_shader(
                    self.fragment_shader_string, GL_FRAGMENT_SHADER)
        if self.shader_program == 0:
            self.shader_program = glCreateProgram()
        glAttachShader(self.shader_program, self.vs)
        glAttachShader(self.shader_program, self.gs)
        glAttachShader(self.shader_program, self.fs)
        glLinkProgram(self.shader_program)
        log = glGetProgramInfoLog(self.shader_program)
        if log:
            print "Shader program error:", log
        self.is_initialized = True;


# NewSphereArray depends on existence of SharedBufferObjects before it
class NewSphereArray(QObject):
    def __init__(self, shared_buffers):
        self.shared_buffers = shared_buffers
        self.radius_scale = 1.0
        self.radius_offset = 0.0
        self.vertex_count = 4 # number of sides on imposter backdrop
        atoms = shared_buffers.atoms
        self.index_array = numpy.array(
                [atom.index for atom in atoms], 
                numpy.uint32)
        self.shader = NewSphereShader()
        self.index_buffer = 0
        self.is_initialized = False
        
    def init_gl(self):
        if self.is_initialized:
            return
        # self.shader.init_gl()
        glPushClientAttrib(GL_CLIENT_VERTEX_ARRAY_BIT)
        self.shared_buffers.init_gl()
        self.index_buffer = glGenBuffers(1)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.index_buffer)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, self.index_array, GL_STATIC_DRAW)        
        glPopClientAttrib()
        self.is_initialized = True
        
    def paint_gl(self, camera=None, renderer=None):
        self.shader.radius_offset = self.radius_offset
        self.shader.radius_scale = self.radius_scale
        self.shader.imposter_edge_count = self.vertex_count
        with self.shader:
            if not self.is_initialized:
                self.init_gl()
            glPushClientAttrib(GL_CLIENT_VERTEX_ARRAY_BIT)
            self.shared_buffers.paint_gl()
            glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.index_buffer)
            glDrawElements(GL_POINTS, len(self.index_array), GL_UNSIGNED_INT, None)            
            glPopClientAttrib()
        
    def update_atom_colors(self):
        self.shared_buffers.update_atom_colors()


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
   
