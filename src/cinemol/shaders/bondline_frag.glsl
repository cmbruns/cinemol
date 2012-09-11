#version 150

in vec4 gl_Color;
in vec2 quadPosition;

out vec4 fragColor;

void main()
{
    // Pass through color
    fragColor = gl_Color;
    float posX = quadPosition.x;
    if (posX <= 0.0)
        return; // not in end cap area
    // Round end cap at atom
    if (dot(quadPosition, quadPosition) > 1.0)
        discard; // rounded end cap
}
