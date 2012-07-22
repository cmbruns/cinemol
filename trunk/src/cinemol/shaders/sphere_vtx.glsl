#version 120

// TODO should be uniform
varying mat4 cameraToClipMatrix;
uniform float zNear;
uniform float zFar;
uniform vec4 background_color;
uniform float eye_shift; // for asymmetric frustum stereo

varying vec3 position_in_eye;
varying vec3 sphere_center_in_eye;
varying float max_front_clip;
varying float radius;
varying float z_front; // positive distance from sphere center to front clip plane
const float near_clip_zone = 0.005;
const float max_radius = 2.0;

// quadratic equation parameters for sphere ray tracing equation
// ax^2 + bx + c = 0
// where x*(vertex-eye) is on the surface of the sphere
varying vec3 undot_qe_half_a; // must be dotted with itself to produce quadratic equation "a" term
varying float qe_half_b;
varying float qe_c;

void main()
{
    // We store a quad as 4 points with the same vertex, but different normals.
    // Reconstruct the quad by adding the normal to the vertex.
    radius = gl_Normal.z;
    vec4 sc = gl_ModelViewMatrix * gl_Vertex;
    vec3 sphere_center_in_camera = sc.xyz * 1.0/sc.w;

    // Parry front and rear clip planes
    vec3 frontmost_in_camera = sphere_center_in_camera + vec3(0, 0, radius);
    vec3 rearmost_in_camera = sphere_center_in_camera - vec3(0, 0, radius);
    cameraToClipMatrix = gl_ProjectionMatrix;
    max_front_clip = (cameraToClipMatrix * vec4(frontmost_in_camera, 1)).z;
    // Actual clip plane for spheres, including near_clip_zone
    vec4 near2_clip = gl_ProjectionMatrix * vec4(0, 0, -zNear, 1);
    near2_clip.z = near_clip_zone;
    float zNear2 = -(gl_ProjectionMatrixInverse * near2_clip).z;
    z_front = -sphere_center_in_camera.z - zNear;
    float max_rear_clip = (cameraToClipMatrix * vec4(rearmost_in_camera, 1)).z;
    // translate imposter plane to optimize clipped appearance

    float relative_quad_position = radius; // default to billboard behind sphere, for best front clipping
    if ((max_rear_clip > 1.0) && (max_front_clip > 0.0))
        relative_quad_position = -radius; // move to front for nice simple rear clipping
    else if (max_rear_clip < 0.0) ; // vertex and sphere should fail front clip
    else if (max_front_clip > 1.0) ; // vertex and sphere should fail rear clip
    else if ((max_rear_clip > 1.0) && (max_front_clip < 0.0))
        // double clip! choose an intermediate distance for the quad
        relative_quad_position = 0.5*(zNear + zFar) + sphere_center_in_camera.z ; // move to front for nice simple rear clipping

    vec3 eye_position_in_camera = vec3(-eye_shift, 0, 0); // compensate for parallax asymmetric frustum shift for stereo 3D
    // vec3 eye_position_in_camera = vec3(0, 0, 0); // compensate for parallax asymmetric frustum shift for stereo 3D
    sphere_center_in_eye = sphere_center_in_camera - eye_position_in_camera;
    vec3 eye_direction = normalize(-sphere_center_in_eye);
    // push quad back to the far back of the sphere, to avoid near clipping
    vec3 quad_center_in_camera = sphere_center_in_camera - relative_quad_position * eye_direction;
    // orient quad perpendicular to camera direction (this rotates normal by about 90 degrees, but that's OK)
    float circumradius_length = length(vec2(gl_Normal.xy));
    vec3 corner_offset = normalize(cross(vec3(gl_Normal.xy,0), eye_direction));
    
    // scale the corner distance
    //  a) - by sqrt(2) because it's a corner: sqrt(1*1 + 1*1)
    //  b) - by radius because that's how big the sphere is
    //  c) - by (d+r)/d because of recessed quad position, 
    //  d) - by d/sqrt(d^2-r^2) for bulge of horizon tangent
    //  e) - by 1.05 because it's too small toward the edge of the screen for some reason
    float r = radius;
    float d2 = dot(sphere_center_in_eye, sphere_center_in_eye);
    float d = sqrt(d2);
    float tangent_distance_squared = d2 - radius*radius;
    float corner_scale = 1.05 * circumradius_length * r*(d+relative_quad_position)/sqrt(tangent_distance_squared);
    corner_offset = corner_scale * corner_offset;
    // Keep the quad oriented toward the camera by not rotating corner_offset.
    vec3 position_in_camera = quad_center_in_camera + corner_offset;
    gl_Position = gl_ProjectionMatrix * vec4(position_in_camera, 1); // in clip
    
    // Put quantities in eye_frame not camera frame for fragment shader use.
    // This only matters in asymmetric frustum stereo 3D
    position_in_eye = position_in_camera - eye_position_in_camera;
    undot_qe_half_a = position_in_eye;
    qe_half_b = -1.0 * dot(position_in_eye, sphere_center_in_eye);
    qe_c = dot(sphere_center_in_eye, sphere_center_in_eye) - radius*radius;

    gl_FrontColor = gl_Color;
}
