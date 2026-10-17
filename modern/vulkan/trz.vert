#version 450
// SPDX-License-Identifier: MIT
// vkprim: softrend's screen-space vertices. x and y in pixels, y down; z from
// 0 (near) to 1 (far). Colour is interpolated in screen space, as BRender's
// software rasteriser does.
layout(location = 0) in vec3 pos;
layout(location = 1) in vec3 col;
layout(push_constant) uniform Viewport { vec2 size; } vp;
layout(location = 0) noperspective out vec3 vcol;

void main()
{
    vcol = col;
    gl_Position = vec4(pos.xy / vp.size * 2.0 - 1.0, pos.z, 1.0);
}
