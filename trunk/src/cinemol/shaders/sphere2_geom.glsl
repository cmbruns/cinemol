#version 150
#extension GL_ARB_geometry_shader4 : enable

// Incoming point vertex is used as the center of a regular
// polygon, oriented toward the user.
// These shaders will paint a picture of a sphere on that polygon.

#define numSides 4

const float apothemRatio = cos(3.14159 / numSides); // polygon needs to be larger than circle it encloses
const float sideTheta = 2.0 * 3.14159 / float(numSides); // angle between polygon vertices

uniform mat4 projectionMatrix;

layout (points) in;
layout (triangle_strip, max_vertices = numSides) out;

in float radius[];
in float horizonRatio[];

out vec2 positionInImposter;
out float imposterRadiusSquared;
out vec3 positionInCamera;
// Quadratic equation paramers for fragment shader ray tracing
out float qe_half_b;
out float qe_c;

void main()
{
    gl_FrontColor = gl_FrontColorIn[0];

    // Emit points from alternate halves of the polygon,
    // to keep the strip triangles in counterclockwise orientation.
    float theta = sideTheta/2.0; // angle of vertex in polar coordinates, align first side with x-axis
    float dTheta = 0.0; // magnitude of next vertex angle change
    float signDTheta = 1.0; // sign of next vertex angle change
    float atomRadius = radius[0];
    float imposterRadius = horizonRatio[0] * atomRadius; // perspective horizon bulge
    float circumradius = imposterRadius / apothemRatio; // polygon corners stick out further
    for(int v = 0; v < numSides; ++v)  // one vertex at a time, starting at top middle
    {   
        theta += signDTheta * dTheta;
        float sinTheta = sin(theta);
        float cosTheta = cos(theta);
        imposterRadiusSquared = imposterRadius * imposterRadius;
        positionInImposter = circumradius * vec2(cosTheta, -sinTheta);
        vec3 delta = vec3(positionInImposter, 0);
        vec3 sphereCenterInCamera = gl_PositionIn[0].xyz;
        positionInCamera = sphereCenterInCamera + delta;
        gl_Position = projectionMatrix * vec4(positionInCamera, 1);
        qe_half_b = -1.0 * dot(positionInCamera, sphereCenterInCamera);
        qe_c = dot(sphereCenterInCamera, sphereCenterInCamera) - atomRadius*atomRadius;

        EmitVertex();
        
        signDTheta *= -1.0;
        dTheta += sideTheta;
    }
    EndPrimitive();
}
