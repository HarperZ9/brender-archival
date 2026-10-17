/*
 * SPDX-License-Identifier: MIT
 * One set of scenes, drawn by two BRender software rasterisers, for a
 * measured pixel comparison (docs/ROADMAP.md, item 5).
 *
 *   period: BRender 1.3.2 (Argonaut, 1998): softrend + pentprim, built 32-bit
 *           from the public source by the materialized harness
 *           (compile with PARITY_PERIOD=1; see period/CMakeLists.txt)
 *   modern: BRender 1.4 (BlazingRenderer): softrend + softprim, 64-bit
 *           (built by modern/CMakeLists.txt as parity-scene)
 *
 * Everything that is not the rasteriser is the same: the model, the camera,
 * the model transform, the material, the light and the 320 x 240 buffer
 * (RGB_888, INDEX_8, RGB_555 or RGB_565 by scene). The renderer setup differs only where the two versions' APIs
 * differ, and each side copies the setup of its own ladder rung, which is
 * known to render.
 *
 * Usage: parity-scene <dat-dir> <out-dir>
 * Writes <out-dir>/<scene>.ppm for every scene and one JSON line per scene.
 */
#include "brender.h"
#include "brddi.h"
#if !PARITY_PERIOD
#include "brsdl3dev.h"
#endif
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define W 320
#define H 240

/* BRender 1.3.2 and 1.4 turn degrees into angles differently. 1.3.2's
 * BR_ANGLE_DEG multiplies by 182 into a 16-bit integer (65536 units a turn,
 * so 182 is 0.024% short of 65536/360, and the product is truncated); 1.4's
 * angle is a float fraction of a turn. Left as it is, the difference moves every
 * period vertex by up to a few hundredths of a pixel. Both sides here use the
 * same angle: the nearest 16-bit unit, given to each version in its own form. */
#if PARITY_PERIOD
#define PARITY_ANGLE(deg) ((br_angle)(long)floor((deg) * 65536.0 / 360.0 + 0.5))
#else
#define PARITY_ANGLE(deg) ((br_angle)(floor((deg) * 65536.0 / 360.0 + 0.5) / 65536.0))
#endif

#if PARITY_PERIOD
void *BR_EXPORT BrDrv1SoftRendBegin(char *arguments);
void *BR_EXPORT BrDrv1PentPrimBegin(char *arguments);
br_error BR_PUBLIC_ENTRY BrV1dbRendererBegin(struct br_device_pixelmap *destination, struct br_renderer *renderer);
#define DEPTH_CLEAR 0xFFFFFFFF /* far: tt24_piz.asm draws where z < *zbuf */
#else
struct br_device *BR_EXPORT BrDrv1SoftPrimBegin(const char *arguments);
struct br_device *BR_EXPORT BrDrv1SoftRendBegin(const char *arguments);
#define DEPTH_CLEAR 0xFFFFFFFF
static char primitive_heap[1500 * 1024];
#endif

typedef struct scene {
    const char *name, *model;
    int         angle;   /* model turn about Y, degrees */
    br_uint_32  flags;   /* material flags */
    int         light;   /* add a directional light */
    const char *texture; /* a period .pix, or NULL: expanded to RGB_888 through std.pal,
                            except in the 8-bit scenes and the lit 24-bit textured ones,
                            which keep the 8-bit map and light it through a shade table */
    int         index8;  /* draw into an INDEX_8 buffer (the std.pal palette) */
    const char *shade;   /* shade table: "shade.tab" as is (8-bit), or expanded to RGB_888 */
    int         base, range; /* the material's palette ramp, for the untextured 8-bit scenes */
    int         tilt;    /* model turn about X, degrees; 0 means the usual 25 */
    int         hicolor; /* 555 or 565: draw into an RGB_555 or RGB_565 buffer, with
                            maps and shade tables packed into that format */
    int         pal;     /* keep the 8-bit map and attach std.pal to it */
    int         white;   /* a white material: no colour to modulate the map by */
    int         zs;      /* z-sorted (BrZsSceneRender, no depth buffer) instead of z-buffered */
    int         opacity; /* material opacity, 0 meaning 255; under 255 the material blends */
} scene;

/* Untextured scenes, then unlit textured ones (RGB_888 maps, the period
 * kernel TriangleRenderPIZ2TA24). The control scene repeats "torus-flat"
 * turned by another 25 degrees; compared with "torus-flat" it must not
 * match. */
static const scene scenes[] = {
    {"sphere-flat", "sph32.dat", 35, 0, 0, NULL},
    {"sphere-lit", "sph32.dat", 35, BR_MATF_LIGHT, 1, NULL},
    {"sphere-smooth", "sph32.dat", 35, BR_MATF_LIGHT | BR_MATF_SMOOTH, 1, NULL},
    {"torus-flat", "torus.dat", 60, 0, 0, NULL},
    {"torus-smooth", "torus.dat", 60, BR_MATF_LIGHT | BR_MATF_SMOOTH, 1, NULL},
    {"teapot-smooth", "teapot.dat", 20, BR_MATF_LIGHT | BR_MATF_SMOOTH, 1, NULL},
    {"sphere-textured", "sph32.dat", 35, 0, 0, "earth.pix"},
    {"sphere-textured-turned", "sph32.dat", 160, 0, 0, "earth.pix"},
    {"torus-textured", "torus.dat", 60, 0, 0, "rosewood.pix"},
    /* lit textured, 24-bit: the 8-bit map lit through shade.tab expanded to
     * RGB_888 (period kernel TrapezoidRenderPIZ2TIA_RGB_888) */
    {"sphere-textured-lit", "sph32.dat", 35, BR_MATF_LIGHT | BR_MATF_SMOOTH, 1, "earth.pix", 0, "shade.tab"},
    {"torus-textured-lit", "torus.dat", 60, BR_MATF_LIGHT | BR_MATF_SMOOTH, 1, "rosewood.pix", 0, "shade.tab"},
    /* 8-bit: the palette path, drawn into INDEX_8 through std.pal ramps and
     * shade.tab (period kernels in zb8.asm and fti8_piz.asm) */
    {"sphere-flat-index8", "sph32.dat", 35, 0, 0, NULL, 1, NULL, 176, 31},
    {"sphere-lit-index8", "sph32.dat", 35, BR_MATF_LIGHT, 1, NULL, 1, NULL, 160, 31},
    {"sphere-smooth-index8", "sph32.dat", 35, BR_MATF_LIGHT | BR_MATF_SMOOTH, 1, NULL, 1, NULL, 160, 31},
    {"torus-smooth-index8", "torus.dat", 60, BR_MATF_LIGHT | BR_MATF_SMOOTH, 1, NULL, 1, NULL, 128, 31},
    {"teapot-smooth-index8", "teapot.dat", 20, BR_MATF_LIGHT | BR_MATF_SMOOTH, 1, NULL, 1, NULL, 224, 31},
    {"sphere-textured-index8", "sph32.dat", 35, 0, 0, "earth.pix", 1, NULL},
    {"torus-textured-index8", "torus.dat", 60, 0, 0, "rosewood.pix", 1, NULL},
    {"sphere-textured-lit-index8", "sph32.dat", 35, BR_MATF_LIGHT | BR_MATF_SMOOTH, 1, "earth.pix", 1, "shade.tab"},
    {"torus-textured-lit-index8", "torus.dat", 60, BR_MATF_LIGHT | BR_MATF_SMOOTH, 1, "rosewood.pix", 1, "shade.tab"},
    /* 8-bit, perspective correct (BR_MATF_PERSPECTIVE): period kernels
     * TriangleRender_ZPT_I8_D16_256 and TriangleRender_ZPTI_I8_D16_256 in
     * fti8pizp.asm, set up by pfpsetup.asm. A triangle whose depth changes
     * little across it takes the setup's linear "cheat" path (the ZT and ZTI
     * kernels above), so a plane of eight large triangles ("plane", built
     * below), turned steeply about X so that it recedes, is where
     * perspective shows. */
    {"sphere-textured-persp-index8", "sph32.dat", 35, BR_MATF_PERSPECTIVE, 0, "earth.pix", 1, NULL},
    {"torus-textured-persp-index8", "torus.dat", 60, BR_MATF_PERSPECTIVE, 0, "rosewood.pix", 1, NULL},
    {"sphere-textured-lit-persp-index8", "sph32.dat", 35, BR_MATF_LIGHT | BR_MATF_SMOOTH | BR_MATF_PERSPECTIVE, 1, "earth.pix", 1, "shade.tab"},
    {"torus-textured-lit-persp-index8", "torus.dat", 60, BR_MATF_LIGHT | BR_MATF_SMOOTH | BR_MATF_PERSPECTIVE, 1, "rosewood.pix", 1, "shade.tab"},
    {"plane-textured-steep-linear-index8", "plane", 20, 0, 0, "earth.pix", 1, NULL, 0, 0, -60},
    {"plane-textured-steep-persp-index8", "plane", 20, BR_MATF_PERSPECTIVE, 0, "earth.pix", 1, NULL, 0, 0, -60},
    {"plane-textured-lit-steep-persp-index8", "plane", 20, BR_MATF_LIGHT | BR_MATF_SMOOTH | BR_MATF_PERSPECTIVE, 1, "earth.pix", 1, "shade.tab", 0, 0, -60},
    /* 15 and 16-bit: drawn into RGB_555 and RGB_565 buffers. Period kernels:
     * untextured, tt15_piz.asm and tt16_piz.asm (TriangleRenderPIZ2 flat,
     * PIZ2I Gouraud); a 256 x 256 map packed into the buffer's format,
     * zb16p2ul.asm (TriangleRender_ZT_RGB565_D16_256, which both tables
     * use); gold8.pix, 320 x 200 and so not a power of two, t_piza.asm's
     * TrapezoidRenderPIZ2TA15; and the 8-bit map lit through shade.tab
     * packed into the buffer's format, TrapezoidRenderPIZ2TIA_RGB_555. */
    {"sphere-flat-rgb555", "sph32.dat", 35, 0, 0, NULL, 0, NULL, 0, 0, 0, 555},
    {"sphere-lit-rgb555", "sph32.dat", 35, BR_MATF_LIGHT, 1, NULL, 0, NULL, 0, 0, 0, 555},
    {"sphere-smooth-rgb555", "sph32.dat", 35, BR_MATF_LIGHT | BR_MATF_SMOOTH, 1, NULL, 0, NULL, 0, 0, 0, 555},
    {"torus-flat-rgb555", "torus.dat", 60, 0, 0, NULL, 0, NULL, 0, 0, 0, 555},
    {"torus-smooth-rgb555", "torus.dat", 60, BR_MATF_LIGHT | BR_MATF_SMOOTH, 1, NULL, 0, NULL, 0, 0, 0, 555},
    {"sphere-textured-rgb555", "sph32.dat", 35, 0, 0, "earth.pix", 0, NULL, 0, 0, 0, 555},
    {"torus-textured-rgb555", "torus.dat", 60, 0, 0, "rosewood.pix", 0, NULL, 0, 0, 0, 555},
    {"sphere-textured-gold-rgb555", "sph32.dat", 35, 0, 0, "gold8.pix", 0, NULL, 0, 0, 0, 555},
    {"sphere-textured-lit-rgb555", "sph32.dat", 35, BR_MATF_LIGHT | BR_MATF_SMOOTH, 1, "earth.pix", 0, "shade.tab", 0, 0, 0, 555},
    {"torus-textured-lit-rgb555", "torus.dat", 60, BR_MATF_LIGHT | BR_MATF_SMOOTH, 1, "rosewood.pix", 0, "shade.tab", 0, 0, 0, 555},
    {"sphere-flat-rgb565", "sph32.dat", 35, 0, 0, NULL, 0, NULL, 0, 0, 0, 565},
    {"sphere-lit-rgb565", "sph32.dat", 35, BR_MATF_LIGHT, 1, NULL, 0, NULL, 0, 0, 0, 565},
    {"sphere-smooth-rgb565", "sph32.dat", 35, BR_MATF_LIGHT | BR_MATF_SMOOTH, 1, NULL, 0, NULL, 0, 0, 0, 565},
    {"torus-flat-rgb565", "torus.dat", 60, 0, 0, NULL, 0, NULL, 0, 0, 0, 565},
    {"torus-smooth-rgb565", "torus.dat", 60, BR_MATF_LIGHT | BR_MATF_SMOOTH, 1, NULL, 0, NULL, 0, 0, 0, 565},
    {"sphere-textured-rgb565", "sph32.dat", 35, 0, 0, "earth.pix", 0, NULL, 0, 0, 0, 565},
    {"torus-textured-rgb565", "torus.dat", 60, 0, 0, "rosewood.pix", 0, NULL, 0, 0, 0, 565},
    {"sphere-textured-gold-rgb565", "sph32.dat", 35, 0, 0, "gold8.pix", 0, NULL, 0, 0, 0, 565},
    {"sphere-textured-lit-rgb565", "sph32.dat", 35, BR_MATF_LIGHT | BR_MATF_SMOOTH, 1, "earth.pix", 0, "shade.tab", 0, 0, 0, 565},
    {"torus-textured-lit-rgb565", "torus.dat", 60, BR_MATF_LIGHT | BR_MATF_SMOOTH, 1, "rosewood.pix", 0, "shade.tab", 0, 0, 0, 565},
    /* 15 and 16-bit with an 8-bit map that carries the std.pal palette, the
     * only maps the 1998 MMX table textures (pentprim match.c:593 swaps it in
     * for the whole 15/16-bit table on a processor with MMX; BRender 1.4 does
     * the same). A white unlit material reaches RasteriseMMX5x5_Z_UV
     * (xzuv1.inc), a coloured one Z_UV_C (xzuvc.inc, the colour modulates the
     * map), a lit smooth one Z_UV_RGB (xzuvrgb.inc). BR_MATF_DITHER reaches
     * the _D kernels: Z_UV_D and, untextured, Z_RGB_D (xzrgb.inc). */
    {"sphere-textured-pal-rgb555", "sph32.dat", 35, 0, 0, "earth.pix", 0, NULL, 0, 0, 0, 555, 1, 1},
    {"torus-textured-pal-rgb555", "torus.dat", 60, 0, 0, "rosewood.pix", 0, NULL, 0, 0, 0, 555, 1, 1},
    {"sphere-textured-pal-tint-rgb555", "sph32.dat", 35, 0, 0, "earth.pix", 0, NULL, 0, 0, 0, 555, 1, 0},
    {"sphere-textured-pal-lit-rgb555", "sph32.dat", 35, BR_MATF_LIGHT | BR_MATF_SMOOTH, 1, "earth.pix", 0, NULL, 0, 0, 0, 555, 1, 0},
    {"torus-textured-pal-lit-rgb555", "torus.dat", 60, BR_MATF_LIGHT | BR_MATF_SMOOTH, 1, "rosewood.pix", 0, NULL, 0, 0, 0, 555, 1, 0},
    {"sphere-textured-pal-dither-rgb555", "sph32.dat", 35, BR_MATF_DITHER, 0, "earth.pix", 0, NULL, 0, 0, 0, 555, 1, 1},
    {"sphere-smooth-dither-rgb555", "sph32.dat", 35, BR_MATF_LIGHT | BR_MATF_SMOOTH | BR_MATF_DITHER, 1, NULL, 0, NULL, 0, 0, 0, 555},
    {"sphere-textured-pal-rgb565", "sph32.dat", 35, 0, 0, "earth.pix", 0, NULL, 0, 0, 0, 565, 1, 1},
    {"torus-textured-pal-rgb565", "torus.dat", 60, 0, 0, "rosewood.pix", 0, NULL, 0, 0, 0, 565, 1, 1},
    {"sphere-textured-pal-tint-rgb565", "sph32.dat", 35, 0, 0, "earth.pix", 0, NULL, 0, 0, 0, 565, 1, 0},
    {"sphere-textured-pal-lit-rgb565", "sph32.dat", 35, BR_MATF_LIGHT | BR_MATF_SMOOTH, 1, "earth.pix", 0, NULL, 0, 0, 0, 565, 1, 0},
    {"torus-textured-pal-lit-rgb565", "torus.dat", 60, BR_MATF_LIGHT | BR_MATF_SMOOTH, 1, "rosewood.pix", 0, NULL, 0, 0, 0, 565, 1, 0},
    {"sphere-textured-pal-dither-rgb565", "sph32.dat", 35, BR_MATF_DITHER, 0, "earth.pix", 0, NULL, 0, 0, 0, 565, 1, 1},
    {"sphere-smooth-dither-rgb565", "sph32.dat", 35, BR_MATF_LIGHT | BR_MATF_SMOOTH | BR_MATF_DITHER, 1, NULL, 0, NULL, 0, 0, 0, 565},
    /* Z-sorted (BrZsSceneRender, no depth buffer): the general tables'
     * z-sorted kernels, tt15_pi.asm, tt16_pi.asm and tt24_pi.asm (flat and
     * Gouraud) and t_pia.asm under awtm.c (maps). "tip": an 8-bit map lit
     * through a 15/16-bit shade table with BR_MATF_PERSPECTIVE, the general
     * tables' TIP256 perspective mappers (t15_pizp.asm z-buffered,
     * t15_pip.asm z-sorted), and with opacity 128 their blended TIPB256 forms.
     * "mmxp": an 8-bit map with std.pal and BR_MATF_PERSPECTIVE, which the
     * MMX table takes on its perspective rows (softrend subdivides). */
    {"sphere-flat-zs-rgb555", "sph32.dat", 35, 0, 0, NULL, 0, NULL, 0, 0, 0, 555, 0, 0, 1},
    {"sphere-smooth-zs-rgb555", "sph32.dat", 35, BR_MATF_LIGHT | BR_MATF_SMOOTH, 1, NULL, 0, NULL, 0, 0, 0, 555, 0, 0, 1},
    {"sphere-textured-zs-rgb555", "sph32.dat", 35, 0, 0, "earth.pix", 0, NULL, 0, 0, 0, 555, 0, 0, 1},
    {"sphere-textured-gold-zs-rgb555", "sph32.dat", 35, 0, 0, "gold8.pix", 0, NULL, 0, 0, 0, 555, 0, 0, 1},
    {"sphere-textured-lit-zs-rgb555", "sph32.dat", 35, BR_MATF_LIGHT | BR_MATF_SMOOTH, 1, "earth.pix", 0, "shade.tab", 0, 0, 0, 555, 0, 0, 1},
    {"sphere-tip-rgb555", "sph32.dat", 35, BR_MATF_LIGHT | BR_MATF_SMOOTH | BR_MATF_PERSPECTIVE, 1, "earth.pix", 0, "shade.tab", 0, 0, 0, 555},
    {"plane-tip-steep-rgb555", "plane", 20, BR_MATF_LIGHT | BR_MATF_SMOOTH | BR_MATF_PERSPECTIVE, 1, "earth.pix", 0, "shade.tab", 0, 0, -60, 555},
    {"sphere-tip-zs-rgb555", "sph32.dat", 35, BR_MATF_LIGHT | BR_MATF_SMOOTH | BR_MATF_PERSPECTIVE, 1, "earth.pix", 0, "shade.tab", 0, 0, 0, 555, 0, 0, 1},
    {"plane-tip-steep-zs-rgb555", "plane", 20, BR_MATF_LIGHT | BR_MATF_SMOOTH | BR_MATF_PERSPECTIVE, 1, "earth.pix", 0, "shade.tab", 0, 0, -60, 555, 0, 0, 1},
    {"sphere-tip-blend-rgb555", "sph32.dat", 35, BR_MATF_LIGHT | BR_MATF_SMOOTH | BR_MATF_PERSPECTIVE, 1, "earth.pix", 0, "shade.tab", 0, 0, 0, 555, 0, 0, 0, 128},
    {"sphere-tip-blend-zs-rgb555", "sph32.dat", 35, BR_MATF_LIGHT | BR_MATF_SMOOTH | BR_MATF_PERSPECTIVE, 1, "earth.pix", 0, "shade.tab", 0, 0, 0, 555, 0, 0, 1, 128},
    {"sphere-mmxp-rgb555", "sph32.dat", 35, BR_MATF_PERSPECTIVE, 0, "earth.pix", 0, NULL, 0, 0, 0, 555, 1, 1},
    {"plane-mmxp-steep-rgb555", "plane", 20, BR_MATF_PERSPECTIVE, 0, "earth.pix", 0, NULL, 0, 0, -60, 555, 1, 1},
    {"sphere-flat-zs-rgb565", "sph32.dat", 35, 0, 0, NULL, 0, NULL, 0, 0, 0, 565, 0, 0, 1},
    {"sphere-smooth-zs-rgb565", "sph32.dat", 35, BR_MATF_LIGHT | BR_MATF_SMOOTH, 1, NULL, 0, NULL, 0, 0, 0, 565, 0, 0, 1},
    {"sphere-textured-zs-rgb565", "sph32.dat", 35, 0, 0, "earth.pix", 0, NULL, 0, 0, 0, 565, 0, 0, 1},
    {"sphere-textured-gold-zs-rgb565", "sph32.dat", 35, 0, 0, "gold8.pix", 0, NULL, 0, 0, 0, 565, 0, 0, 1},
    {"sphere-textured-lit-zs-rgb565", "sph32.dat", 35, BR_MATF_LIGHT | BR_MATF_SMOOTH, 1, "earth.pix", 0, "shade.tab", 0, 0, 0, 565, 0, 0, 1},
    {"sphere-tip-rgb565", "sph32.dat", 35, BR_MATF_LIGHT | BR_MATF_SMOOTH | BR_MATF_PERSPECTIVE, 1, "earth.pix", 0, "shade.tab", 0, 0, 0, 565},
    {"plane-tip-steep-rgb565", "plane", 20, BR_MATF_LIGHT | BR_MATF_SMOOTH | BR_MATF_PERSPECTIVE, 1, "earth.pix", 0, "shade.tab", 0, 0, -60, 565},
    {"sphere-tip-zs-rgb565", "sph32.dat", 35, BR_MATF_LIGHT | BR_MATF_SMOOTH | BR_MATF_PERSPECTIVE, 1, "earth.pix", 0, "shade.tab", 0, 0, 0, 565, 0, 0, 1},
    {"plane-tip-steep-zs-rgb565", "plane", 20, BR_MATF_LIGHT | BR_MATF_SMOOTH | BR_MATF_PERSPECTIVE, 1, "earth.pix", 0, "shade.tab", 0, 0, -60, 565, 0, 0, 1},
    {"sphere-tip-blend-rgb565", "sph32.dat", 35, BR_MATF_LIGHT | BR_MATF_SMOOTH | BR_MATF_PERSPECTIVE, 1, "earth.pix", 0, "shade.tab", 0, 0, 0, 565, 0, 0, 0, 128},
    {"sphere-tip-blend-zs-rgb565", "sph32.dat", 35, BR_MATF_LIGHT | BR_MATF_SMOOTH | BR_MATF_PERSPECTIVE, 1, "earth.pix", 0, "shade.tab", 0, 0, 0, 565, 0, 0, 1, 128},
    {"sphere-mmxp-rgb565", "sph32.dat", 35, BR_MATF_PERSPECTIVE, 0, "earth.pix", 0, NULL, 0, 0, 0, 565, 1, 1},
    {"plane-mmxp-steep-rgb565", "plane", 20, BR_MATF_PERSPECTIVE, 0, "earth.pix", 0, NULL, 0, 0, -60, 565, 1, 1},
    {"sphere-flat-zs", "sph32.dat", 35, 0, 0, NULL, 0, NULL, 0, 0, 0, 0, 0, 0, 1},
    {"sphere-smooth-zs", "sph32.dat", 35, BR_MATF_LIGHT | BR_MATF_SMOOTH, 1, NULL, 0, NULL, 0, 0, 0, 0, 0, 0, 1},
    {"sphere-textured-zs", "sph32.dat", 35, 0, 0, "earth.pix", 0, NULL, 0, 0, 0, 0, 0, 0, 1},
    {"sphere-textured-lit-zs", "sph32.dat", 35, BR_MATF_LIGHT | BR_MATF_SMOOTH, 1, "earth.pix", 0, "shade.tab", 0, 0, 0, 0, 0, 0, 1},
    {"control-torus-turned", "torus.dat", 85, 0, 0, NULL},
};

/* A 15 or 16-bit pixel to 8 bits a channel, the same arithmetic on both
 * sides: each field moves to the top of its byte and its top bits repeat
 * below, so 0 stays 0 and a full field becomes 255. Gives R, G, B. */
static void expand16(unsigned v, int is565, unsigned char rgb[3])
{
    unsigned r = is565 ? (v >> 11) & 31 : (v >> 10) & 31;
    unsigned g = is565 ? (v >> 5) & 63 : (v >> 5) & 31;
    unsigned b = v & 31;
    rgb[0] = (unsigned char)(r << 3 | r >> 2);
    rgb[1] = (unsigned char)(is565 ? g << 2 | g >> 4 : g << 3 | g >> 2);
    rgb[2] = (unsigned char)(b << 3 | b >> 2);
}

/* A 24-bit colour (B, G, R bytes, as std.pal stores them) packed into a 15
 * or 16-bit pixel by dropping the low bits of each channel. */
static unsigned pack16(const unsigned char *bgr, int is565)
{
    if (is565) return (unsigned)(bgr[2] >> 3) << 11 | (unsigned)(bgr[1] >> 2) << 5 | (unsigned)(bgr[0] >> 3);
    return (unsigned)(bgr[2] >> 3) << 10 | (unsigned)(bgr[1] >> 3) << 5 | (unsigned)(bgr[0] >> 3);
}

static int is16(const br_pixelmap *pm) { return pm->type == BR_PMT_RGB_555 || pm->type == BR_PMT_RGB_565; }

/* An 8-bit buffer is written through the palette, so both sides' frames
 * compare in the same colours; the raw indices go to <scene>.pgm as well.
 * A 15 or 16-bit buffer goes through expand16. */
static int dump_ppm(const br_pixelmap *pm, const br_pixelmap *pal, const char *path)
{
    FILE *f = fopen(path, "wb");
    int x, y, index8 = pm->type == BR_PMT_INDEX_8;
    if (f == NULL || (index8 && pal == NULL)) {
        if (f) fclose(f);
        return 0;
    }
    fprintf(f, "P6\n%d %d\n255\n", (int)pm->width, (int)pm->height);
    for (y = 0; y < (int)pm->height; y++) {
        const unsigned char *row = (const unsigned char *)pm->pixels + (long)y * pm->row_bytes;
        for (x = 0; x < (int)pm->width; x++) {
            const unsigned char *bgr = index8 ? (const unsigned char *)pal->pixels + (long)row[x] * pal->row_bytes : row + x * 3;
            unsigned char rgb[3];
            if (is16(pm)) {
                expand16((unsigned)row[x * 2] | (unsigned)row[x * 2 + 1] << 8, pm->type == BR_PMT_RGB_565, rgb);
            } else {
                rgb[0] = bgr[2]; rgb[1] = bgr[1]; rgb[2] = bgr[0];
            }
            fwrite(rgb, 1, 3, f);
        }
    }
    fclose(f);
    if (index8) {
        char raw[1024];
        size_t n = strlen(path);
        snprintf(raw, sizeof(raw), "%.*s.pgm", (int)(n > 4 ? n - 4 : n), path);
        if ((f = fopen(raw, "wb")) == NULL) return 0;
        fprintf(f, "P5\n%d %d\n255\n", (int)pm->width, (int)pm->height);
        for (y = 0; y < (int)pm->height; y++)
            fwrite((const unsigned char *)pm->pixels + (long)y * pm->row_bytes, 1, (size_t)pm->width, f);
        fclose(f);
    }
    return 1;
}

static long count_lit(const br_pixelmap *pm)
{
    long total = 0;
    int x, y, bpp = pm->type == BR_PMT_INDEX_8 ? 1 : is16(pm) ? 2 : 3;
    for (y = 0; y < (int)pm->height; y++) {
        const unsigned char *row = (const unsigned char *)pm->pixels + (long)y * pm->row_bytes;
        for (x = 0; x < (int)pm->width; x++)
            total += bpp == 1 ? row[x] != 0
                   : bpp == 2 ? (row[x * 2] | row[x * 2 + 1]) != 0
                              : (row[x * 3] | row[x * 3 + 1] | row[x * 3 + 2]) != 0;
    }
    return total;
}

/* The 8-bit map as stored, registered under its own name. */
static br_pixelmap *load_texture8(const char *dat, const char *name)
{
    char path[1024];
    br_pixelmap *tex;
    snprintf(path, sizeof(path), "%s/%s", dat, name);
    if ((tex = BrPixelmapLoad(path)) == NULL || tex->type != BR_PMT_INDEX_8) return NULL;
    tex->identifier = (char *)name;
    BrMapAdd(tex);
    BrMapUpdate(tex, BR_MAPU_ALL);
    return tex;
}

/* The 8-bit map as stored, with std.pal attached as its palette (the
 * renderer takes a map's palette when it is RGBX_888, one pixel wide), then
 * registered. */
static br_pixelmap *load_texture8_pal(const char *dat, const char *name, br_pixelmap *pal)
{
    char path[1024];
    br_pixelmap *tex;
    snprintf(path, sizeof(path), "%s/%s", dat, name);
    if ((tex = BrPixelmapLoad(path)) == NULL || tex->type != BR_PMT_INDEX_8 || pal == NULL) return NULL;
    tex->map = pal;
    tex->identifier = (char *)name;
    BrMapAdd(tex);
    BrMapUpdate(tex, BR_MAPU_ALL);
    return tex;
}

/* shade.tab with each entry packed through std.pal into an RGB_555 or
 * RGB_565 table of the same shape (two bytes an entry), for a 15 or 16-bit
 * target. */
static br_pixelmap *load_shade16(const br_pixelmap *tab, const br_pixelmap *pal, int hicolor)
{
    int x, y, is565 = hicolor == 565;
    br_pixelmap *out = pal == NULL ? NULL
        : BrPixelmapAllocate(is565 ? BR_PMT_RGB_565 : BR_PMT_RGB_555, tab->width, tab->height, NULL, BR_PMAF_NORMAL);
    if (out == NULL) return NULL;
    for (y = 0; y < (int)tab->height; y++) {
        const unsigned char *src = (const unsigned char *)tab->pixels + (long)y * tab->row_bytes;
        unsigned char *dst = (unsigned char *)out->pixels + (long)y * out->row_bytes;
        for (x = 0; x < (int)tab->width; x++) {
            unsigned v = pack16((const unsigned char *)pal->pixels + (long)src[x] * pal->row_bytes, is565);
            dst[x * 2] = (unsigned char)(v & 0xff);
            dst[x * 2 + 1] = (unsigned char)(v >> 8);
        }
    }
    out->identifier = (char *)(is565 ? "shade-rgb565" : "shade-rgb555");
    BrTableAdd(out);
    BrTableUpdate(out, BR_TABU_ALL);
    return out;
}

/* shade.tab as stored (8-bit), or each entry expanded through std.pal into
 * an RGB_888 table of the same shape, for a 24-bit target, or into a 15 or
 * 16-bit one (hicolor). */
static br_pixelmap *load_shade(const char *dat, const char *name, const br_pixelmap *pal, int rgb, int hicolor)
{
    char path[1024];
    br_pixelmap *tab, *out;
    int x, y, stride4 = 0;
    snprintf(path, sizeof(path), "%s/%s", dat, name);
    if ((tab = BrPixelmapLoad(path)) == NULL || tab->type != BR_PMT_INDEX_8) return NULL;
    if (hicolor) return load_shade16(tab, pal, hicolor);
    out = tab;
    if (rgb) {
        /* The 1998 kernel for this table (TrapezoidRenderPIZ2TIA_RGB_888)
         * reads entry n at byte 4n of a table whose entries are 3 bytes, so
         * from the 48th row on it reads past the table. The table gets spare
         * zeroed rows below it, so that read stays in memory this program
         * owns and gives the same bytes every run; both sides see a table of
         * tab->height rows. */
        int rows = (tab->height * 4 + 2) / 3;
        if (pal == NULL || (out = BrPixelmapAllocate(BR_PMT_RGB_888, tab->width, rows, NULL, BR_PMAF_NORMAL)) == NULL)
            return NULL;
        memset(out->pixels, 0, (size_t)out->row_bytes * (size_t)rows);
        out->height = tab->height;
        /* PARITY_SHADE4=1 lays entry n at byte 4n instead, the stride the
         * 1998 kernel reads: an experiment for the period side only (see
         * README), which shows the stride is the whole difference. */
        stride4 = getenv("PARITY_SHADE4") != NULL;
        for (y = 0; y < (int)tab->height; y++) {
            const unsigned char *src = (const unsigned char *)tab->pixels + (long)y * tab->row_bytes;
            for (x = 0; x < (int)tab->width; x++) {
                const unsigned char *entry = (const unsigned char *)pal->pixels + (long)src[x] * pal->row_bytes;
                long at = stride4 ? ((long)y * tab->width + x) * 4 : (long)y * out->row_bytes + x * 3;
                unsigned char *dst = (unsigned char *)out->pixels + at;
                dst[0] = entry[0]; dst[1] = entry[1]; dst[2] = entry[2];
            }
        }
    }
    out->identifier = (char *)(rgb ? "shade-rgb" : name);
    BrTableAdd(out);
    BrTableUpdate(out, BR_TABU_ALL);
    return out;
}

/* Load a period texture and expand it through std.pal into RGB_888 (for
 * hicolor 555 or 565, pack it into RGB_555 or RGB_565), the same bytes on
 * both sides, then register it so the renderer stores it. */
static br_pixelmap *load_texture(const char *dat, const char *name, int hicolor)
{
    char path[1024];
    br_pixelmap *tex, *pal, *rgb;
    int x, y;
    snprintf(path, sizeof(path), "%s/%s", dat, name);
    if ((tex = BrPixelmapLoad(path)) == NULL) return NULL;
    snprintf(path, sizeof(path), "%s/std.pal", dat);
    pal = tex->map != NULL ? tex->map : BrPixelmapLoad(path);
    if (tex->type != BR_PMT_INDEX_8 || pal == NULL) return NULL;
    rgb = BrPixelmapAllocate(hicolor == 565 ? BR_PMT_RGB_565 : hicolor ? BR_PMT_RGB_555 : BR_PMT_RGB_888,
                             tex->width, tex->height, NULL, BR_PMAF_NORMAL);
    if (rgb == NULL) return NULL;
    for (y = 0; y < (int)tex->height; y++) {
        const unsigned char *src = (const unsigned char *)tex->pixels + (long)y * tex->row_bytes;
        unsigned char *dst = (unsigned char *)rgb->pixels + (long)y * rgb->row_bytes;
        for (x = 0; x < (int)tex->width; x++) {
            const unsigned char *entry = (const unsigned char *)pal->pixels + (long)src[x] * pal->row_bytes;
            if (hicolor) {
                unsigned v = pack16(entry, hicolor == 565);
                dst[x * 2] = (unsigned char)(v & 0xff);
                dst[x * 2 + 1] = (unsigned char)(v >> 8);
            } else {
                dst[x * 3 + 0] = entry[0]; dst[x * 3 + 1] = entry[1]; dst[x * 3 + 2] = entry[2];
            }
        }
    }
    rgb->identifier = (char *)name;
    BrMapAdd(rgb);
    BrMapUpdate(rgb, BR_MAPU_ALL);
    return rgb;
}

/* "plane": a square in the XY plane facing the camera, two by two quads
 * (eight triangles), its map coordinates running 0 to 2 so the map repeats
 * once each way. Built here, the same on both sides. */
static br_model *make_plane(void)
{
    const int n = 2;
    int x, y, f = 0;
    br_model *model = BrModelAllocate("plane", (n + 1) * (n + 1), 2 * n * n);
    if (model == NULL) return NULL;
    for (y = 0; y <= n; y++) {
        for (x = 0; x <= n; x++) {
            br_vertex *v = &model->vertices[y * (n + 1) + x];
            v->p.v[0] = BrFloatToScalar(2.0f * x / n - 1.0f);
            v->p.v[1] = BrFloatToScalar(2.0f * y / n - 1.0f);
            v->p.v[2] = 0;
            v->map.v[0] = BrFloatToScalar(2.0f * x / n);
            v->map.v[1] = BrFloatToScalar(2.0f * y / n);
        }
    }
    for (y = 0; y < n; y++) {
        for (x = 0; x < n; x++) {
            int a = y * (n + 1) + x, b = a + 1, c = a + n + 1, d = c + 1;
            model->faces[f].vertices[0] = (br_uint_16)a; model->faces[f].vertices[1] = (br_uint_16)b;
            model->faces[f].vertices[2] = (br_uint_16)d; f++;
            model->faces[f].vertices[0] = (br_uint_16)a; model->faces[f].vertices[1] = (br_uint_16)d;
            model->faces[f].vertices[2] = (br_uint_16)c; f++;
        }
    }
    return model;
}

/* Fit the model in a unit sphere at the origin, then turn it: the same
 * matrix arithmetic on both sides, in the same order. */
static void place_model(br_actor *actor, const br_model *model, int angle, int tilt)
{
    float c[3] = {0, 0, 0}, radius = 0, s;
    int k, nv = (int)model->nvertices;
    br_matrix34 scale;
    for (k = 0; k < nv; k++) {
        c[0] += BrScalarToFloat(model->vertices[k].p.v[0]);
        c[1] += BrScalarToFloat(model->vertices[k].p.v[1]);
        c[2] += BrScalarToFloat(model->vertices[k].p.v[2]);
    }
    c[0] /= nv; c[1] /= nv; c[2] /= nv;
    for (k = 0; k < nv; k++) {
        float dx = BrScalarToFloat(model->vertices[k].p.v[0]) - c[0];
        float dy = BrScalarToFloat(model->vertices[k].p.v[1]) - c[1];
        float dz = BrScalarToFloat(model->vertices[k].p.v[2]) - c[2];
        float r = (float)sqrt(dx * dx + dy * dy + dz * dz);
        if (r > radius) radius = r;
    }
    s = radius > 0 ? 1.0f / radius : 1.0f;
    actor->t.type = BR_TRANSFORM_MATRIX34;
    BrMatrix34Translate(&actor->t.t.mat, BrFloatToScalar(-c[0]), BrFloatToScalar(-c[1]), BrFloatToScalar(-c[2]));
    BrMatrix34Scale(&scale, BrFloatToScalar(s), BrFloatToScalar(s), BrFloatToScalar(s));
    BrMatrix34Post(&actor->t.t.mat, &scale);
    BrMatrix34PostRotateX(&actor->t.t.mat, PARITY_ANGLE(tilt ? tilt : 25));
    BrMatrix34PostRotateY(&actor->t.t.mat, PARITY_ANGLE(angle));
}

int main(int argc, char **argv)
{
    const char *dat = argc > 1 ? argv[1] : ".", *out = argc > 2 ? argv[2] : ".";
    br_pixelmap *colour, *depth, *colour8, *colour555, *colour565, *palette;
    br_actor *world, *camera_actor, *light_actor;
    br_camera *camera;
    int i, failed = 0;

    if (BrBegin() != BRE_OK) return 3;
#if PARITY_PERIOD
    /* the setup of the period renderer rung (brender-core-softrend-render.c) */
    if (BrDevAddStatic(NULL, (br_device_begin_fn *)BrDrv1SoftRendBegin, NULL) != BRE_OK) return 4;
    if (BrDevAddStatic(NULL, (br_device_begin_fn *)BrDrv1PentPrimBegin, NULL) != BRE_OK) return 4;
    {
        br_renderer_facility *facility = NULL;
        struct br_primitive_library *plib = NULL;
        void *heap = BrMemAllocate(512 * 1024, BR_MEMORY_APPLICATION);
        if (BrRendererFacilityFind(&facility, NULL, BRT_FLOAT) != BRE_OK || facility == NULL) return 5;
        if (BrV1dbRendererBegin(NULL, NULL) != BRE_OK) return 5;
        if (heap == NULL || BrPrimitiveLibraryFind(&plib, NULL, BR_SCALAR_TOKEN) != BRE_OK || plib == NULL) return 5;
        BrRendererBegin(NULL, NULL, plib, heap, 512 * 1024);
    }
    colour = BrPixelmapAllocate(BR_PMT_RGB_888, W, H, NULL, BR_PMAF_NORMAL);
    depth = BrPixelmapAllocate(BR_PMT_DEPTH_16, W, H, NULL, BR_PMAF_NORMAL);
    colour8 = BrPixelmapAllocate(BR_PMT_INDEX_8, W, H, NULL, BR_PMAF_NORMAL);
    colour555 = BrPixelmapAllocate(BR_PMT_RGB_555, W, H, NULL, BR_PMAF_NORMAL);
    colour565 = BrPixelmapAllocate(BR_PMT_RGB_565, W, H, NULL, BR_PMAF_NORMAL);
#else
    /* the setup of the 1.4 renderer rung (ladder64/softrend-render-14.c) */
    {
        br_pixelmap *screen = NULL;
        if (BrDevAddStatic(NULL, BrDrv1SoftPrimBegin, NULL) != BRE_OK) return 4;
        if (BrDevAddStatic(NULL, BrDrv1SoftRendBegin, NULL) != BRE_OK) return 4;
        if (BrDevAddStatic(NULL, BrDrv1SDL3Begin, NULL) != BRE_OK) return 4;
        if (BrDevBeginVar(&screen, "SDL3", BRT_WIDTH_I32, W, BRT_HEIGHT_I32, H, BR_NULL_TOKEN) != BRE_OK) return 5;
        colour = BrPixelmapMatchTyped(screen, BR_PMMATCH_OFFSCREEN, BR_PMT_RGB_888);
        depth = colour ? BrPixelmapMatch(colour, BR_PMMATCH_DEPTH_16) : NULL;
        colour8 = BrPixelmapMatchTyped(screen, BR_PMMATCH_OFFSCREEN, BR_PMT_INDEX_8);
        colour555 = BrPixelmapMatchTyped(screen, BR_PMMATCH_OFFSCREEN, BR_PMT_RGB_555);
        colour565 = BrPixelmapMatchTyped(screen, BR_PMMATCH_OFFSCREEN, BR_PMT_RGB_565);
        if (colour == NULL || depth == NULL) return 5;
        BrRendererBegin(colour, NULL, NULL, primitive_heap, sizeof(primitive_heap));
    }
#endif
    if (colour == NULL || depth == NULL || colour8 == NULL || colour555 == NULL || colour565 == NULL) return 5;
    colour->origin_x = depth->origin_x = colour8->origin_x = colour555->origin_x = colour565->origin_x = W / 2;
    colour->origin_y = depth->origin_y = colour8->origin_y = colour555->origin_y = colour565->origin_y = H / 2;
    {
        char path[1024];
        snprintf(path, sizeof(path), "%s/std.pal", dat);
        if ((palette = BrPixelmapLoad(path)) == NULL) return 6;
    }

    world = BrActorAllocate(BR_ACTOR_NONE, NULL);
    camera_actor = BrActorAdd(world, BrActorAllocate(BR_ACTOR_CAMERA, NULL));
    camera = (br_camera *)camera_actor->type_data;
    camera->type = BR_CAMERA_PERSPECTIVE_FOV;
    camera->field_of_view = PARITY_ANGLE(55);
    camera->hither_z = BrFloatToScalar(1.0f);
    camera->yon_z = BrFloatToScalar(100.0f);
    camera->aspect = BrFloatToScalar((float)W / (float)H);
    camera_actor->t.type = BR_TRANSFORM_MATRIX34;
    BrMatrix34Translate(&camera_actor->t.t.mat, 0, 0, BrFloatToScalar(2.5f));
    light_actor = BrActorAdd(world, BrActorAllocate(BR_ACTOR_LIGHT, NULL));
    light_actor->t.type = BR_TRANSFORM_MATRIX34;
    BrMatrix34RotateY(&light_actor->t.t.mat, PARITY_ANGLE(-30));
    BrMatrix34PostRotateX(&light_actor->t.t.mat, PARITY_ANGLE(-20));

    for (i = 0; i < (int)(sizeof(scenes) / sizeof(scenes[0])); i++) {
        const scene *sc = &scenes[i];
        char path[1024];
        br_model *model;
        br_material *material;
        br_actor *actor;
        long lit;
        snprintf(path, sizeof(path), "%s/%s", dat, sc->model);
        model = strcmp(sc->model, "plane") == 0 ? make_plane() : BrModelLoad(path);
        if (model == NULL || model->nvertices < 3) {
            printf("{\"scene\":\"%s\",\"error\":\"model %s did not load\"}\n", sc->name, sc->model);
            failed++;
            continue;
        }
        actor = BrActorAdd(world, BrActorAllocate(BR_ACTOR_MODEL, NULL));
        place_model(actor, model, sc->angle, sc->tilt); /* before BrModelUpdate, which may drop the vertex array */
        material = BrMaterialAllocate(sc->name);
        material->colour = BR_COLOUR_RGB(200, 170, 110);
        material->ka = BrFloatToScalar(0.15f);
        material->kd = BrFloatToScalar(0.85f);
        material->ks = BrFloatToScalar(0.0f);
        material->flags = sc->flags;
        if (sc->opacity) material->opacity = (br_uint_8)sc->opacity;
        material->index_base = (br_uint_8)sc->base;
        material->index_range = (br_uint_8)sc->range;
        if (sc->shade != NULL && (material->index_shade = load_shade(dat, sc->shade, palette, !sc->index8, sc->hicolor)) == NULL) {
            printf("{\"scene\":\"%s\",\"error\":\"shade table %s did not load\"}\n", sc->name, sc->shade);
            BrActorRemove(actor);
            failed++;
            continue;
        }
        if (sc->white) material->colour = BR_COLOUR_RGB(255, 255, 255);
        if (sc->texture != NULL
            && (material->colour_map = sc->pal ? load_texture8_pal(dat, sc->texture, palette)
                                       : sc->index8 || sc->shade ? load_texture8(dat, sc->texture)
                                                                 : load_texture(dat, sc->texture, sc->hicolor)) == NULL) {
            printf("{\"scene\":\"%s\",\"error\":\"texture %s did not load\"}\n", sc->name, sc->texture);
            BrActorRemove(actor);
            failed++;
            continue;
        }
        BrMaterialUpdate(material, BR_MATU_ALL);
        BrModelUpdate(model, BR_MODU_ALL);
        actor->model = model;
        actor->material = material;
        if (sc->light) BrLightEnable(light_actor);
        else BrLightDisable(light_actor);
#if !PARITY_PERIOD
        BrRendererFrameBegin();
#endif
        {
            br_pixelmap *target = sc->index8 ? colour8 : sc->hicolor == 555 ? colour555 : sc->hicolor == 565 ? colour565 : colour;
            BrPixelmapFill(target, 0);
            BrPixelmapFill(depth, DEPTH_CLEAR);
            if (sc->zs) BrZsSceneRender(world, camera_actor, target);
            else BrZbSceneRender(world, camera_actor, target, depth);
#if !PARITY_PERIOD
            BrRendererFrameEnd();
#endif
            lit = count_lit(target);
            snprintf(path, sizeof(path), "%s/%s.ppm", out, sc->name);
            if (!dump_ppm(target, palette, path)) failed++;
        }
        printf("{\"scene\":\"%s\",\"model\":\"%s\",\"flags\":%u,\"light\":%d,\"lit_pixels\":%ld}\n", sc->name, sc->model,
               (unsigned)sc->flags, sc->light, lit);
        BrActorRemove(actor); /* one model in the world at a time */
    }
    fflush(stdout);
    /* As the period rung does, let BrEnd reclaim the rest at exit. */
    return failed ? 11 : 0;
}
