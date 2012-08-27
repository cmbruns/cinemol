#version 150

uniform mat4 modelViewMatrix;
uniform float radius_scale;
uniform float radius_offset;

in vec3 vertexPosition;

out float radius;
out vec4 gl_Position;
out float horizonRatio; // d/sqrt(d^2-r^2) correction for perpective horizon

void main()
{
    gl_FrontColor = vec4(0.4, 0.1, 0 ,1);

    radius = 1.0 * radius_scale;

    // projection matrix is postponed to geometry shader
    gl_Position = modelViewMatrix * vec4(vertexPosition, 1.0);
    
    // horizon bulges larger than midline disk in perspective projection
    float cameraDistanceSqr = dot(gl_Position, gl_Position);
    horizonRatio = sqrt(cameraDistanceSqr / (cameraDistanceSqr - radius*radius));
}
