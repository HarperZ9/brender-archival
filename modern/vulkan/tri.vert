#version 450
// SPDX-License-Identifier: MIT
// Screen-space triangles: positions in pixels, y down, mapped to Vulkan's
// clip space (also y down). Flat colour per vertex.
layout(location = 0) in vec2 pos;
layout(location = 1) in vec3 col;
layout(push_constant) uniform Viewport { vec2 size; } vp;
layout(location = 0) flat out vec3 vcol;

void main()
{
    vcol = col;
    gl_Position = vec4(pos / vp.size * 2.0 - 1.0, 0.0, 1.0);
}
