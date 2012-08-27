#version 150

#define TRACE_RAY
#define CORRECT_DEPTH
#define USE_HALOS

uniform mat4 projectionMatrix;

in vec4 gl_FragCoord;
in vec4 gl_Color;
in float imposterRadiusSquared;
in vec2 positionInImposter;
in vec3 positionInCamera;
in float qe_half_b;
in float qe_c;

out vec4 gl_FragColor;
#ifdef CORRECT_DEPTH
out float gl_FragDepth;
#endif

void main()
{
    // Restrict pixels to lie within circular sphere sillhouette
    float relRadSqr = dot(positionInImposter, positionInImposter) 
            / imposterRadiusSquared;
    if (relRadSqr > 1.00) {
        discard;
        // gl_FragColor = vec4(0,0,1,1); // for debugging
        // return;
    }
        
    vec4 color = gl_Color;
    
#ifdef TRACE_RAY
    float qe_half_a = dot(positionInCamera, positionInCamera);
    float determinant = qe_half_b*qe_half_b - qe_half_a*qe_c;
    if (determinant < 0.0) {
        discard;
        // gl_FragColor = vec4(0,0,1,1); // for debugging
        // return;
    }
    // first intersection is visible surface
    float alpha1 = (-qe_half_b - sqrt(determinant))/qe_half_a; // front of sphere
    vec3 surfaceInCamera = alpha1 * positionInCamera;

#ifdef CORRECT_DEPTH
    vec4 surfaceInClip = projectionMatrix * vec4(surfaceInCamera, 1);
    gl_FragDepth = surfaceInClip.z / surfaceInClip.w;
#endif // CORRECT_DEPTH

#endif // TRACE_RAY

  
#ifdef USE_HALOS
    // TODO - antialias inner edge of rim
    if (relRadSqr > 0.95 * 0.95) // dark rims
        color = vec4(0,0,0,1);
#endif

    gl_FragColor = color;
}
