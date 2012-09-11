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
uniform vec3 lightDirection;

in vec4 gl_FragCoord;
in vec4 gl_Color;
in float imposterRadius;
in float outlineWidth;
in vec2 positionInImposter;
in vec3 positionInCamera;
in vec3 sphereCenterInCamera;
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
        // return;
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
    vec3 dMax = horizonPlanePosition * outlineDepthRatio;
    float edginess = clamp((radius - imposterRadius) / outlineWidth, 0, 1);
    vec3 featheredPosition = mix(dMin, dMax, edginess);
    gl_FragDepth = fragDepthFromCameraPosition(featheredPosition, projectionMatrix);
#endif // CORRECT_DEPTH
    fragColor = outlineColor;
    return true;
}


vec4 shadeLambertian(in vec3 surfaceInCamera)
{
    LightInfo light = LightInfo(
	    vec4(normalize(lightDirection), 0.0),
	    vec3(1,1,1),
	    vec3(1,1,1),
	    vec3(1,1,1));
    
    // TODO - take shading parameters from attributes
    // for now, hard code colors for testing
    MaterialInfo material = MaterialInfo(
        0.2 * gl_Color.rgb, 
        0.6 * gl_Color.rgb, 
        0.2 * vec3(1,1,1), 
        25.0);
    vec3 s; // light vector
    if (light.position.w == 0.0) // light at infinity
        s = normalize(light.position.xyz);
    else
        s = normalize(vec3(light.position - vec4(surfaceInCamera, 1)));
    vec3 v = normalize(-surfaceInCamera); // view vector
    vec3 normal = normalize(surfaceInCamera - sphereCenterInCamera);
    vec3 r = reflect( -s, normal );
    vec3 ambient = light.lA * material.kA;
    float sDotN = max(dot(s, normal), 0.0);
    vec3 diffuse = light.lD * material.kD * sDotN;
    vec3 specular = vec3(0,0,0);
    if (sDotN > 0.0) {
        specular = light.lS * material.kS *
            pow(max(dot(r,v), 0.0), material.shininess);
    }
    return vec4(ambient + specular + diffuse, 1.0);
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
    float qe_a = dot(positionInCamera, positionInCamera);
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
	    vec3 surfaceInCamera = alpha1 * positionInCamera;

#ifdef CORRECT_DEPTH
	    gl_FragDepth = fragDepthFromCameraPosition(surfaceInCamera, projectionMatrix);
#endif // CORRECT_DEPTH

#ifdef LAMBERTIAN_SHADING
        fragColor = shadeLambertian(surfaceInCamera);
#else
        fragColor = gl_Color;
#endif

    }
#endif // TRACE_RAY
  
}
