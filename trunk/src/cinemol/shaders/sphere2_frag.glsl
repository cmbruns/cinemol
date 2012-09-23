#version 150

// Paint a shaded sphere on an imposter polygon

// TODO: BLINN_PHONG, STEREO, FOG, SOLID_CORE

// Toggleable effects
#define LAMBERTIAN_SHADING // use 3d shading
#define CORRECT_DEPTH // put accurate values into z-buffer
// #define USE_OUTLINES // draw a dark outline around each atom

// ray tracing is required to get correct depth value
#ifdef CORRECT_DEPTH
#define TRACE_RAY
#endif
// ray tracing is required for Lambertian shading
#ifdef LAMBERTIAN_SHADING
#define TRACE_RAY
#endif

// pragma include is something I made up and parse specially
#pragma include "shared_functions.glsl"

const vec4 outlineColor = vec4(0,0,0,1); // black

uniform mat4 projectionMatrix;
uniform vec4 lightDirection = vec4(normalize(vec3(1,1,1)), 0);
uniform float outlineWidth = 0.001;

in vec4 gl_FragCoord;
in vec4 gl_Color;
in float imposterRadius;
in vec2 positionInImposter;
in vec3 positionInEye;
in vec3 sphereCenterInEye;
in float qe_half_b;
in float qe_c;
// outlines
in vec3 horizonPlanePosition;
in float outlineDepthRatio;


out vec4 fragColor;
#ifdef CORRECT_DEPTH
out float gl_FragDepth;
#endif


// Restrict pixels to lie within circular sphere sillhouette
float cullByRadius() 
{
    float radSqr = dot(positionInImposter, positionInImposter);
    float outerEdge = (imposterRadius + outlineWidth);
    outerEdge *= outerEdge;
    if (radSqr > outerEdge) {
        discard;
        // fragColor = vec4(0,0,1,1); // for debugging
        // return radSqr;
    }
    return radSqr;
}

// draw a dark outline around each atom,
// especially when atom is way in front of whatever is behind it.
bool drawOutline(in float radSqr)
{
    float innerEdge = imposterRadius * imposterRadius;
    if (radSqr < innerEdge)
        return false;
    // TODO - antialias inner edge of rim
#ifdef CORRECT_DEPTH
    float radius = sqrt(radSqr);
    vec3 dMin = horizonPlanePosition;
    float cullCheck = fragDepthFromCameraPosition(dMin, projectionMatrix);
    if (cullCheck < 0)
        discard;
    vec3 dMax = horizonPlanePosition * outlineDepthRatio;
    float edginess = clamp((radius - imposterRadius) / outlineWidth, 0, 1);
    vec3 featheredPosition = mix(dMin, dMax, edginess);
    gl_FragDepth = fragDepthFromCameraPosition(featheredPosition, projectionMatrix);
#endif // CORRECT_DEPTH
    fragColor = outlineColor;
    return true;
}


void main()
{
    // trim imposter polygon to a perfect circle
    float radSqr = cullByRadius();
        
#ifdef USE_OUTLINES
    // TODO - antialias inner edge of outlines
    if (drawOutline(radSqr))
        return;
#endif

#ifdef TRACE_RAY
    // Use quadratic formula to solve ray tracing equation
    float qe_a = dot(positionInEye, positionInEye);
    // (b^2 - 4ac) / 4.0
    float b2m4acd4 = qe_half_b*qe_half_b - qe_a*qe_c;
    if (b2m4acd4 < 0.0) { // outside of sphere
        // fragColor = vec4(0,0,1,1); // for debugging
        // return;
#ifdef USE_OUTLINES
        // rare pixels do fall between outline and sphere tests
        // TODO - antialias this case
        fragColor = outlineColor;
#ifdef CORRECT_DEPTH
        gl_FragDepth = fragDepthFromCameraPosition(horizonPlanePosition, projectionMatrix);
#endif // CORRECT_DEPTH
        return;
#else
        discard;
#endif
    }
    else {
	    // first intersection is visible surface
	    float alpha1 = (-qe_half_b - sqrt(b2m4acd4))/qe_a; // front of sphere
	    vec3 surfaceInEye = alpha1 * positionInEye;

#ifdef CORRECT_DEPTH
	    gl_FragDepth = fragDepthFromCameraPosition(surfaceInEye, projectionMatrix);
#endif // CORRECT_DEPTH

#ifdef LAMBERTIAN_SHADING
        vec3 normal = normalize(surfaceInEye - sphereCenterInEye);
        fragColor = shadeLambertian(surfaceInEye, normal, gl_Color, lightDirection);
#else
        fragColor = gl_Color;
#endif

    }
#endif // TRACE_RAY
  
}
