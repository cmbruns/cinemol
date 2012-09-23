#version 150
#extension GL_ARB_geometry_shader4 : enable

uniform mat4 projectionMatrix;
uniform float radius = 0.02;

layout (lines) in;
layout (triangle_strip, max_vertices = 24) out;

// Quadratic equation "a" component is non-linear, so we need to finish
// the computation in the fragment shader.  Hence "undot"
out vec3 qe_undot_half_a;
out float qe_c;
out float qe_half_b;
// 
out vec3 positionInCamera;
out vec3 cylCen;
out vec3 cylAxis;
out float maxCDistSqr; // points farther than this are not in segment

void sendVertex(vec3 pos, mat4 projectionMatrix, vec3 qe_undot_b_part) 
{
    positionInCamera = pos;
    qe_half_b = dot(positionInCamera, qe_undot_b_part);
    qe_undot_half_a = cross(positionInCamera, cylAxis);
    gl_Position = projectionMatrix * vec4(positionInCamera, 1);
    EmitVertex();
}

void draw_half_bond_cylinder(in vec3 atomPos, in vec3 midPos0, in float radius, in mat4 projectionMatrix)
{
    vec3 bondVec = midPos0 - atomPos;
    vec3 midPos = midPos0; // Ensure that the middle is fully covered
    float bondLengthSqr = dot(bondVec, bondVec);
    float bondLength = sqrt(bondLengthSqr);
    maxCDistSqr = 1.00 * (0.25 * bondLengthSqr + radius * radius);
    cylCen = 0.5 * (atomPos + midPos); // center of cylinder segment

    // local coordinate system for expanding to polygon
    vec3 x = normalize(bondVec); // along bond direction
    vec3 y = normalize(cross(vec3(0,0,-1), x)); // width direction not along view axis
    vec3 z = normalize(cross(x, y));

    // precompute quadratic equation terms to ease ray tracing in fragment shader
    cylAxis = x;
    vec3 cxa = cross(cylCen, cylAxis);
    qe_c = dot(cxa, cxa) - radius * radius;
    vec3 qe_undot_b_part = vec3(
        dot(cylCen, vec3(-x.y*x.y -x.z*x.z, x.x*x.y, x.x*x.z)),
        dot(cylCen, vec3( x.x*x.y, -x.x*x.x - x.z*x.z, x.y*x.z)),
        dot(cylCen, vec3( x.x*x.z,  x.y*x.z, -x.x*x.x - x.y*x.y)));
    
    // horizon bulges larger than midline disk in perspective projection
    float cameraDistanceSqr0 = dot(atomPos, atomPos);
    float cameraDistanceSqr1 = dot(midPos, midPos);
    float cameraDistanceSqr = min(cameraDistanceSqr0, cameraDistanceSqr1);
    // d/sqrt(d^2-r^2) correction for perpective horizon
    float horizonRatio = sqrt(cameraDistanceSqr / (cameraDistanceSqr - radius*radius));

    vec3 dx = 1.01 * 0.50 * bondVec; // Add a bit of extra canvas just in case
    vec3 dy = 1.01 * radius * y * horizonRatio;
    vec3 dz = 1.01 * radius * z;
    
    // axial quadrilateral
    sendVertex(cylCen + dx + dy, projectionMatrix, qe_undot_b_part);
    sendVertex(cylCen + dx - dy, projectionMatrix, qe_undot_b_part);
    sendVertex(cylCen - dx + dy, projectionMatrix, qe_undot_b_part);
    sendVertex(cylCen - dx - dy, projectionMatrix, qe_undot_b_part);
    EndPrimitive();
    
    // end cap 1 - at bond center
    sendVertex(cylCen + dx + dy + dz, projectionMatrix, qe_undot_b_part);
    sendVertex(cylCen + dx + dy - dz, projectionMatrix, qe_undot_b_part);
    sendVertex(cylCen + dx - dy + dz, projectionMatrix, qe_undot_b_part);
    sendVertex(cylCen + dx - dy - dz, projectionMatrix, qe_undot_b_part);
    EndPrimitive();

    // end cap 2 - at atom position
    sendVertex(cylCen - dx + dy + dz, projectionMatrix, qe_undot_b_part);
    sendVertex(cylCen - dx - dy + dz, projectionMatrix, qe_undot_b_part);
    sendVertex(cylCen - dx + dy - dz, projectionMatrix, qe_undot_b_part);
    sendVertex(cylCen - dx - dy - dz, projectionMatrix, qe_undot_b_part);
    EndPrimitive();
}

// #pragma include "shared_functions.glsl"

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
    draw_half_bond_cylinder(p1, middle, radius, projectionMatrix);
    
    ///////////////////////////////////////////////
    //// Segment 2 of 2: middle to second atom ////
    ///////////////////////////////////////////////
    // Use color of first atom for bond segment
    gl_FrontColor = gl_FrontColorIn[1];    
    draw_half_bond_cylinder(p2, middle, radius, projectionMatrix);
}
