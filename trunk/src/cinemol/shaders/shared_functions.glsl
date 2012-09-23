
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

vec4 shadeLambertian(in vec3 positionInEye, in vec3 normalInEye, in vec4 color, in vec3 lightDirection)
{
    LightInfo light = LightInfo(
        vec4(normalize(lightDirection), 0.0),
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

out vec2 quadPosition;

void draw_half_bond_line(in vec3 atomPos, in vec3 midPos, in float lineWidth, in mat4 projectionMatrix)
{
    // local coordinate system for expanding to polygon
    vec3 x = normalize(midPos - atomPos); // along bond direction
    vec3 y = normalize(cross(midPos, x)); // width direction not along view axis
    vec3 z = normalize(cross(x, y));
    float bondLength = length(midPos - atomPos);
    
    // quadrilateral vertices
    vec3 q1 = midPos + 0.5 * lineWidth * y;
    vec3 q2 = q1 - lineWidth * y;
    vec3 q3 = q2 - bondLength * x;
    vec3 q4 = q3 + lineWidth * y;
    quadPosition = vec2(0.0, 0.0);
    gl_Position = projectionMatrix * vec4(q1, 1);
    EmitVertex();
    gl_Position = projectionMatrix * vec4(q2, 1);
    EmitVertex();
    gl_Position = projectionMatrix * vec4(q4, 1);
    EmitVertex();
    gl_Position = projectionMatrix * vec4(q3, 1);
    EmitVertex();
    EndPrimitive();
}

void draw_atom_circle(in vec3 atomPos, in float lineWidth, in mat4 projectionMatrix)
{
    float capLen = lineWidth/2.0; // rounded end cap

    // Send a second user-facing quad with a circle at the bond end
    quadPosition = vec2(1.0, 1.0);
    gl_Position = projectionMatrix * vec4(atomPos + capLen*vec3(quadPosition,0), 1);
    EmitVertex();
    quadPosition = vec2(-1.0, 1.0);
    gl_Position = projectionMatrix * vec4(atomPos + capLen*vec3(quadPosition,0), 1);
    EmitVertex();
    quadPosition = vec2(1.0, -1.0);
    gl_Position = projectionMatrix * vec4(atomPos + capLen*vec3(quadPosition,0), 1);
    EmitVertex();
    quadPosition = vec2(-1.0, -1.0);
    gl_Position = projectionMatrix * vec4(atomPos + capLen*vec3(quadPosition,0), 1);
    EmitVertex();
    EndPrimitive();
}

void draw_half_bond(in vec3 atomPos, in vec3 midPos, in float lineWidth, in mat4 projectionMatrix)
{
    draw_half_bond_line(atomPos, midPos, lineWidth, projectionMatrix);
    draw_atom_circle(atomPos, lineWidth, projectionMatrix);
}


