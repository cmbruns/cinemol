#150

uniform mat4 modelViewMatrix;

in vec4 atomPosition;
in vec4 atomColorLinear;

void main()
{
    gl_FrontColor = atomColorLinear;
    
    // projection matrix is postponed to geometry shader
    gl_Position = modelViewMatrix * atomPosition;
}
