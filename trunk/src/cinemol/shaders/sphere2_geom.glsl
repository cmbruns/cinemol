#version 150
#extension GL_ARB_geometry_shader4 : enable

const int numSides = 20;

inout float radius;
layout (points) in;
layout (triangle_strip, max_vertices = 20) out;

void main()
{
    gl_FrontColor = gl_FrontColorIn[0];
    // Grab points from alternate sides of the polygon
    // to keep the triangles in counterclockwise orientation.
    float theta = 0.0;
    for(int s = 0; s < numSides; ++s) {
        if (s % 2 == 1) { // s is odd
            theta = -theta - 2.0 * 3.14159 / float(numSides); 
        }
        else { // s is even
            theta = -theta;
        }
        float sv = sin(theta);
        float cv = cos(theta);
        vec4 delta = vec4(sv, cv, 0, 0);
        gl_Position = gl_PositionIn[0] + delta;
        EmitVertex();
    }
    EndPrimitive();
}
