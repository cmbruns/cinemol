
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

