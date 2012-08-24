#version 120

uniform float radius_scale;
uniform float radius_offset;
uniform int imposter_edge_count;

varying vec3 sphere_center_in_eye;
varying float radius;

void main()
{
    radius = gl_Normal.z * radius_scale + radius_offset;
    vec4 sc = gl_ModelViewMatrix * gl_Vertex;
    vec3 sphere_center_in_eye = sc.xyz * 1.0/sc.w;
    gl_Position = gl_ProjectionMatrix * sc; // in clip
    gl_FrontColor = gl_Color;
}
