#version 150

#pragma include "shared_functions.glsl"

uniform vec3 lightDirection = normalize(vec3(1,1,1));
uniform mat4 projectionMatrix;

in vec4 gl_Color;
in vec3 qe_undot_half_a;
in float qe_c;
in float qe_half_b;
in vec3 positionInCamera;
in vec3 cylCen;
in vec3 cylAxis;
in float maxCDistSqr; // points farther than this are not in segment

out vec4 fragColor;

void main()
{
    // discard points outside the cylinder by inspecting one term of the quadratic equation
    float qe_half_a = dot(qe_undot_half_a, qe_undot_half_a);
    float qeDeterminant = qe_half_b * qe_half_b - qe_half_a * qe_c;
    if (qeDeterminant <= 0.0) {
        discard;
        fragColor = vec4(1,1,0,1);
        return;
    }
    
    // ray trace point on cylinder surface
    float alpha1 = (-qe_half_b - sqrt(qeDeterminant)) / qe_half_a;
    vec3 surfaceInCamera = alpha1 * positionInCamera;
    vec3 dc = surfaceInCamera - cylCen;
    if (dot(dc, dc) > maxCDistSqr) { // beyond end of cylinder
        discard;
        fragColor = vec4(0,1,0,1);
        return;
    }
    
    vec3 normal = normalize(dc - dot(dc, cylAxis) * cylAxis);
    
    // Pass through color
    fragColor = gl_Color;
    
    fragColor = shadeLambertian(surfaceInCamera, normal, gl_Color, lightDirection);
    
    gl_FragDepth = fragDepthFromCameraPosition(surfaceInCamera, projectionMatrix);
}
