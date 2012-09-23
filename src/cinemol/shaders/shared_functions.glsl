
struct LightInfo {
    vec4 position;
    vec3 lA;
    vec3 lD;
    vec3 lS;
};
    
struct MaterialInfo {
    vec3 kA;
    vec3 kD;
    vec3 kS;
    float shininess;
};

// http://gamedev.stackexchange.com/questions/16588/computing-gl-fragdepth
float fragDepthFromClipPosition(in vec4 positionInClip)
{
    float ndcDepth = positionInClip.z / positionInClip.w;
    return ((gl_DepthRange.diff * ndcDepth) +
        gl_DepthRange.near + gl_DepthRange.far) / 2.0;
}

float fragDepthFromCameraPosition(in vec3 positionInCamera, in mat4 projectionMatrix)
{
    vec4 positionInClip = projectionMatrix * vec4(positionInCamera, 1);
    return fragDepthFromClipPosition(positionInClip);
}

vec4 shadeLambertian(in vec3 positionInEye, in vec3 normalInEye, in vec4 color, in vec4 lightDirection)
{
    // TODO - non-infinity lights
    LightInfo light = LightInfo(
        vec4(normalize(lightDirection.xyz), 0.0),
        vec3(1,1,1),
        vec3(1,1,1),
        vec3(1,1,1));
    
    // TODO - take shading parameters from attributes
    // for now, hard code colors for testing
    MaterialInfo material = MaterialInfo(
        0.2 * color.rgb, 
        0.6 * color.rgb, 
        0.2 * vec3(1,1,1), 
        25.0);
    vec3 s; // light vector
    if (light.position.w == 0.0) // light at infinity
        s = normalize(light.position.xyz);
    else
        s = normalize(vec3(light.position - vec4(positionInEye, 1)));
    vec3 v = normalize(-positionInEye); // view vector
    // vec3 normal = normalize(surfaceInEye - sphereCenterInEye);
    vec3 r = reflect( -s, normalInEye );
    vec3 ambient = light.lA * material.kA;
    float sDotN = max(dot(s, normalInEye), 0.0);
    vec3 diffuse = light.lD * material.kD * sDotN;
    vec3 specular = vec3(0,0,0);
    if (sDotN > 0.0) {
        specular = light.lS * material.kS *
            pow(max(dot(r,v), 0.0), material.shininess);
    }
    return vec4(ambient + specular + diffuse, 1.0);
}
