/*
 * SPDX-License-Identifier: MIT
 * A headless Vulkan rasteriser with a depth buffer, for vkprim
 * (docs/adr/0002-vulkan-backend.md, stage B). It draws into a copy of a
 * BRender RGB_888 colour buffer and 16-bit depth buffer and writes both back,
 * so the buffers BRender owns stay the frame.
 */
#ifndef VKZ_H
#define VKZ_H

#include <stddef.h>
#include <stdint.h>

/* x and y in pixels (Vulkan's pixel centres at i + 0.5), z from 0 (near)
 * to 1 (far), colour 0 to 1, interpolated linearly in screen space. */
typedef struct vkz_vertex {
    float x, y, z;
    float r, g, b;
} vkz_vertex;

typedef struct vkz_context vkz_context;

vkz_context *vkz_create(uint32_t width, uint32_t height, char *device_name, size_t name_len);

/* Upload the colour (B, G, R per pixel, colour_stride bytes a row) and depth
 * (uint16 per pixel, depth_stride bytes a row) buffers, draw count / 3
 * triangles with a less-than depth test, and write both buffers back. */
int vkz_draw(vkz_context *c, const vkz_vertex *v, uint32_t count, uint8_t *bgr, size_t colour_stride, uint8_t *depth,
             size_t depth_stride);

void vkz_destroy(vkz_context *c);

#endif
