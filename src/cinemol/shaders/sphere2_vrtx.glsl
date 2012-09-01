#version 150

uniform mat4 modelViewMatrix;
uniform float radius_scale;
uniform float radius_offset;

in vec3 vertexPosition;

out float radius;
out vec4 gl_Position;

void main()
{
    gl_FrontColor = vec4(0.4, 0.1, 0 ,1);

    radius = 1.0 * radius_scale + radius_offset;

    // projection matrix is postponed to geometry shader
    gl_Position = modelViewMatrix * vec4(vertexPosition, 1.0);
}
