from actor import Actor
from imposter import SphereImposterArray, CylinderImposterArray, NewSphereArray, SharedGLBufferObjects
from rotation import Vec3
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import numpy

class GlutSphereActor(Actor):
    def __init__(self, position=[0,0,0], radius=1.0):
        self.position = position[:]
        self.radius = radius
        
    def paint_gl(self):
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        p = self.position
        glTranslate(p[0], p[1], p[2])
        glutSolidSphere(self.radius, 20, 20)
        glPopMatrix()


class GlutCylinderActor(Actor):
    def __init__(self, position=[0,0,0], radius=1.0, height=2.0):
        self.position = position[:]
        self.radius = radius
        self.height = height

    def init_gl(self):
        self.quadric = gluNewQuadric()
        gluQuadricNormals(self.quadric, GLU_SMOOTH)
        gluQuadricTexture(self.quadric, GL_TRUE)
        
    def paint_gl(self):
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        p = self.position
        glTranslate(p[0], p[1], p[2] - self.height/2.0)
        gluCylinder(self.quadric, self.radius, self.radius, self.height, 20, 20)
        glPopMatrix()


class TeapotActor(Actor):
    def paint_gl(self):
        glPushAttrib(GL_POLYGON_BIT) # remember current GL_FRONT_FACE indictor
        glFrontFace(GL_CW) # teapot polygon vertex order is opposite to modern convention
        glColor3f(0.3, 0.3, 0.3) # paint it gray
        glutSolidTeapot(1.0) # thank you GLUT tool kit
        glPopAttrib() # restore GL_FRONT_FACE

################################
# Dev area for geometry shader approach

class Sphere2Shader:
    def __init__(self):
        self.is_initialized = False
        self.shader_program = 0
        self.previous_program = 0
        self.light_direction = [1.0, 2.0, 1.0];
        self.position_attrib = 0
        self.color_attrib = 1
        self.radius_attrib = 2

    def __enter__(self):
        self.previous_program = glGetIntegerv(GL_CURRENT_PROGRAM)
        if not self.is_initialized:
            self.init_gl()
        glUseProgram(self.shader_program)
        glUniformMatrix4fv(
                glGetUniformLocation(self.shader_program, "modelViewMatrix"),
                1, False, glGetDoublev(GL_MODELVIEW_MATRIX).tolist())
        glUniformMatrix4fv(
                glGetUniformLocation(self.shader_program, "projectionMatrix"),
                1, False, glGetDoublev(GL_PROJECTION_MATRIX).tolist())
        glUniform1f(glGetUniformLocation(self.shader_program, "radiusScale"), 
                    self.radius_scale)
        glUniform1f(glGetUniformLocation(self.shader_program, "radiusOffset"), 
                    self.radius_offset)
        glUniform3fv(glGetUniformLocation(self.shader_program, "lightDirection"), 
                    1, self.light_direction)
        glBindFragDataLocation(self.shader_program, 0, "fragColor");
        # Positions
        glBindBuffer(GL_ARRAY_BUFFER, self.position_buffer)
        glEnableVertexAttribArray(self.position_attrib)
        glVertexAttribPointer(self.position_attrib, 3,
                              GL_FLOAT, False, 0, None)
        # Colors
        glBindBuffer(GL_ARRAY_BUFFER, self.color_buffer)
        glEnableVertexAttribArray(self.color_attrib)
        glVertexAttribPointer(self.color_attrib, 3,
                              GL_FLOAT, False, 0, None)
        # Radii
        glBindBuffer(GL_ARRAY_BUFFER, self.radius_buffer)
        glEnableVertexAttribArray(self.radius_attrib)
        glVertexAttribPointer(self.radius_attrib, 1,
                              GL_FLOAT, False, 0, None)
        """
        if buffer_way:
            # TODO - colors atoms red
            # glBindVertexArray(self.color_array_handle)
            glBindBuffer(GL_ARRAY_BUFFER, self.color_buffer_handle)
            glVertexAttribPointer(self.color_attrib, 3,
                                  GL_FLOAT, False, 0, 0)
            glEnableVertexAttribArray(self.color_attrib)
            glBindBuffer(GL_ARRAY_BUFFER, 0)
            # glBindVertexArray(0)
        else:
            # Colors atoms correctly
            glEnableVertexAttribArray(self.color_attrib)
            glVertexAttribPointer(self.color_attrib,
                    3, GL_FLOAT, False, 0, self.color_array)
        #
        glEnableVertexAttribArray(self.radius_attrib)
        glVertexAttribPointer(self.radius_attrib,
                1, GL_FLOAT, False, 0, self.radii)
        """
        #
        return self
    
    def __exit__(self, type, value, tb):
        glDisableVertexAttribArray(self.position_attrib)
        glUseProgram(self.previous_program)

    def init_gl(self):
        if self.is_initialized:
            return
        vertex_shader = self.init_one_shader(
                "sphere2_vrtx.glsl", GL_VERTEX_SHADER)
        geometry_shader = self.init_one_shader(
                "sphere2_geom.glsl", GL_GEOMETRY_SHADER)
        fragment_shader = self.init_one_shader(
                "sphere2_frag.glsl", GL_FRAGMENT_SHADER)
        shader_program = glCreateProgram()
        glAttachShader(shader_program, vertex_shader)
        glAttachShader(shader_program, geometry_shader)
        glAttachShader(shader_program, fragment_shader)
        glBindAttribLocation(shader_program, self.position_attrib, "atomPosition")
        glBindAttribLocation(shader_program, self.color_attrib, "atomColorSrgb")
        glBindAttribLocation(shader_program, self.radius_attrib, "vdwRadius")
        glLinkProgram(shader_program)
        # print shader_program, vertex_shader, fragment_shader
        log = glGetProgramInfoLog(shader_program)
        if log:
            print "Shader program error:", log
        self.shader_program = shader_program
        self.is_initialized = True

    def init_one_shader(self, file_name, shader_type):
        this_dir = os.path.split(__file__)[0]
        shader_dir = os.path.join(this_dir, "shaders")
        # print os.path.join(shader_dir, file_name)
        shader_string = open(os.path.join(shader_dir, file_name)).read()
        shader = glCreateShader(shader_type)
        glShaderSource(shader, shader_string)
        glCompileShader(shader)
        log = glGetShaderInfoLog(shader)
        if log:
            print "Shader error:", log
        return shader


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

    def init_gl(self):
        if self.is_initialized:
            return
        self.array_handle = glGenVertexArrays(1)
        glBindVertexArray(self.array_handle)
        self.buffer_handle = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.buffer)
        glBufferData(GL_ARRAY_BUFFER, self._array, GL_STATIC_DRAW)
        glVertexAttribPointer(self.attribute_index, self.stride,
                    GL_FLOAT, False, 0, 0)
        glEnableVertexAttribArray(self.attribute_index)
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindVertexArray(0)
        self.is_initialized = True
        
    def paint_gl(self):
        use_buffers = False
        if use_buffers:
            glBindBuffer(GL_ARRAY_BUFFER, self.buffer)
            glVertexAttribPointer(self.attribute_index, self.stride,
                    GL_FLOAT, False, 0, 0)
            glEnableVertexAttribArray(self.attribute_index)
            glBindBuffer(GL_ARRAY_BUFFER, 0)
        else:
            glEnableVertexAttribArray(self.attribute_index)
            glVertexAttribPointer(self.attribute_index, self.stride,
                    GL_FLOAT, False, 0, self._array)
        
    def update_all_atoms(self, atoms):
        expected_size = self.stride() * len(atoms)
        if len(self._array) != expected_size:
            self._array = numpy.zeros([expected_size,], dtype='float32')
            self._has_new_atoms = True
        index = 0
        for atom in atoms:
            vals = atom.getattr(self.attribute_name)
            if (self.stride == 1):
                vals = [vals,]
            for i in range(self.stride):
                value = vals[i]
                if self[index] != value:
                    self._values_changed = True
                    self[index] = value
                index += 1


class Atoms2:
    def __init__(self, atoms):
        self._atoms = list()
        self.gl_arrays = list()
        self.gl_arrays.append(AtomAttributeArray("center", 3, len(self.gl_arrays)))
        self.gl_arrays.append(AtomAttributeArray("color", 3, len(self.gl_arrays)))
        self.gl_arrays.append(AtomAttributeArray("radius", 1, len(self.gl_arrays)))
        self.is_initialized = False
        
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
    

class Sphere2TestScene(Actor):
    "Demonstrates side by side use of immediate mode and OpenGL 3.0 style"
    def __init__(self):
        self.shader = Sphere2Shader()
        self.positions = numpy.array(
                [ 1,  1, 0,
                  1, -1, 0,
                  3,  1, 0,
                  3, -1 , 0]
                , dtype='float32')
        self.colors = numpy.array(
                [ 0.6, 0.3, 0,
                  0.6, 0.3, 0,
                  0.8, 0.7, 0,
                  0.6, 0.3, 0]
                , dtype='float32')
        self.radii = numpy.array(
                [ 1.0,
                  0.8,
                  1.0,
                  1.0]
                , dtype='float32')
        self.index_array = numpy.array(
                [ 0, 1, 2, 3 ]
                , dtype='uint32')
        self.is_initialized = False
        
    def init_gl(self):
        # Positions
        self.position_buffer = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.position_buffer)
        glBufferData(GL_ARRAY_BUFFER, self.positions, GL_STATIC_DRAW)
        # Colors
        self.color_buffer = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.color_buffer)
        glBufferData(GL_ARRAY_BUFFER, self.colors, GL_STATIC_DRAW)
        # Radii
        self.radius_buffer = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.radius_buffer)
        glBufferData(GL_ARRAY_BUFFER, self.radii, GL_STATIC_DRAW)
        # Atom indices
        self.atom_index_buffer = glGenBuffers(1)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.atom_index_buffer)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, self.index_array, GL_STATIC_DRAW)
        # 
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        self.is_initialized = True
    
    def paint_gl(self, camera=None, renderer=None):
        if not self.is_initialized:
            self.init_gl()
        # First square direct mode
        glColor3d(1,1,0)
        glBegin(GL_TRIANGLE_STRIP)
        glVertex3d(-3, 1, 0)
        glVertex3d(-3,-1, 0)
        glVertex3d(-1, 1, 0)
        glVertex3d(-1,-1, 0)
        glEnd()
        # second square uses shader
        """
        glBegin(GL_TRIANGLE_STRIP)
        glVertex3d( 1, 1, 0)
        glVertex3d( 1,-1, 0)
        glVertex3d( 3, 1, 0)
        glVertex3d( 3,-1, 0)
        glEnd()
        """
        # New way with 1.50
        self.shader.radius_scale = 1.2
        self.shader.radius_offset = 0.0
        self.shader.position_buffer = self.position_buffer
        self.shader.color_buffer = self.color_buffer
        self.shader.radius_buffer = self.radius_buffer
        with self.shader:
            # Use integer indices to access atom sphere data
            glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.atom_index_buffer)
            glDrawElements(GL_POINTS, len(self.index_array), GL_UNSIGNED_INT, None)
            # clean up
            glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)
            glBindBuffer(GL_ARRAY_BUFFER, 0)
    
##########################################

class FiveBallScene(Actor):
    def __init__(self):
        Actor.__init__(self)
        self.glut_sphere = GlutSphereActor()
        self.glut_cylinder = GlutCylinderActor()
        self.color = [0.15, 0.15, 0.80]
        sphere = Vec3([0,0,0])
        sphere.center = Vec3([0,0,0])
        sphere.radius = 1.0
        sphere.color = self.color
        sphere.index = 0
        # self.sphere_array = VertexArrayTest()
        self.sphere_array = SphereImposterArray([sphere,])
        buffers = SharedGLBufferObjects([sphere,])
        # self.sphere_array = NewSphereArray(buffers)
        cylinder = Vec3([0,0,0])
        cylinder.center = Vec3([0,0,0])
        cylinder.radius = 1.0
        cylinder.height = 2.0
        self.cylinder_array = CylinderImposterArray([cylinder,])
        
    def init_gl(self):
        self.sphere_array.init_gl()
        self.glut_cylinder.init_gl()
        self.cylinder_array.init_gl()
        
    def paint_gl(self, camera=None, renderer=None):
        c = self.color
        glColor3f(c[0], c[1], c[2]) # paint spheres blue
        glPushMatrix()
        glTranslate(-3.0, 0, 0)
        for p in range(5):
            # Leave a spot for shader sphere
            if 3 == p:
                self.sphere_array.paint_gl(camera, renderer)
            else:
                self.glut_sphere.paint_gl()
            glTranslate(1.5, 0, 0)
        glPopMatrix()
        glPushMatrix()
        glTranslate(-3.0, 2.0, 0)
        for p in range(5):
            # TODO Leave a spot for shader cylinder
            if 3 == p:
                self.cylinder_array.paint_gl()
            else:
                self.glut_cylinder.paint_gl()
            glTranslate(1.5, 0, 0)
        glPopMatrix()
        glPushMatrix()
        glTranslate(-3.0, 4.0, 0)
        for p in range(5):
            # TODO Leave a spot for shader cylinder
            self.glut_cylinder.paint_gl()
            glTranslate(1.5, 0, 0)
        glPopMatrix()
