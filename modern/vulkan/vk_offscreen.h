/*
 * SPDX-License-Identifier: MIT
 * A headless Vulkan rasteriser for flat-coloured screen-space triangles, the
 * first stage of a Vulkan backend for BRender (docs/adr/0002-vulkan-backend.md).
 * No window and no surface: one offscreen colour image, drawn and read back.
 */
#ifndef VK_OFFSCREEN_H
#define VK_OFFSCREEN_H

#include <stdint.h>

/* One vertex: a position in pixels (x right, y down, as in a BRender
 * pixelmap with its origin at the top left) and a colour, 0 to 1. */
typedef struct vko_vertex {
    float x, y;
    float r, g, b;
} vko_vertex;

typedef struct vko_context vko_context;

/* Create a Vulkan instance and device and a width x height RGBA8 image.
 * The device is the first one found that can draw, unless VKO_DEVICE_TYPE
 * is "cpu", which asks for a CPU device (Mesa's lavapipe). The name of the
 * device used is written to device_name. NULL on failure, with a message on
 * stderr. */
vko_context *vko_create(uint32_t width, uint32_t height, char *device_name, size_t name_len);

/* Clear to (r, g, b), draw count / 3 triangles, wait, and copy the image
 * into rgb (width * height * 3 bytes, rows top to bottom, R G B). 0 on
 * success. */
int vko_draw(vko_context *c, const vko_vertex *vertices, uint32_t count, float r, float g, float b, uint8_t *rgb);

void vko_destroy(vko_context *c);

#endif
