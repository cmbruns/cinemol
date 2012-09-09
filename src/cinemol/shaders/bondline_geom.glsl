#version 150
#extension GL_ARB_geometry_shader4 : enable

uniform mat4 projectionMatrix;
uniform float lineWidth = 0.02;

layout (lines) in;
layout (triangle_strip, max_vertices = 8) out;

void draw_half_bond(in vec3 b1, in vec3 b2)
{
    // local coordinate system for expanding to polygon
    vec3 x = normalize(b2 - b1); // along bond direction
    vec3 y = normalize(cross(b2, x)); // width direction not along view axis
    vec3 z = normalize(cross(x, y));
    float bondLength = length(b2 - b1);
    
    // quadrilateral vertices
    vec3 q1 = b1 + 0.5 * lineWidth * y;
    vec3 q2 = q1 - lineWidth * y;
    vec3 q3 = q2 + bondLength * x;
    vec3 q4 = q3 + lineWidth * y;
    gl_Position = projectionMatrix * vec4(q1, 1);
    EmitVertex();
    gl_Position = projectionMatrix * vec4(q4, 1);
    EmitVertex();
    gl_Position = projectionMatrix * vec4(q2, 1);
    EmitVertex();
    gl_Position = projectionMatrix * vec4(q3, 1);
    EmitVertex();
    EndPrimitive();
}

void main()
{
    vec3 p1 = gl_PositionIn[0].xyz; // first atom
    vec3 p2 = gl_PositionIn[1].xyz; // second atom
    vec3 middle = 0.5 * (p1 + p2); // bond midpoint
    
    //////////////////////////////////////////////
    //// Segment 1 of 2: first atom to middle ////
    //////////////////////////////////////////////
    // Use color of first atom for bond segment
    gl_FrontColor = gl_FrontColorIn[0];
    draw_half_bond(p1, middle);
    
    ///////////////////////////////////////////////
    //// Segment 2 of 2: middle to second atom ////
    ///////////////////////////////////////////////
    // Use color of first atom for bond segment
    gl_FrontColor = gl_FrontColorIn[1];    
    draw_half_bond(p2, middle);
}
