from actor import Actor
from OpenGL.GL import *
import cinemol.cinemol_globals as cinemol_globals
import os


class ShaderProgram:
    "Base class for shader programs."
    def __init__(self):
        self.is_initialized = False
        self.previous_program = 0
        self.shader_program = 0
        self.vertex_shader = """
void main()
{
    // pass through shader
    gl_FrontColor = gl_Color;
    gl_TexCoord[0] = gl_MultiTexCoord0;
    gl_Position = gl_ModelViewProjectionMatrix * gl_Vertex;
}       
"""
        self.fragment_shader = """
void main()
{
    // pass through shader
    gl_FragColor = gl_Color;
}
"""

    def init_gl(self):
        if self.is_initialized:
            return
        # print "creating shaders"
        self.vs = glCreateShader(GL_VERTEX_SHADER)
        self.fs = glCreateShader(GL_FRAGMENT_SHADER)
        glShaderSource(self.vs, self.vertex_shader)
        glShaderSource(self.fs, self.fragment_shader)
        glCompileShader(self.vs)
        log = glGetShaderInfoLog(self.vs)
        if log:
            print "Vertex Shader:", log
        glCompileShader(self.fs)
        log = glGetShaderInfoLog(self.fs)
        if log:
            print "Fragment Shader:", log
        if self.shader_program == 0:
            self.shader_program = glCreateProgram()
        glAttachShader(self.shader_program, self.vs)
        glAttachShader(self.shader_program, self.fs)
        glLinkProgram(self.shader_program)
        self.is_initialized = True

    def __enter__(self):
        self.previous_program = glGetIntegerv(GL_CURRENT_PROGRAM)
        try:
            glUseProgram(self.shader_program)
        except OpenGL.error.GLError:
            print glGetProgramInfoLog(self.shader_program)
            raise
        return self
        
    def __exit__(self, type, value, tb):
        glUseProgram(self.previous_program)


class GreenShaderProgram(ShaderProgram):
    def __init__(self):
        ShaderProgram.__init__(self)
        self.fragment_shader = """
void main()
{
    gl_FragColor = vec4(0, 0.8, 0, 1);
}
"""


class Shader150:
    def __init__(self):
        self.is_initialized = False
        self.shader_program = 0
        self.previous_program = 0
        # Indices for shared vertex attributes
        # TODO - centralize these indices
        self.position_attrib = 0
        self.color_attrib = 1
        self.radius_attrib = 2

    def __enter__(self):
        if not self.is_initialized:
            self.init_gl()
        self.previous_program = glGetIntegerv(GL_CURRENT_PROGRAM)
        glUseProgram(self.shader_program)
        glUniformMatrix4fv(
                glGetUniformLocation(self.shader_program, "modelViewMatrix"),
                1, False, glGetDoublev(GL_MODELVIEW_MATRIX).tolist())
        glUniformMatrix4fv(
                glGetUniformLocation(self.shader_program, "projectionMatrix"),
                1, False, glGetDoublev(GL_PROJECTION_MATRIX).tolist())
        glBindFragDataLocation(self.shader_program, 0, "fragColor");
        #
        return self

    def __exit__(self, type, value, tb):
        glDisableVertexAttribArray(self.position_attrib)
        glDisableVertexAttribArray(self.color_attrib)
        glDisableVertexAttribArray(self.radius_attrib)
        glUseProgram(self.previous_program)

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


class Sphere2Shader(Shader150):
    def __init__(self):
        Shader150.__init__(self)
        # Default values for uniforms
        self.light_direction = [1.0, 2.0, 1.0];
        self.radius_scale = 1.0
        self.radius_offset = 2.0

    def __enter__(self):
        Shader150.__enter__(self)
        glUniform1f(glGetUniformLocation(self.shader_program, "radiusScale"), 
                    self.radius_scale * cinemol_globals.atom_scale)
        glUniform1f(glGetUniformLocation(self.shader_program, "radiusOffset"), 
                    self.radius_offset)
        glUniform3fv(glGetUniformLocation(self.shader_program, "lightDirection"), 
                    1, self.light_direction)
        #
        return self
    
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
        glBindAttribLocation(shader_program, self.color_attrib, "atomColorLinear")
        glBindAttribLocation(shader_program, self.radius_attrib, "vdwRadius")
        glLinkProgram(shader_program)
        # print shader_program, vertex_shader, fragment_shader
        log = glGetProgramInfoLog(shader_program)
        if log:
            print "Shader program error:", log
        self.shader_program = shader_program
        self.is_initialized = True
    

class WireFrameShader(Shader150):
    def __init__(self):
        Shader150.__init__(self)
    
    def __enter__(self):
        Shader150.__enter__(self)
        return self
    
    def init_gl(self):
        if self.is_initialized:
            return
        vertex_shader = self.init_one_shader(
                "bondline_vrtx.glsl", GL_VERTEX_SHADER)
        geometry_shader = self.init_one_shader(
                "bondline_geom.glsl", GL_GEOMETRY_SHADER)
        fragment_shader = self.init_one_shader(
                "bondline_frag.glsl", GL_FRAGMENT_SHADER)
        shader_program = glCreateProgram()
        glAttachShader(shader_program, vertex_shader)
        glAttachShader(shader_program, geometry_shader)
        glAttachShader(shader_program, fragment_shader)
        glBindAttribLocation(shader_program, self.position_attrib, "atomPosition")
        glBindAttribLocation(shader_program, self.color_attrib, "atomColorLinear")
        glBindAttribLocation(shader_program, self.radius_attrib, "vdwRadius")
        glLinkProgram(shader_program)
        # print shader_program, vertex_shader, fragment_shader
        log = glGetProgramInfoLog(shader_program)
        if log:
            print "Shader program error:", log
        self.shader_program = shader_program
        self.is_initialized = True

