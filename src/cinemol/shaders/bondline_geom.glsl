#version 150
#extension GL_ARB_geometry_shader4 : enable

uniform mat4 projectionMatrix;

layout (lines) in;
layout (line_strip, max_vertices = 4) out;

void main()
{
    // Use color of first atom for bond segment
    gl_FrontColor = gl_FrontColorIn[0];
    // gl_FrontColor = vec4(1,0.5,0.5,1); // pink for testing
    gl_Position = projectionMatrix * gl_PositionIn[0];
    EmitVertex();
    // Only extend halfway to second atom
    // TODO - use a fancier ratio based on radius
    vec4 middle = 0.5 * (gl_PositionIn[0] + gl_PositionIn[1]);
    gl_Position = projectionMatrix * middle;
    EmitVertex();
    EndPrimitive();
    
    // Segment by second atom (assumes each bond appears only once)
    gl_FrontColor = gl_FrontColorIn[1];
    // gl_FrontColor = vec4(0.5,1.0,0.5,1); // green for testing
    gl_Position = projectionMatrix * middle;
    EmitVertex();
    gl_Position = projectionMatrix * gl_PositionIn[1]; 
    EmitVertex();
    EndPrimitive();
}
