#version 150
#extension GL_ARB_geometry_shader4 : enable

// Incoming point vertex is used as the center of a regular
// polygon, oriented toward the user.
// These shaders will paint a picture of a sphere on that polygon.

#define numSides 4

const float apothemRatio = cos(3.14159 / numSides); // polygon needs to be larger than circle it encloses
const float sideTheta = 2.0 * 3.14159 / float(numSides); // angle between polygon vertices
const float outlineWidthValue = 0.001;
const float outlineDepth = 1.5; 

uniform mat4 projectionMatrix;
uniform float eye_shift = 0.0; // for asymmetric frustum stereo

layout (points) in;
layout (triangle_strip, max_vertices = numSides) out;

in float radius[];

out vec2 positionInImposter;
out vec3 positionInEye;
out vec3 sphereCenterInEye;
out vec3 horizonPlanePosition; // for feathering outlines
out float outlineDepthRatio;

out float imposterRadius;
out float outlineWidth;

// Quadratic equation paramers for fragment shader ray tracing
out float qe_half_b;
out float qe_c;

void main()
{
    // pass through color
    gl_FrontColor = gl_FrontColorIn[0];
    
    outlineWidth = outlineWidthValue;
    
    vec3 sphereCenterInCamera = gl_PositionIn[0].xyz;
    // Asymmetric frustum stereo
    vec3 eyeInCamera = vec3(-eye_shift, 0, 0);
    sphereCenterInEye = sphereCenterInCamera - eyeInCamera;
    
    // horizon bulges larger than midline disk in perspective projection
    float cameraDistanceSqr = dot(sphereCenterInEye, sphereCenterInEye);
    // d/sqrt(d^2-r^2) correction for perpective horizon
    float horizonRatio = sqrt(cameraDistanceSqr / (cameraDistanceSqr - radius[0]*radius[0]));

    // Emit points from alternate halves of the polygon,
    // to keep the strip triangles in counterclockwise orientation.
    float theta = sideTheta/2.0; // angle of vertex in polar coordinates, align first side with x-axis
    float dTheta = 0.0; // magnitude of next vertex angle change
    float signDTheta = 1.0; // sign of next vertex angle change
    float atomRadius = radius[0];
    imposterRadius = horizonRatio * atomRadius; // perspective horizon bulge
    float circumradius = (imposterRadius + outlineWidth) / apothemRatio; // polygon corners stick out further

    // Local coordinate system of imposter polygon,
    // so we can orient the polygon toward the camera
    vec3 pZ = normalize(-sphereCenterInEye); // minus z axis along view vector
    vec3 pX = normalize(cross(vec3(0,1,0), pZ)); // x orthogonal to y/pZ plane
    vec3 pY = normalize(cross(pZ, pX)); // normalize not needed?
    for(int v = 0; v < numSides; ++v)  // one vertex at a time, starting at top middle
    {   
        theta += signDTheta * dTheta;
        float sinTheta = sin(theta);
        float cosTheta = cos(theta);
        positionInImposter = circumradius * vec2(cosTheta, -sinTheta);
        vec3 delta = pX * positionInImposter.x + pY * positionInImposter.y;
        vec3 positionInCamera = sphereCenterInCamera + delta;
        gl_Position = projectionMatrix * vec4(positionInCamera, 1);
        //
        positionInEye = positionInCamera - eyeInCamera;
        qe_half_b = -1.0 * dot(positionInEye, sphereCenterInEye);
        qe_c = dot(sphereCenterInEye, sphereCenterInEye) - atomRadius*atomRadius;

        // precompute parameters for outlines
        horizonPlanePosition = positionInCamera / horizonRatio;
        float cameraDistance = sqrt(cameraDistanceSqr);
        outlineDepthRatio = (cameraDistance + outlineDepth) / cameraDistance;

        EmitVertex();
        
        signDTheta *= -1.0;
        dTheta += sideTheta;
    }
    EndPrimitive();
}
