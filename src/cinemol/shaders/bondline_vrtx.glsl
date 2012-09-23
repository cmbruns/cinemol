#version 150

uniform mat4 modelViewMatrix;

in vec4 atomPosition;
in vec4 atomColorLinear;

out vec4 atomColor;

void main()
{
    atomColor = atomColorLinear;
    
    // projection matrix is postponed to geometry shader
    gl_Position = modelViewMatrix * atomPosition;
}
