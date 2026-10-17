#version 450
// SPDX-License-Identifier: MIT
layout(location = 0) flat in vec3 vcol;
layout(location = 0) out vec4 colour;

void main()
{
    colour = vec4(vcol, 1.0);
}
