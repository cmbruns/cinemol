#version 150

// TODO: BLINN_PHONG, STEREO, SOLID_CORE

#define LAMBERTIAN_SHADING
#define CORRECT_DEPTH
// #define USE_OUTLINES

// ray tracing is required to get correct depth value
#ifdef CORRECT_DEPTH
#define TRACE_RAY
#endif
// ray tracing is required for Lambertian shading
#ifdef LAMBERTIAN_SHADING
#define TRACE_RAY
#endif

struct LightInfo {
    vec4 position;
    vec3 lA;
    vec3 lD;
    vec3 lS;
};
const LightInfo light = LightInfo(
    normalize(vec4(1.0, 2.0, 1.0, 0.0)),
    vec3(1,1,1),
    vec3(1,1,1),
    vec3(1,1,1));
    
struct MaterialInfo {
    vec3 kA;
    vec3 kD;
    vec3 kS;
    float shininess;
};

const vec4 outlineColor = vec4(0,0,0,1);

uniform mat4 projectionMatrix;

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

out vec4 gl_FragColor;
#ifdef CORRECT_DEPTH
out float gl_FragDepth;
#endif

void main()
{
    // Restrict pixels to lie within circular sphere sillhouette
    float radSqr = dot(positionInImposter, positionInImposter);
    float outerEdge = (imposterRadius + outlineWidth);
    outerEdge *= outerEdge;
    if (radSqr > outerEdge) {
        discard;
        // gl_FragColor = vec4(0,0,1,1); // for debugging
        // return;
    }
    float radius = sqrt(radSqr);
        
#ifdef USE_OUTLINES
    float innerEdge = imposterRadius * imposterRadius;
    // TODO - antialias inner edge of rim
    if (radSqr >= innerEdge) { // dark rims
#ifdef CORRECT_DEPTH
        vec3 dMin = horizonPlanePosition;
        vec3 dMax = horizonPlanePosition * outlineDepthRatio;
        float edginess = clamp((radius - imposterRadius) / outlineWidth, 0, 1);
        vec3 featheredPosition = mix(dMin, dMax, edginess);
        vec4 featheredInClip = projectionMatrix * vec4(featheredPosition, 1);
        gl_FragDepth = featheredInClip.z / featheredInClip.w;
#endif // CORRECT_DEPTH
        gl_FragColor = outlineColor;
        return;
    }
#endif

    vec4 color = gl_Color;
    gl_FragColor = color;
    
#ifdef TRACE_RAY
    float qe_half_a = dot(positionInCamera, positionInCamera);
    float determinant = qe_half_b*qe_half_b - qe_half_a*qe_c;
    if (determinant < 0.0) { // outside of sphere
        // gl_FragColor = vec4(0,0,1,1); // for debugging
        // return;
        // rare pixels fall between outline and sphere tests
#ifdef USE_OUTLINES
        gl_FragColor = outlineColor;
        return;
#else
        discard;
#endif
    }
    else {
	    // first intersection is visible surface
	    float alpha1 = (-qe_half_b - sqrt(determinant))/qe_half_a; // front of sphere
	    vec3 surfaceInCamera = alpha1 * positionInCamera;

#ifdef CORRECT_DEPTH
	    vec4 surfaceInClip = projectionMatrix * vec4(surfaceInCamera, 1);
	    gl_FragDepth = surfaceInClip.z / surfaceInClip.w;
#endif // CORRECT_DEPTH

#ifdef LAMBERTIAN_SHADING
        // TODO - take shading parameters from attributes
        // for now, hard code colors for testing
        MaterialInfo material = MaterialInfo(
            0.3 * color.rgb, 
            0.6 * color.rgb, 
            0.1 * vec3(1,1,1), 
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
        gl_FragColor = vec4(ambient + specular + diffuse, 1.0);
#endif
    }
#endif // TRACE_RAY
  
}
