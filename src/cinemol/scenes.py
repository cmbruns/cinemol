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


class QuadSceneShader:
    def __init__(self):
        self.is_initialized = False
        self.shader_program = 0
        self.previous_program = 0
        self.light_direction = [1.0, 2.0, 1.0];

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
        #
        position_handle = glGetAttribLocation(self.shader_program, "atomPosition");
        glEnableVertexAttribArray(position_handle)
        glVertexAttribPointer(position_handle,
                3, GL_FLOAT, False, 0, self.position_array)
        #
        color_handle = glGetAttribLocation(self.shader_program, "atomColorSrgb");
        glEnableVertexAttribArray(color_handle)
        glVertexAttribPointer(color_handle,
                3, GL_FLOAT, False, 0, self.color_array)
        #
        radius_handle = glGetAttribLocation(self.shader_program, "vdwRadius");
        glEnableVertexAttribArray(radius_handle)
        glVertexAttribPointer(radius_handle,
                1, GL_FLOAT, False, 0, self.radius_array)
        #
        glBindFragDataLocation(self.shader_program, 0, "fragColor");
        return self
    
    def __exit__(self, type, value, tb):
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


class AtomGlAttributes:
    def __init__(self, atoms):
        pass

class QuadScene(Actor):
    "Demonstrates side by side use of immediate mode and OpenGL 3.0 style"
    def __init__(self):
        self.shader = QuadSceneShader()
        self.position_array = numpy.array(
                [ 1,  1, 0,
                  1, -1, 0,
                  3,  1, 0,
                  3, -1 , 0]
                , dtype='float32')
        self.color_array = numpy.array(
                [ 0.6, 0.3, 0,
                  0.6, 0.3, 0,
                  0.8, 0.7, 0,
                  0.6, 0.3, 0]
                , dtype='float32')
        self.radius_array = numpy.array(
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
        self.atom_index_buffer = glGenBuffers(1)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.atom_index_buffer)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, self.index_array, GL_STATIC_DRAW)
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
        self.shader.position_array = self.position_array
        self.shader.color_array = self.color_array
        self.shader.radius_array = self.radius_array
        with self.shader:
            # glDrawArrays(GL_POINTS, 0, 4)
            glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.atom_index_buffer)
            glDrawElements(GL_POINTS, len(self.index_array), GL_UNSIGNED_INT, None)
    

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
