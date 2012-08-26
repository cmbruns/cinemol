#version 150

in vec3 vertexPosition;
uniform mat4 modelViewMatrix;
uniform mat4 projectionMatrix;
invariant gl_Position;

uniform float radius_scale;
uniform float radius_offset;
uniform int imposter_edge_count;

out vec3 sphere_center_in_eye;
out float radius;

void main()
{
    // radius = gl_Normal.z * radius_scale + radius_offset;
    radius = 1.0;
    vec4 sc = modelViewMatrix * vec4(vertexPosition, 1.0);
    vec3 sphere_center_in_eye = sc.xyz * 1.0/sc.w;
    gl_Position = projectionMatrix * sc; // in clip
    gl_FrontColor = vec4(1,0,0,1);
}
