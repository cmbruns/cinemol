#version 120

// TODO cameraToClipMatrix should be uniform
varying mat4 cameraToClipMatrix;
uniform vec4 background_color;
uniform float zNear;
varying float max_front_clip;
varying vec3 position_in_eye;
varying vec3 sphere_center_in_eye;
varying float radius;
varying float z_front; // distance from sphere center to front clip plane
const float near_clip_zone = 0.005;
const float max_radius = 4.0;

// quadratic equation parameters for sphere ray tracing equation
// ax^2 + bx + c = 0
// where x*(vertex-eye) is on the surface of the sphere
varying vec3 undot_qe_half_a; // must be dotted with itself to produce quadratic equation "a" term
varying float qe_half_b;
varying float qe_c;

void main()
{
    // Ray casting for actual surface point
    // Use quadratic equation - factor of 2 is elided
    // x = (-b +- sqrt(b^2 - 4ac)) / 2a // quadratic equation
    float qe_half_a = dot(undot_qe_half_a, undot_qe_half_a); // compute in frag shader because non linear
    float det = qe_half_b*qe_half_b - qe_half_a*qe_c; // (b^2-4ac) / 4.0
    if (det <= 0.0) {
        discard;  // No solution? means ray misses sphere
        // for debugging...
        // gl_FragColor = vec4(1,0,0,1);
        // return;
    }
    float alpha1 = (-qe_half_b - sqrt(det))/qe_half_a; // front of sphere
    vec3 surface_in_eye = alpha1 * position_in_eye.xyz;
    
    // cull by front and rear clip planes
    vec4 depth_vec = cameraToClipMatrix * vec4(surface_in_eye, 1);
    float depth = ((depth_vec.z / depth_vec.w) + 1.0) * 0.5;
    if (depth >= 1.0)
        discard; // front of sphere is behind back clip plane
        
    // If sphere is solid core, clip on back of sphere
    float alpha2 = (-qe_half_b + sqrt(det))/qe_half_a; // back of sphere
    vec3 back_surface_in_eye = alpha2 * position_in_eye;
    depth_vec = cameraToClipMatrix * vec4(back_surface_in_eye, 1);
    float depth2 = ((depth_vec.z / depth_vec.w) + 1.0) * 0.5;
    if (depth2 <= 0.0)
        discard; // back of sphere is in front of front clip plane
    
    vec3 surface_in_sphere = surface_in_eye - sphere_center_in_eye;
    vec3 normal_in_camera = normalize(surface_in_sphere);
    
    // Correct depth for Z buffer
    // Use a finite near slice of the frustum to handle solid-core clip overlaps,
    // so two intersecting near-clipped spheres are segregated more gracefully.
    if (depth <= near_clip_zone) { // front clip bisects this sphere, show solid core
        // clip to reveal a solid core
        // tiny offset so neighboring clipped spheres overlap correctly
        float m = radius * (-zNear - sphere_center_in_eye.z - 0.20) / surface_in_sphere.z;
        float rel_depth = 1.0 - (radius*radius - m*m) / max_radius;
        rel_depth = clamp(rel_depth, 0.0, 1.0);
        gl_FragDepth = 0.0 + near_clip_zone * rel_depth; // overlap
        normal_in_camera = vec3(0, 0, 1); // slice it flat against screen
    }
    else {
        gl_FragDepth = depth;
    }
    
    // Use Lambertian shading model
    // DIFFUSE
    // from http://www.davidcornette.com/glsl/glsl.html
    // TODO - distinguish sources at infinity from local sources
    vec3 s = -normalize(surface_in_eye - gl_LightSource[0].position.xyz);
    vec3 lightvec_in_camera = s;
    vec3 n = normalize(normal_in_camera);
    vec3 r = normalize(-reflect(lightvec_in_camera, n));
    vec3 v = normalize(-surface_in_eye.xyz);
    // vec4 diffuse = gl_FrontMaterial.diffuse * max(0.0, dot(n, s)) * gl_LightSource[0].diffuse;
    vec4 diffuse = gl_Color * max(0.0, dot(n, s)) * gl_LightSource[0].diffuse;
    // SPECULAR
    vec4 specular = vec4(0,0,0,0);
    if (gl_FrontMaterial.shininess != 0.0)
        specular = gl_LightSource[0].specular * 
            gl_FrontMaterial.specular * 
            // TODO - Seems I have to divide by 5 to get the same effect as fixed pipeline
            // Perhaps I am not properly handling light source at infinity...
            pow(max(0.0, dot(r, v)), 0.20 * gl_FrontMaterial.shininess);
    // AMBIENT
    vec4 ambient =  gl_LightSource[0].ambient * gl_FrontMaterial.ambient;
    // vec4 sceneColor = gl_FrontLightModelProduct.sceneColor;
    vec4 sceneColor = gl_FrontMaterial.emission + gl_Color * gl_LightModel.ambient;
    
    vec4 objectColor = sceneColor + ambient + diffuse + specular;

    // FOG
    float fog_start = 0.80;
    vec4 fogColor = background_color;
    float fog_ratio = 0.0;
    if (depth > fog_start)
        fog_ratio = (fog_start - depth) / (fog_start - 1.0);
    fog_ratio = clamp(fog_ratio, 0.0, 1.0);

    gl_FragColor = mix(objectColor, fogColor, fog_ratio);
}
