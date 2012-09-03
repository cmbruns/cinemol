from atom import Atom, AtomList
import color
from actor import Actor
from imposter import SphereImposterArray, CylinderImposterArray, atom_attributes, Sphere2Shader
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



class Sphere2TestScene(Actor):
    "Demonstrates side by side use of immediate mode and OpenGL 3.0 style"
    def __init__(self):
        self.shader = Sphere2Shader()
        self.atoms = AtomList()
        self.atoms.load_line(
                "ATOM      1  C   MOL     1      -1.597   0.768   6.992   inf   inf")
        self.atoms.load_line(
                "ATOM      2  N   MOL     1      -1.586  -0.581   6.688   inf   inf")
        self.atoms.load_line(
                "ATOM      3  C1  MOL     1      -2.832  -1.358   6.759   inf   inf")
        self.atoms.load_line(
                "ATOM      4  C2  MOL     1      -0.407  -1.203   6.316   inf   inf")
        for atom in self.atoms:
            atom.colorizer = color.ColorByRasmolCpk()
        #
        self.atom_attributes = atom_attributes
        #
        self.index_array = numpy.array(
                [ x for x in range(len(self.atoms)) ]
                , dtype='uint32')
        #
        self.is_initialized = False
        
    def init_gl(self):
        if self.is_initialized:
            return
        # Atom indices
        self.atom_index_buffer = glGenBuffers(1)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.atom_index_buffer)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, self.index_array, GL_STATIC_DRAW)
        #
        self.atom_attributes.init_gl()
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
        self.shader.radius_scale = 1.0
        self.shader.radius_offset = 0.0
        with self.shader:
            # Activate buffer objects
            self.atom_attributes.paint_gl()
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
        buffers = atom_attributes
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
