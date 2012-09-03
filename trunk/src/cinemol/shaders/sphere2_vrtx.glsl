#version 150

uniform mat4 modelViewMatrix;
uniform float radiusScale;
uniform float radiusOffset;

in vec3 atomPosition;
in vec3 atomColorSrgb;
in float vdwRadius;

out float radius;
out vec4 gl_Position;

void main()
{
    vec3 atomColorLinear = pow(atomColorSrgb, vec3(2.2)); // approximately
    gl_FrontColor = vec4(atomColorLinear, 1);
    // gl_FrontColor = vec4(0.5, 0, 0.5, 1.0);
    
    radius = vdwRadius * radiusScale + radiusOffset;
    // radius = 1.0 * radiusScale + radiusOffset;
    
    // projection matrix is postponed to geometry shader
    gl_Position = modelViewMatrix * vec4(atomPosition, 1.0);
}
