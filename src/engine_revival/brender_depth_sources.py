from __future__ import annotations


def depth_smoke_source() -> str:
    """C source for the BRender portable-core depth-buffered render smoke.

    Adds a per-pixel depth buffer to the portable rasterizer, replacing the
    painter's-algorithm limitation of the fill smoke. Two distinctly tinted
    cubes are placed at different depths so they overlap in screen space; the
    near cube is drawn first, and the depth test must then reject the far cube's
    fragments where the near cube already owns the pixel. This proves per-pixel
    occlusion (correct for concave and multi-object scenes), still with no
    assembly renderer.
    """
    return r"""/*
 * BRender v1.3.2 portable-core depth-buffered render smoke.
 *
 * Extends the solid-fill path with a per-pixel float depth buffer and z-test,
 * so occlusion is resolved per pixel instead of by painter's ordering. Two
 * cubes (a near red-tinted one and a far blue-tinted one) overlap in screen
 * space. The near cube is drawn FIRST; the far cube is drawn second and its
 * fragments must be rejected by the depth test wherever the near cube is closer.
 * A non-zero rejection count and a clean red-over-blue overlap prove the z-buffer
 * works. Everything is pure C over the memory pixelmap; no softrend driver.
 *
 * Usage: brender_core_depth_smoke [output.ppm]
 */
#define __BR_V1DB__ 1
#include "brender.h"

#include <math.h>
#include <stdio.h>
#include <stdlib.h>

#define RENDER_W 320
#define RENDER_H 240

#define COLOUR_BLACK BR_COLOUR_RGB(0, 0, 0)

static const float CUBE_VERTS[8][3] = {
    {-1.0f, -1.0f, -1.0f}, { 1.0f, -1.0f, -1.0f},
    { 1.0f,  1.0f, -1.0f}, {-1.0f,  1.0f, -1.0f},
    {-1.0f, -1.0f,  1.0f}, { 1.0f, -1.0f,  1.0f},
    { 1.0f,  1.0f,  1.0f}, {-1.0f,  1.0f,  1.0f},
};

static const int CUBE_TRIS[12][3] = {
    {4, 5, 6}, {4, 6, 7}, {1, 0, 3}, {1, 3, 2},
    {0, 4, 7}, {0, 7, 3}, {5, 1, 2}, {5, 2, 6},
    {3, 7, 6}, {3, 6, 2}, {0, 1, 5}, {0, 5, 4},
};

static float g_zbuf[RENDER_H * RENDER_W];   /* depth = homogeneous w; smaller is nearer */
static long  g_rejections;                  /* fragments rejected by the depth test */

static void zbuf_clear(void)
{
    int i;
    for (i = 0; i < RENDER_H * RENDER_W; i++) {
        g_zbuf[i] = 1.0e30f;
    }
}

static int lit(br_pixelmap *pm, int x, int y)
{
    return BrPixelmapPixelGet(pm, x, y) != COLOUR_BLACK;
}

/*
 * Depth-tested flat-fill of a screen triangle whose vertices carry a depth w.
 * Interpolates depth linearly in screen space and z-tests each pixel.
 */
static void fill_triangle_z(br_pixelmap *pm,
    int x0, int y0, float w0, int x1, int y1, float w1,
    int x2, int y2, float w2, br_uint_32 colour)
{
    int y, ymin, ymax;

    ymin = y0; if (y1 < ymin) ymin = y1; if (y2 < ymin) ymin = y2;
    ymax = y0; if (y1 > ymax) ymax = y1; if (y2 > ymax) ymax = y2;
    if (ymin < 0) ymin = 0;
    if (ymax >= RENDER_H) ymax = RENDER_H - 1;

    for (y = ymin; y <= ymax; y++) {
        /* Gather edge crossings for this scanline: x and depth at the crossing. */
        int hx[3];
        float hw[3];
        int n = 0;
        int e;
        int ex[3][2], ey[3][2];
        float ew[3][2];
        int lo_i, hi_i, x;

        ex[0][0] = x0; ey[0][0] = y0; ew[0][0] = w0; ex[0][1] = x1; ey[0][1] = y1; ew[0][1] = w1;
        ex[1][0] = x1; ey[1][0] = y1; ew[1][0] = w1; ex[1][1] = x2; ey[1][1] = y2; ew[1][1] = w2;
        ex[2][0] = x2; ey[2][0] = y2; ew[2][0] = w2; ex[2][1] = x0; ey[2][1] = y0; ew[2][1] = w0;

        for (e = 0; e < 3; e++) {
            int ya = ey[e][0], yb = ey[e][1];
            if (ya == yb) {
                continue;
            }
            if ((y >= ya && y < yb) || (y >= yb && y < ya)) {
                float t = (float)(y - ya) / (float)(yb - ya);
                if (n < 3) {
                    hx[n] = ex[e][0] + (int)((ex[e][1] - ex[e][0]) * t);
                    hw[n] = ew[e][0] + (ew[e][1] - ew[e][0]) * t;
                    n++;
                }
            }
        }
        if (n < 2) {
            continue;
        }
        /* Use the two extreme crossings as the span. */
        lo_i = 0; hi_i = 0;
        {
            int k;
            for (k = 1; k < n; k++) {
                if (hx[k] < hx[lo_i]) lo_i = k;
                if (hx[k] > hx[hi_i]) hi_i = k;
            }
        }
        {
            int xl = hx[lo_i], xr = hx[hi_i];
            float wl = hw[lo_i], wr = hw[hi_i];
            int span = xr - xl;
            for (x = xl; x <= xr; x++) {
                float w;
                int idx;
                if (x < 0 || x >= RENDER_W) {
                    continue;
                }
                w = (span == 0) ? wl : (wl + (wr - wl) * (float)(x - xl) / (float)span);
                idx = y * RENDER_W + x;
                if (w < g_zbuf[idx]) {
                    g_zbuf[idx] = w;
                    BrPixelmapPixelSet(pm, x, y, colour);
                } else {
                    g_rejections++;
                }
            }
        }
    }
}

/* Project + depth-rasterize one cube actor with a tint (0 = red, 1 = blue). */
static int render_cube(br_pixelmap *pm, br_model *model,
    br_actor *model_actor, br_actor *camera_actor, int tint)
{
    br_matrix4 m2s;
    int sx[8], sy[8];
    float sw[8];
    float world[8][3];
    float lx = 0.3f, ly = 0.5f, lz = 1.0f;
    float ll = (float)sqrt(lx * lx + ly * ly + lz * lz);
    int i;

    lx /= ll; ly /= ll; lz /= ll;

    BrActorToScreenMatrix4(&m2s, model_actor, camera_actor);

    for (i = 0; i < 8; i++) {
        br_vector4 clip;
        br_vector3 wpos;
        float w, ndc_x, ndc_y;
        BrMatrix4ApplyP(&clip, &model->vertices[i].p, &m2s);
        w = BrScalarToFloat(clip.v[3]);
        if (!(w > 0.0f)) {
            return 0;
        }
        ndc_x = BrScalarToFloat(clip.v[0]) / w;
        ndc_y = BrScalarToFloat(clip.v[1]) / w;
        sx[i] = (int)lround((ndc_x * 0.5f + 0.5f) * RENDER_W);
        sy[i] = (int)lround((0.5f - ndc_y * 0.5f) * RENDER_H);
        sw[i] = w;
        BrMatrix34ApplyP(&wpos, &model->vertices[i].p, &model_actor->t.t.mat);
        world[i][0] = BrScalarToFloat(wpos.v[0]);
        world[i][1] = BrScalarToFloat(wpos.v[1]);
        world[i][2] = BrScalarToFloat(wpos.v[2]);
    }

    for (i = 0; i < 12; i++) {
        int a = CUBE_TRIS[i][0], b = CUBE_TRIS[i][1], c = CUBE_TRIS[i][2];
        float ux = world[b][0] - world[a][0], uy = world[b][1] - world[a][1], uz = world[b][2] - world[a][2];
        float vx = world[c][0] - world[a][0], vy = world[c][1] - world[a][1], vz = world[c][2] - world[a][2];
        float nx = uy * vz - uz * vy, ny = uz * vx - ux * vz, nz = ux * vy - uy * vx;
        float nl = (float)sqrt(nx * nx + ny * ny + nz * nz);
        float d, shade;
        int hi, mid;
        br_uint_32 colour;
        if (nl <= 0.0f) {
            continue;
        }
        nx /= nl; ny /= nl; nz /= nl;
        d = nx * lx + ny * ly + nz * lz;
        if (d < 0.0f) d = -d;
        shade = 0.30f + 0.70f * d;
        if (shade > 1.0f) shade = 1.0f;
        hi = (int)(shade * 255.0f);
        mid = (int)(shade * 70.0f);
        colour = (tint == 0) ? BR_COLOUR_RGB(hi, mid, mid) : BR_COLOUR_RGB(mid, mid, hi);
        fill_triangle_z(pm, sx[a], sy[a], sw[a], sx[b], sy[b], sw[b], sx[c], sy[c], sw[c], colour);
    }
    return 1;
}

static void counts(br_pixelmap *pm, long *red, long *blue, long *any)
{
    int x, y;
    *red = 0; *blue = 0; *any = 0;
    for (y = 0; y < RENDER_H; y++) {
        for (x = 0; x < RENDER_W; x++) {
            br_uint_32 c = BrPixelmapPixelGet(pm, x, y);
            int r = (int)((c >> 16) & 0xff);
            int b = (int)(c & 0xff);
            if (c == COLOUR_BLACK) {
                continue;
            }
            (*any)++;
            if (r > b) (*red)++;
            else if (b > r) (*blue)++;
        }
    }
}

static int dump_ppm(br_pixelmap *pm, const char *path)
{
    FILE *f = fopen(path, "wb");
    const unsigned char *base;
    int x, y;
    if (f == NULL) return 0;
    fprintf(f, "P6\n%d %d\n255\n", (int)pm->width, (int)pm->height);
    base = (const unsigned char *)pm->pixels;
    for (y = 0; y < (int)pm->height; y++) {
        const unsigned char *row = base + (long)y * pm->row_bytes;
        for (x = 0; x < (int)pm->width; x++) {
            const unsigned char *px = row + (long)x * 3;
            unsigned char rgb[3];
            rgb[0] = px[2]; rgb[1] = px[1]; rgb[2] = px[0];
            fwrite(rgb, 1, 3, f);
        }
    }
    fclose(f);
    return 1;
}

static br_actor *make_cube_actor(br_actor *world, br_model *model,
    float tx, float ty, float tz)
{
    br_actor *a = BrActorAllocate(BR_ACTOR_MODEL, NULL);
    if (a == NULL) {
        return NULL;
    }
    a->model = model;
    BrMatrix34RotateY(&a->t.t.mat, BR_ANGLE_DEG(30));
    BrMatrix34PreRotateX(&a->t.t.mat, BR_ANGLE_DEG(20));
    a->t.t.mat.m[3][0] = BrFloatToScalar(tx);
    a->t.t.mat.m[3][1] = BrFloatToScalar(ty);
    a->t.t.mat.m[3][2] = BrFloatToScalar(tz);
    BrActorAdd(world, a);
    return a;
}

int main(int argc, char **argv)
{
    const char *out_path = (argc > 1) ? argv[1] : "brender-core-depth-smoke.ppm";
    br_pixelmap *pm;
    br_actor *world, *camera_actor, *near_actor, *far_actor;
    br_camera *camera;
    br_model *model;
    long red, blue, any;
    int i;

    if (BrBegin() != BRE_OK) {
        return 1;
    }
    pm = BrPixelmapAllocate(BR_PMT_RGB_888, RENDER_W, RENDER_H, NULL, BR_PMAF_NORMAL);
    if (pm == NULL || pm->pixels == NULL) { BrEnd(); return 2; }
    BrPixelmapFill(pm, COLOUR_BLACK);
    zbuf_clear();
    g_rejections = 0;

    world = BrActorAllocate(BR_ACTOR_NONE, NULL);
    camera_actor = BrActorAllocate(BR_ACTOR_CAMERA, NULL);
    if (world == NULL || camera_actor == NULL || camera_actor->type_data == NULL) {
        BrPixelmapFree(pm); BrEnd(); return 3;
    }
    camera = (br_camera *)camera_actor->type_data;
    camera->type = BR_CAMERA_PERSPECTIVE;
    camera->field_of_view = BR_ANGLE_DEG(60);
    camera->hither_z = BrFloatToScalar(1.0f);
    camera->yon_z = BrFloatToScalar(100.0f);
    camera->aspect = BrFloatToScalar((float)RENDER_W / (float)RENDER_H);
    BrMatrix34Translate(&camera_actor->t.t.mat,
        BrFloatToScalar(0.0f), BrFloatToScalar(0.0f), BrFloatToScalar(7.0f));
    BrActorAdd(world, camera_actor);

    model = BrModelAllocate("cube", 8, 12);
    if (model == NULL || model->vertices == NULL || model->faces == NULL) {
        BrPixelmapFree(pm); BrEnd(); return 4;
    }
    for (i = 0; i < 8; i++) {
        BrVector3SetFloat(&model->vertices[i].p, CUBE_VERTS[i][0], CUBE_VERTS[i][1], CUBE_VERTS[i][2]);
    }
    for (i = 0; i < 12; i++) {
        model->faces[i].vertices[0] = (br_uint_16)CUBE_TRIS[i][0];
        model->faces[i].vertices[1] = (br_uint_16)CUBE_TRIS[i][1];
        model->faces[i].vertices[2] = (br_uint_16)CUBE_TRIS[i][2];
        model->faces[i].material = NULL;
        model->faces[i].smoothing = 0;
    }
    model->flags = BR_MODF_UPDATEABLE;
    BrModelUpdate(model, BR_MODU_ALL);

    /* Near cube (red) slightly left; far cube (blue) right and pushed back so
       they overlap in screen space. */
    near_actor = make_cube_actor(world, model, -0.9f, 0.0f, 0.5f);
    far_actor  = make_cube_actor(world, model,  0.9f, 0.0f, -2.5f);
    if (near_actor == NULL || far_actor == NULL) {
        BrPixelmapFree(pm); BrEnd(); return 5;
    }

    /* Draw the NEAR cube first, then the FAR cube: the depth test must reject
       the far cube where the near cube is closer. */
    if (!render_cube(pm, model, near_actor, camera_actor, 0)) {
        BrPixelmapFree(pm); BrEnd(); return 6;
    }
    g_rejections = 0; /* count only rejections caused while drawing the far cube */
    if (!render_cube(pm, model, far_actor, camera_actor, 1)) {
        BrPixelmapFree(pm); BrEnd(); return 7;
    }

    counts(pm, &red, &blue, &any);

    /* Both cubes visible. */
    if (red < 500 || blue < 500) {
        BrPixelmapFree(pm); BrEnd(); return 8;
    }
    /* The far cube lost fragments to the depth test: per-pixel occlusion. */
    if (g_rejections <= 0) {
        BrPixelmapFree(pm); BrEnd(); return 9;
    }
    /* Sanity on total coverage. */
    if (any < 2000 || any >= (long)(RENDER_W * RENDER_H)) {
        BrPixelmapFree(pm); BrEnd(); return 10;
    }

    if (!dump_ppm(pm, out_path)) {
        BrPixelmapFree(pm); BrEnd(); return 11;
    }

    printf("brender depth smoke: %dx%d, red(near)=%ld blue(far)=%ld lit=%ld, far-cube depth rejections=%ld, wrote %s\n",
        RENDER_W, RENDER_H, red, blue, any, g_rejections, out_path);

    BrPixelmapFree(pm);
    if (BrEnd() != BRE_OK) {
        return 12;
    }
    return 0;
}
"""
