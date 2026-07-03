from __future__ import annotations


def render_smoke_source() -> str:
    """C source for the BRender portable-core render smoke.

    The program exercises the pure-C rendering path with no assembly software
    renderer, no DOS layer, and no driver DLL: it starts the framework, builds
    a real BRender perspective projection, transforms a unit cube through the
    engine matrix pipeline, rasterizes the wireframe into an in-memory pixelmap
    through the memory dispatch table (backed only by the harness _Mem*
    primitives), reads pixels back to verify, and dumps a portable PPM image.
    """
    return r"""/*
 * BRender v1.3.2 portable-core render smoke.
 *
 * This is the first BRender revival milestone that produces an actual rendered
 * image instead of only starting the framework. It draws a projected 3D
 * wireframe cube into an in-memory pixelmap using ONLY the pure-C path:
 *
 *   BrBegin
 *     -> BrPixelmapAllocate(BR_PMT_RGB_888, ...)   (memory pixelmap, no driver)
 *     -> BrPixelmapFill                            (clear, via _MemFill_A stub)
 *     -> BrMatrix4Identity / BrMatrix4Mul          (engine matrix pipeline)
 *     -> BrMatrix4Perspective                      (engine projection, libc trig)
 *     -> BrMatrix4ApplyP                           (engine point transform)
 *     -> BrPixelmapLine / PixelSet / PixelGet      (memory dispatch, pure C)
 *     -> raw PPM dump of pm->pixels
 *   BrEnd
 *
 * Every plotting call flows through the memory pixelmap dispatch table in
 * core/pixelmap/pmmem.c, which is pure C and calls the _MemPixelSet / _MemFill
 * primitives the harness supplies. The assembly softrend driver is NOT used.
 *
 * The program is self-verifying: it asserts fill, pixel set/get round-trip,
 * deterministic line endpoints, all eight cube vertices projecting in front of
 * the camera, and a plausible count of lit pixels. It returns 0 only when every
 * check passes; each failure returns a distinct non-zero code.
 *
 * Usage: brender_core_render_smoke [output.ppm]
 */
#define __BR_V1DB__ 0
#include "brender.h"

#include <math.h>
#include <stdio.h>
#include <stdlib.h>

#define RENDER_W 320
#define RENDER_H 240

#define COLOUR_BLACK BR_COLOUR_RGB(0, 0, 0)
#define COLOUR_WHITE BR_COLOUR_RGB(255, 255, 255)
#define COLOUR_RED   BR_COLOUR_RGB(255, 0, 0)
#define COLOUR_GREEN BR_COLOUR_RGB(0, 255, 0)

/* Eight corners of a unit cube in model space. */
static const float CUBE_VERTS[8][3] = {
    {-1.0f, -1.0f, -1.0f}, { 1.0f, -1.0f, -1.0f},
    { 1.0f,  1.0f, -1.0f}, {-1.0f,  1.0f, -1.0f},
    {-1.0f, -1.0f,  1.0f}, { 1.0f, -1.0f,  1.0f},
    { 1.0f,  1.0f,  1.0f}, {-1.0f,  1.0f,  1.0f},
};

/* Twelve edges connecting those corners. */
static const int CUBE_EDGES[12][2] = {
    {0, 1}, {1, 2}, {2, 3}, {3, 0},
    {4, 5}, {5, 6}, {6, 7}, {7, 4},
    {0, 4}, {1, 5}, {2, 6}, {3, 7},
};

static void set_identity_rot(br_matrix4 *m)
{
    BrMatrix4Identity(m);
}

/* Row-vector rotation about the Y axis (sign only affects spin direction). */
static void rotation_y(br_matrix4 *m, float radians)
{
    float c = (float)cos(radians);
    float s = (float)sin(radians);

    set_identity_rot(m);
    m->m[0][0] = BrFloatToScalar(c);
    m->m[0][2] = BrFloatToScalar(-s);
    m->m[2][0] = BrFloatToScalar(s);
    m->m[2][2] = BrFloatToScalar(c);
}

/* Row-vector rotation about the X axis. */
static void rotation_x(br_matrix4 *m, float radians)
{
    float c = (float)cos(radians);
    float s = (float)sin(radians);

    set_identity_rot(m);
    m->m[1][1] = BrFloatToScalar(c);
    m->m[1][2] = BrFloatToScalar(s);
    m->m[2][1] = BrFloatToScalar(-s);
    m->m[2][2] = BrFloatToScalar(c);
}

static int lit(br_pixelmap *pm, int x, int y)
{
    return BrPixelmapPixelGet(pm, x, y) != COLOUR_BLACK;
}

static br_uint_32 count_lit(br_pixelmap *pm)
{
    br_uint_32 total = 0;
    int x, y;

    for (y = 0; y < RENDER_H; y++) {
        for (x = 0; x < RENDER_W; x++) {
            if (lit(pm, x, y)) {
                total++;
            }
        }
    }
    return total;
}

/*
 * Dump an RGB_888 pixelmap to a binary PPM (P6). RGB_888 pixels are stored in
 * memory as B, G, R (little-endian of a 0x00RRGGBB colour), so the channels are
 * reordered to the R, G, B order PPM expects.
 */
static int dump_ppm(br_pixelmap *pm, const char *path)
{
    FILE *f = fopen(path, "wb");
    const unsigned char *base;
    int x, y;

    if (f == NULL) {
        return 0;
    }
    fprintf(f, "P6\n%d %d\n255\n", (int)pm->width, (int)pm->height);
    base = (const unsigned char *)pm->pixels;
    for (y = 0; y < (int)pm->height; y++) {
        const unsigned char *row = base + (long)y * pm->row_bytes;
        for (x = 0; x < (int)pm->width; x++) {
            const unsigned char *px = row + (long)x * 3;
            unsigned char rgb[3];
            rgb[0] = px[2];
            rgb[1] = px[1];
            rgb[2] = px[0];
            fwrite(rgb, 1, 3, f);
        }
    }
    fclose(f);
    return 1;
}

int main(int argc, char **argv)
{
    const char *out_path = (argc > 1) ? argv[1] : "brender-core-render-smoke.ppm";
    br_pixelmap *pm;
    br_matrix4 rot_y, rot_x, model_view, proj, model_to_screen;
    int screen_x[8];
    int screen_y[8];
    br_uint_32 total_lit;
    int i;

    if (BrBegin() != BRE_OK) {
        return 1;
    }

    pm = BrPixelmapAllocate(BR_PMT_RGB_888, RENDER_W, RENDER_H, NULL, BR_PMAF_NORMAL);
    if (pm == NULL) {
        BrEnd();
        return 2;
    }
    if (pm->pixels == NULL || pm->width != RENDER_W || pm->height != RENDER_H) {
        BrPixelmapFree(pm);
        BrEnd();
        return 3;
    }

    /* Clear the framebuffer and confirm the fill actually reached memory. */
    BrPixelmapFill(pm, COLOUR_BLACK);
    if (lit(pm, 0, 0) || lit(pm, RENDER_W / 2, RENDER_H / 2) || lit(pm, RENDER_W - 1, RENDER_H - 1)) {
        BrPixelmapFree(pm);
        BrEnd();
        return 4;
    }

    /* Pixel set/get round-trip on a non-symmetric colour proves the channels. */
    BrPixelmapPixelSet(pm, 10, 10, COLOUR_GREEN);
    if (BrPixelmapPixelGet(pm, 10, 10) != COLOUR_GREEN) {
        BrPixelmapFree(pm);
        BrEnd();
        return 5;
    }

    /*
     * Build model->screen through the engine matrix pipeline:
     *   model_view = rot_y * rot_x, with a translation down -Z (camera at -Z),
     *   model_to_screen = model_view * perspective.
     */
    rotation_y(&rot_y, 0.6f);
    rotation_x(&rot_x, 0.5f);
    BrMatrix4Mul(&model_view, &rot_y, &rot_x);
    model_view.m[3][0] = BrFloatToScalar(0.0f);
    model_view.m[3][1] = BrFloatToScalar(0.0f);
    model_view.m[3][2] = BrFloatToScalar(-5.0f);
    model_view.m[3][3] = BrFloatToScalar(1.0f);

    BrMatrix4Perspective(&proj,
        BR_ANGLE_DEG(60),
        BrFloatToScalar((float)RENDER_W / (float)RENDER_H),
        BrFloatToScalar(1.0f),
        BrFloatToScalar(100.0f));

    BrMatrix4Mul(&model_to_screen, &model_view, &proj);

    /* Project the eight corners and map clip space to pixels. */
    for (i = 0; i < 8; i++) {
        br_vector3 v;
        br_vector4 clip;
        float w, ndc_x, ndc_y;

        BrVector3SetFloat(&v, CUBE_VERTS[i][0], CUBE_VERTS[i][1], CUBE_VERTS[i][2]);
        BrMatrix4ApplyP(&clip, &v, &model_to_screen);

        w = BrScalarToFloat(clip.v[3]);
        if (!(w > 0.0f)) {
            /* Every corner must sit in front of the camera. */
            BrPixelmapFree(pm);
            BrEnd();
            return 6;
        }
        ndc_x = BrScalarToFloat(clip.v[0]) / w;
        ndc_y = BrScalarToFloat(clip.v[1]) / w;
        screen_x[i] = (int)lround((ndc_x * 0.5f + 0.5f) * RENDER_W);
        screen_y[i] = (int)lround((0.5f - ndc_y * 0.5f) * RENDER_H);
    }

    /* At least half the projected corners should land inside the viewport. */
    {
        int inside = 0;
        for (i = 0; i < 8; i++) {
            if (screen_x[i] >= 0 && screen_x[i] < RENDER_W &&
                screen_y[i] >= 0 && screen_y[i] < RENDER_H) {
                inside++;
            }
        }
        if (inside < 4) {
            BrPixelmapFree(pm);
            BrEnd();
            return 7;
        }
    }

    /* Draw the wireframe. */
    for (i = 0; i < 12; i++) {
        int a = CUBE_EDGES[i][0];
        int b = CUBE_EDGES[i][1];
        BrPixelmapLine(pm, screen_x[a], screen_y[a], screen_x[b], screen_y[b], COLOUR_WHITE);
    }

    /*
     * A deterministic diagonal whose endpoints are guaranteed plotted. This
     * pins the line/pixel-get path independently of the projection maths.
     */
    BrPixelmapLine(pm, 0, 0, RENDER_W - 1, RENDER_H - 1, COLOUR_RED);
    if (BrPixelmapPixelGet(pm, 0, 0) != COLOUR_RED ||
        BrPixelmapPixelGet(pm, RENDER_W - 1, RENDER_H - 1) != COLOUR_RED) {
        BrPixelmapFree(pm);
        BrEnd();
        return 8;
    }

    /* Substantial geometry, but not a fully-lit buffer. */
    total_lit = count_lit(pm);
    if (total_lit < 200 || total_lit >= (br_uint_32)(RENDER_W * RENDER_H)) {
        BrPixelmapFree(pm);
        BrEnd();
        return 9;
    }

    if (!dump_ppm(pm, out_path)) {
        BrPixelmapFree(pm);
        BrEnd();
        return 10;
    }

    printf("brender render smoke: %dx%d RGB_888, %lu lit pixels, wrote %s\n",
        RENDER_W, RENDER_H, (unsigned long)total_lit, out_path);
    for (i = 0; i < 8; i++) {
        printf("  vertex %d -> (%d, %d)\n", i, screen_x[i], screen_y[i]);
    }

    BrPixelmapFree(pm);

    if (BrEnd() != BRE_OK) {
        return 11;
    }

    return 0;
}
"""
