/*
 * SPDX-License-Identifier: MIT
 * vkprim: a BRender primitive library whose triangles Vulkan rasterises
 * (docs/adr/0002-vulkan-backend.md, stage B).
 *
 * It wraps softprim. softrend still transforms, lights, clips and projects,
 * and softprim still chooses the block for each primitive state and sets the
 * component ranges, so both libraries are handed the same screen-space
 * vertices. vkprim replaces the block's render function for untextured
 * triangles into an RGB_888 buffer with a 16-bit depth buffer: it collects
 * them and draws them with Vulkan when the renderer flushes, into the same
 * colour and depth buffers. Everything else (textured triangles, lines,
 * points) is still drawn by softprim.
 */
#ifndef VKPRIM_H
#define VKPRIM_H

#include <stddef.h>
#include "brender.h"

struct br_primitive_library;

/* Start Vulkan for width x height buffers; the device name is written to
 * device_name. 0 on success. */
int VkPrimBegin(br_uint_32 width, br_uint_32 height, char *device_name, size_t name_len);

/* A primitive library to pass to BrRendererBegin in place of softprim's. */
struct br_primitive_library *VkPrimWrap(struct br_primitive_library *softprim);

/* The colour (RGB_888) and depth (DEPTH_16) buffers the scene renders into. */
void VkPrimTarget(br_pixelmap *colour, br_pixelmap *depth);

/* Triangles drawn by Vulkan and passed on to softprim since VkPrimBegin. */
void VkPrimCounts(unsigned long *vulkan, unsigned long *software);

void VkPrimEnd(void);

#endif
