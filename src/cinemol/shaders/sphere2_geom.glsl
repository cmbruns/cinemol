#version 150
#extension GL_ARB_geometry_shader4 : enable

inout float radius;
layout (triangles) in;

void main()
{
    gl_Position = gl_PositionIn[0];
    EmitVertex();
    gl_Position = gl_PositionIn[1];
    EmitVertex();
    gl_Position = gl_PositionIn[2];
    EmitVertex();
    // gl_Position = gl_PositionIn[0] + vec4(1,0,0,0);
    // EmitVertex();
    // gl_Position = gl_PositionIn[0] + vec4(0,1,0,0);
    // EndPrimitive();
}
