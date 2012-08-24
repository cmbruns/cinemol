#version 120

varying float radius;

void main()
{
    gl_FragColor = vec4(1, 0, 0, 1) * radius;
}
