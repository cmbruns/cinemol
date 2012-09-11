#version 150

in vec4 gl_Color;
in vec2 quadPosition;

out vec4 fragColor;

void main()
{
    // Round end cap at atom
    if (quadPosition.x > 0.0) {
        if (dot(quadPosition, quadPosition) > 1.0)
            discard; // rounded end cap
    }
    // Pass through color
    fragColor = gl_Color;
}
