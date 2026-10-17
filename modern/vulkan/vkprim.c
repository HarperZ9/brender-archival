/*
 * SPDX-License-Identifier: MIT
 * vkprim: the methods that differ from softprim. See vkprim.h.
 */
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "vkprim.h"
#include "vkprim_ip.h"
#include "vkz.h"

#define MAX_SLOTS 128

/* A copy of one of softprim's blocks with vkprim's render function in it.
 * The block comes first, so the block pointer softrend hands back is the slot. */
typedef struct slot {
    brp_block  block;
    brp_block *inner;
} slot;

static struct {
    vkz_context  *vk;
    br_pixelmap  *colour, *depth;
    vkz_vertex   *v;
    size_t        n, cap;
    unsigned long vulkan, software;
    float         offset_x, offset_y; /* subtracted from softprim's screen x and y; see VkPrimBegin */
    slot          slots[MAX_SLOTS];
    int           nslots;
} VP;

static float comp(const brp_block *b, brp_vertex *v0, brp_vertex *v, int c, br_uint_32 mask)
{
    return (b->constant_components & mask) ? v0->comp_f[c] : v->comp_f[c];
}

static float channel(float value)
{
    /* softprim writes the integer part of the colour component */
    float f = floorf(value);
    return (f < 0 ? 0 : (f > 255 ? 255 : f)) / 255.0f;
}

static void BR_ASM_CALL vkp_triangle(brp_block *block, brp_vertex *v0, brp_vertex *v1, brp_vertex *v2)
{
    brp_vertex *vs[3] = {v0, v1, v2};
    int k;
    if (VP.n + 3 > VP.cap) {
        size_t cap = VP.cap ? VP.cap * 2 : 3072;
        vkz_vertex *grown = realloc(VP.v, cap * sizeof(*grown));
        if (grown == NULL) return;
        VP.v = grown;
        VP.cap = cap;
    }
    for (k = 0; k < 3; k++) {
        vkz_vertex *o = &VP.v[VP.n++];
        o->x = comp(block, v0, vs[k], C_SX, CM_SX) - VP.offset_x;
        o->y = comp(block, v0, vs[k], C_SY, CM_SY) - VP.offset_y;
        o->z = (comp(block, v0, vs[k], C_SZ, CM_SZ) + 32768.0f) / 65535.0f;
        o->r = channel(comp(block, v0, vs[k], C_R, CM_R));
        o->g = channel(comp(block, v0, vs[k], C_G, CM_G));
        o->b = channel(comp(block, v0, vs[k], C_B, CM_B));
    }
    VP.vulkan++;
}

static void BR_ASM_CALL vkp_forward(brp_block *block, brp_vertex *v0, brp_vertex *v1, brp_vertex *v2)
{
    VP.software++;
    brp_render3(((slot *)block)->inner, v0, v1, v2);
}

/* Untextured, unblended triangles with RGB colour into an RGB_888 buffer
 * with 16-bit depth; the rest stays with softprim. */
static int takes(const brp_block *b)
{
    br_uint_32 c = b->constant_components | b->vertex_components;
    return VP.vk != NULL && VP.colour != NULL && VP.depth != NULL && VP.colour->type == BR_PMT_RGB_888
           && VP.depth->type == BR_PMT_DEPTH_16 && !(c & (CM_U | CM_V)) && (c & CM_R) && (c & CM_G) && (c & CM_B)
           && (c & CM_SZ) && !(b->flags & BR_PRIMF_BLENDED);
}

static slot *slot_for(brp_block *inner)
{
    int i;
    for (i = 0; i < VP.nslots && VP.slots[i].inner != inner; i++) {}
    if (i == VP.nslots) {
        if (VP.nslots == MAX_SLOTS) return NULL;
        VP.nslots++;
    }
    VP.slots[i].block = *inner;
    VP.slots[i].inner = inner;
    VP.slots[i].block.render = (brp_render_fn *)(takes(inner) ? vkp_triangle : vkp_forward);
    return &VP.slots[i];
}

br_error BR_CMETHOD_DECL(vkp_state, renderBegin)(struct br_primitive_state *self, brp_block **rpb, br_boolean *block_changed,
                                                br_boolean *ranges_changed, br_boolean no_render, br_token prim_type)
{
    brp_block *inner = NULL;
    br_error   r = ((vkp_pstate *)self)->inner->dispatch->_renderBegin(((vkp_pstate *)self)->inner, &inner, block_changed,
                                                                      ranges_changed, no_render, prim_type);
    slot *s;
    if (r == BRE_OK && inner != NULL && inner->render != NULL && prim_type == BRT_TRIANGLE && (s = slot_for(inner)) != NULL)
        inner = &s->block;
    *rpb = inner;
    return r;
}

br_error BR_CMETHOD_DECL(vkp_state, renderEnd)(struct br_primitive_state *self, brp_block *rpb)
{
    slot *s = (slot *)rpb;
    if (s >= VP.slots && s < VP.slots + VP.nslots)
        rpb = s->inner;
    return ((vkp_pstate *)self)->inner->dispatch->_renderEnd(((vkp_pstate *)self)->inner, rpb);
}

br_error BR_CMETHOD_DECL(vkp_state, stateCopy)(struct br_primitive_state *self, struct br_primitive_state *source, br_uint_32 mask)
{
    if (source != NULL && source->dispatch == (struct br_primitive_state_dispatch *)&vkp_state_dispatch)
        source = ((vkp_pstate *)source)->inner;
    return ((vkp_pstate *)self)->inner->dispatch->_stateCopy(((vkp_pstate *)self)->inner, source, mask);
}

br_error BR_CMETHOD_DECL(vkp_plib, stateNew)(struct br_primitive_library *self, struct br_primitive_state **rps)
{
    struct br_primitive_state *inner = NULL;
    vkp_pstate *w;
    br_error r = ((vkp_library *)self)->inner->dispatch->_stateNew(((vkp_library *)self)->inner, &inner);
    if (r != BRE_OK) return r;
    if ((w = BrResAllocate(NULL, sizeof(*w), BR_MEMORY_OBJECT)) == NULL) return BRE_NO_MEMORY;
    w->dispatch = (struct br_primitive_state_dispatch *)&vkp_state_dispatch;
    w->inner = inner;
    *rps = w;
    return BRE_OK;
}

br_error BR_CMETHOD_DECL(vkp_plib, flush)(struct br_primitive_library *self, br_boolean wait)
{
    br_error r = ((vkp_library *)self)->inner->dispatch->_flush(((vkp_library *)self)->inner, wait);
    if (VP.n > 0 && VP.vk != NULL)
        vkz_draw(VP.vk, VP.v, (uint32_t)VP.n, (uint8_t *)VP.colour->pixels, (size_t)VP.colour->row_bytes,
                 (uint8_t *)VP.depth->pixels, (size_t)VP.depth->row_bytes);
    VP.n = 0;
    return r;
}

int VkPrimBegin(br_uint_32 width, br_uint_32 height, char *device_name, size_t name_len)
{
    /* softprim's ranges add half a pixel to screen x and y (match.c,
     * updateRanges), and its scanline walker then truncates. Vulkan samples
     * pixel i at i + 0.5. Of the offsets measured on 17 October 2026 (x and y
     * each from -0.25 to 0.75), x 0.5 and y 0 came closest (mean coverage IoU
     * 0.9919 against 0.9865 for 0.5, 0.5); none reaches 1, because the two
     * fill rules differ at edges. VKPRIM_OFFSET="x,y" overrides it. */
    const char *o = getenv("VKPRIM_OFFSET");
    VP.offset_x = 0.5f;
    VP.offset_y = 0.0f;
    if (o != NULL && sscanf(o, "%f,%f", &VP.offset_x, &VP.offset_y) == 1)
        VP.offset_y = VP.offset_x;
    VP.vk = vkz_create(width, height, device_name, name_len);
    return VP.vk != NULL ? 0 : -1;
}

struct br_primitive_library *VkPrimWrap(struct br_primitive_library *softprim)
{
    vkp_library *w = BrResAllocate(NULL, sizeof(*w), BR_MEMORY_OBJECT);
    if (w == NULL) return NULL;
    w->dispatch = (struct br_primitive_library_dispatch *)&vkp_plib_dispatch;
    w->inner = softprim;
    return w;
}

void VkPrimTarget(br_pixelmap *colour, br_pixelmap *depth) { VP.colour = colour; VP.depth = depth; }

void VkPrimCounts(unsigned long *vulkan, unsigned long *software) { *vulkan = VP.vulkan; *software = VP.software; }

void VkPrimEnd(void)
{
    vkz_destroy(VP.vk);
    VP.vk = NULL;
    free(VP.v);
    VP.v = NULL;
    VP.n = VP.cap = 0;
}
