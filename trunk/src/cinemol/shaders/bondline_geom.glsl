#version 150
#extension GL_ARB_geometry_shader4 : enable

uniform mat4 projectionMatrix;
uniform float lineWidth = 0.02;

layout (lines) in;
layout (triangle_strip, max_vertices = 16) out;

in vec4 atomColor[];

#pragma include "shared_functions.glsl"

out vec2 quadPosition;
out vec4 gl_Position;

void draw_half_bond_line(in vec3 atomPos, in vec3 midPos, in float lineWidth, in mat4 projectionMatrix)
{
    // local coordinate system for expanding to polygon
    vec3 x = normalize(midPos - atomPos); // along bond direction
    vec3 y = normalize(cross(midPos, x)); // width direction not along view axis
    vec3 z = normalize(cross(x, y));
    float bondLength = length(midPos - atomPos);
    
    // quadrilateral vertices
    vec3 q1 = midPos + 0.5 * lineWidth * y;
    vec3 q2 = q1 - lineWidth * y;
    vec3 q3 = q2 - bondLength * x;
    vec3 q4 = q3 + lineWidth * y;
    quadPosition = vec2(0.0, 0.0);
    gl_Position = projectionMatrix * vec4(q1, 1);
    EmitVertex();
    gl_Position = projectionMatrix * vec4(q2, 1);
    EmitVertex();
    gl_Position = projectionMatrix * vec4(q4, 1);
    EmitVertex();
    gl_Position = projectionMatrix * vec4(q3, 1);
    EmitVertex();
    EndPrimitive();
}

void draw_atom_circle(in vec3 atomPos, in float lineWidth, in mat4 projectionMatrix)
{
    float capLen = lineWidth/2.0; // rounded end cap

    // Send a second user-facing quad with a circle at the bond end
    quadPosition = vec2(1.0, 1.0);
    gl_Position = projectionMatrix * vec4(atomPos + capLen*vec3(quadPosition,0), 1);
    EmitVertex();
    quadPosition = vec2(-1.0, 1.0);
    gl_Position = projectionMatrix * vec4(atomPos + capLen*vec3(quadPosition,0), 1);
    EmitVertex();
    quadPosition = vec2(1.0, -1.0);
    gl_Position = projectionMatrix * vec4(atomPos + capLen*vec3(quadPosition,0), 1);
    EmitVertex();
    quadPosition = vec2(-1.0, -1.0);
    gl_Position = projectionMatrix * vec4(atomPos + capLen*vec3(quadPosition,0), 1);
    EmitVertex();
    EndPrimitive();
}

void draw_half_bond(in vec3 atomPos, in vec3 midPos, in float lineWidth, in mat4 projectionMatrix)
{
    draw_half_bond_line(atomPos, midPos, lineWidth, projectionMatrix);
    draw_atom_circle(atomPos, lineWidth, projectionMatrix);
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
    gl_FrontColor = atomColor[0];
    draw_half_bond(p1, middle, lineWidth, projectionMatrix);
    
    ///////////////////////////////////////////////
    //// Segment 2 of 2: middle to second atom ////
    ///////////////////////////////////////////////
    // Use color of first atom for bond segment
    gl_FrontColor = atomColor[1];    
    draw_half_bond(p2, middle, lineWidth, projectionMatrix);
}
