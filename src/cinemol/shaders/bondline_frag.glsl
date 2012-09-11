#version 150

in vec4 gl_Color;
in vec2 quadPosition;

out vec4 fragColor;

void main()
{
    // Pass through color
    fragColor = gl_Color;
    // Round end cap at atom
    if (dot(quadPosition, quadPosition) > 1.0)
        discard; // rounded end cap
}
