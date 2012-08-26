#version 150
#extension GL_ARB_geometry_shader4 : enable

// Incoming point vertex is used as the center of a regular
// polygon, oriented toward the user.

#define numSides 4

uniform mat4 projectionMatrix;
in float radius[];

layout (points) in;
layout (triangle_strip, max_vertices = numSides) out;

void main()
{
    gl_FrontColor = gl_FrontColorIn[0];

    // Emit points from alternate sides of the polygon,
    // to keep the strip triangles in counterclockwise orientation.
    const float sideTheta = 2.0 * 3.14159 / float(numSides); // angle between vertices
    float theta = sideTheta/2.0; // angle of vertex in polar coordinates
    float dTheta = 0.0; // magnitude of next vertex angle change
    float signDTheta = 1.0; // sign of next vertex angle change
    for(int v = 0; v < numSides; ++v)  // one vertex at a time, starting at top middle
    {   
        theta += signDTheta * dTheta;
        float sinTheta = sin(theta);
        float cosTheta = cos(theta);
        vec4 delta = radius[0] * vec4(cosTheta, -sinTheta, 0, 0);
        gl_Position = projectionMatrix * (gl_PositionIn[0] + delta);
        EmitVertex();
        signDTheta *= -1.0;
        dTheta += sideTheta;
    }
    EndPrimitive();
}
