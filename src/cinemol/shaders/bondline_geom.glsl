#version 150
#extension GL_ARB_geometry_shader4 : enable

uniform mat4 projectionMatrix;
uniform float lineWidth = 0.02;

layout (lines) in;
layout (triangle_strip, max_vertices = 16) out;

#pragma include "shared_functions.glsl"

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
    draw_half_bond(p1, middle, lineWidth, projectionMatrix);
    
    ///////////////////////////////////////////////
    //// Segment 2 of 2: middle to second atom ////
    ///////////////////////////////////////////////
    // Use color of first atom for bond segment
    gl_FrontColor = gl_FrontColorIn[1];    
    draw_half_bond(p2, middle, lineWidth, projectionMatrix);
}
