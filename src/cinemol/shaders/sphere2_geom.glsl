#version 120
#extension GL_ARB_geometry_shader4 : enable

varying float radius;

void main()
{
    gl_Position = gl_PositionIn[0];
    EmitVertex();
    gl_Position = gl_PositionIn[0] + vec4(1,0,0,0);
    EmitVertex();
    gl_Position = gl_PositionIn[0] + vec4(0,1,0,0);
    EndPrimitive();
}
