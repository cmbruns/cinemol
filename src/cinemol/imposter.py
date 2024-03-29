
import cinemol_globals
from shader import ShaderProgram, Sphere2Shader
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


class AtomAttributeArray:
    "Lists of atom attributes that can be used as OpenGL array objects"
    def __init__(self, attribute_name, attribute_index, stride):
        self.attribute_name = attribute_name
        self.attribute_index = attribute_index
        self.stride = stride
        self._array = numpy.array([], dtype='float32')
        self._has_new_atoms = False # to trigger copy from python source
        self._values_changed = False # to trigger OpengGL array update
        self.is_initialized = False

    def clear(self):
        if len(self._array) > 0:
            self._array = numpy.array([], dtype='float32')
            self._has_new_atoms = True
            self._values_changed = True
        
    def init_gl(self):
        if self.is_initialized:
            return
        self.buffer = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.buffer)
        glBufferData(GL_ARRAY_BUFFER, self._array, GL_STATIC_DRAW)
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        self.is_initialized = True

    def paint_gl(self):
        if not self.is_initialized:
            self.init_gl()
        glBindBuffer(GL_ARRAY_BUFFER, self.buffer)
        if self._values_changed or self._has_new_atoms:
            glBufferData(GL_ARRAY_BUFFER, self._array, GL_STATIC_DRAW)
            self._values_changed = False
            self._has_new_atoms = False
        glEnableVertexAttribArray(self.attribute_index)
        glVertexAttribPointer(self.attribute_index, self.stride,
                GL_FLOAT, False, 0, None)
        
    def update_all_atoms(self, atoms):
        expected_size = self.stride * len(atoms)
        if len(self._array) != expected_size:
            self._array = numpy.zeros([expected_size,], dtype='float32')
            self._has_new_atoms = True
        index = 0
        for atom in atoms:
            vals = getattr(atom, self.attribute_name)
            if (self.stride == 1):
                vals = [vals,]
            for i in range(self.stride):
                value = vals[i]
                if self._array[index] != value:
                    self._values_changed = True
                    self._array[index] = value
                index += 1


class AtomGLAttributes:
    def __init__(self):
        self.atoms = None
        self.gl_arrays = list()
        self.gl_arrays.append(AtomAttributeArray("center", 0, 3))
        self.gl_arrays.append(AtomAttributeArray("color", 1, 3))
        self.gl_arrays.append(AtomAttributeArray("radius", 2, 1))
        self.is_initialized = False
        
    def add_atoms(self, atoms):
        if (self.atoms == None) or (len(self.atoms) == 0):
            self.set_atoms(atoms)
            return
        # TODO - combine
        self.set_atoms(atoms)
        
    def clear(self):
        for att in self.gl_arrays:
            att.clear()
        self.atoms = None
        
    def init_gl(self):
        if self.is_initialized:
            return
        for array in self.gl_arrays:
            array.init_gl()
        self.is_initialized = True
        
    def paint_gl(self):
        if not self.is_initialized:
            self.init_gl()
        for array in self.gl_arrays:
            array.paint_gl()
    
    def set_atoms(self, atoms):
        self.atoms = atoms
        for att in self.gl_arrays:
            att.update_all_atoms(atoms)
        
    def update_atom_colors(self):
        if self.atoms is None:
            return
        self.gl_arrays[1].update_all_atoms(self.atoms)


atom_attributes = AtomGLAttributes()





# Sphere2Array depends on existence of SharedBufferObjects before it
class Sphere2Array(QObject):
    def __init__(self, atom_attributes):
        self.atom_attributes = atom_attributes
        self.radius_scale = 1.0
        self.radius_offset = 0.0
        self.outline_pixel_width = 3.0
        atoms = atom_attributes.atoms
        na = 0
        if atoms is not None:
            na = len(atoms)
        self.index_array = numpy.array(
                [x for x in range(na)], 
                numpy.uint32)
        self.shader = Sphere2Shader()
        self.index_buffer = 0
        self.atoms_changed = False
        self.is_initialized = False
        
    def add_atoms(self, atoms):
        if len(atoms) < 1:
            return
        index_set = set(self.index_array)
        bChanged = False
        for atom in atoms:
            index = atom.index
            if not index in index_set:
                index_set.add(index)
                bChanged = True
        if bChanged:
            self.index_array = numpy.array(list(index_set), numpy.uint32)
            self.atoms_changed = True
        
    def clear(self):
        if len(self.index_array) > 0:
            self.index_array = numpy.array([], numpy.int32)
            self.atoms_changed = True
        
    def init_gl(self):
        if len(self.index_array) == 0:
            return
        if self.is_initialized:
            return
        self.atom_attributes.init_gl()
        self.index_buffer = glGenBuffers(1)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.index_buffer)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, self.index_array, GL_STATIC_DRAW)
        self.atoms_changed = False
        # clean up
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)
        self.is_initialized = True
        
    def paint_gl(self, camera=None, renderer=None):
        if len(self.index_array) == 0:
            return
        if not self.is_initialized:
            self.init_gl()
        self.shader.radius_offset = self.radius_offset
        self.shader.radius_scale = self.radius_scale
        self.shader.eye_shift = camera.eye_shift_in_ground
        self.shader.outline_width = self.outline_pixel_width * camera.glunits_per_pixel
        if renderer is not None:
            self.shader.light_direction = renderer.light_direction
        with self.shader:
            self.atom_attributes.paint_gl()
            glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.index_buffer)
            if self.atoms_changed:
                glBufferData(GL_ELEMENT_ARRAY_BUFFER, self.index_array, GL_STATIC_DRAW)
                self.atoms_changed = False
            glDrawElements(GL_POINTS, len(self.index_array), GL_UNSIGNED_INT, None)            
            # clean up
            glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)
            glBindBuffer(GL_ARRAY_BUFFER, 0)

    def remove_atoms(self, atoms):
        if len(atoms) < 1:
            return
        index_set = set(self.index_array)
        bChanged = False
        for atom in atoms:
            index = atom.index
            if index in index_set:
                index_set.remove(index)
                bChanged = True
        if bChanged:
            self.index_array = numpy.array(list(index_set), numpy.uint32)
            self.atoms_changed = True

    def update_atom_colors(self):
        self.atom_attributes.update_atom_colors()


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
   
