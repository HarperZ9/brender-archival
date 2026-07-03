from __future__ import annotations


def texture_smoke_source() -> str:
    """C source for the BRender portable-core textured render smoke.

    Adds perspective-correct texture mapping to the depth-buffered rasterizer: a
    checkerboard texture pixelmap is sampled per pixel with u/w, v/w, 1/w
    interpolation, modulated by the flat face shade, and depth-tested on 1/w.
    This is the rung that lets the portable path render textured surfaces, still
    with no assembly renderer.
    """
    return r"""/*
 * BRender v1.3.2 portable-core textured render smoke.
 *
 * Perspective-correct texture mapping over the depth-buffered rasterizer. A
 * checkerboard is built in a BRender texture pixelmap and sampled per pixel:
 * u/w, v/w and 1/w are interpolated linearly in screen space, the per-pixel
 * texel is looked up, modulated by the flat face shade, and depth-tested on 1/w.
 * A rotated cube is mapped so each face shows the full checkerboard. Pure C over
 * the memory pixelmap; no softrend driver.
 *
 * Usage: brender_core_texture_smoke [output.ppm]
 */
#define __BR_V1DB__ 1
#include "brender.h"

#include <math.h>
#include <stdio.h>
#include <stdlib.h>

#define RENDER_W 320
#define RENDER_H 240
#define TEX_W 64
#define TEX_H 64

#define COLOUR_BLACK BR_COLOUR_RGB(0, 0, 0)
#define CHECK_A BR_COLOUR_RGB(230, 120, 30)   /* warm */
#define CHECK_B BR_COLOUR_RGB(30, 150, 160)   /* cool */

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

/* Per-triangle UVs: each face's two triangles map the quad to the full texture. */
static const float TRI_UV[2][3][2] = {
    { {0.0f, 0.0f}, {1.0f, 0.0f}, {1.0f, 1.0f} },   /* first triangle of a face */
    { {0.0f, 0.0f}, {1.0f, 1.0f}, {0.0f, 1.0f} },   /* second triangle of a face */
};

static float g_zbuf[RENDER_H * RENDER_W];   /* depth = 1/w; larger is nearer */

typedef struct { int x, y; float iw, uow, vow; } tvert;

static int lit(br_pixelmap *pm, int x, int y)
{
    return BrPixelmapPixelGet(pm, x, y) != COLOUR_BLACK;
}

/* Perspective-correct, depth-tested, textured triangle fill. */
static void fill_triangle_tex(br_pixelmap *pm, br_pixelmap *tex,
    tvert a, tvert b, tvert c, float shade)
{
    tvert v[3];
    int y, ymin, ymax;

    v[0] = a; v[1] = b; v[2] = c;
    ymin = v[0].y; if (v[1].y < ymin) ymin = v[1].y; if (v[2].y < ymin) ymin = v[2].y;
    ymax = v[0].y; if (v[1].y > ymax) ymax = v[1].y; if (v[2].y > ymax) ymax = v[2].y;
    if (ymin < 0) ymin = 0;
    if (ymax >= RENDER_H) ymax = RENDER_H - 1;

    for (y = ymin; y <= ymax; y++) {
        /* Edge crossings carry x plus the perspective-correct varyings. */
        float cx[3], ciw[3], cuo[3], cvo[3];
        int n = 0;
        int e, lo, hi, x;

        for (e = 0; e < 3; e++) {
            tvert p0 = v[e], p1 = v[(e + 1) % 3];
            int ya = p0.y, yb = p1.y;
            if (ya == yb) {
                continue;
            }
            if ((y >= ya && y < yb) || (y >= yb && y < ya)) {
                float t = (float)(y - ya) / (float)(yb - ya);
                if (n < 3) {
                    cx[n]  = p0.x  + (p1.x  - p0.x)  * t;
                    ciw[n] = p0.iw + (p1.iw - p0.iw) * t;
                    cuo[n] = p0.uow + (p1.uow - p0.uow) * t;
                    cvo[n] = p0.vow + (p1.vow - p0.vow) * t;
                    n++;
                }
            }
        }
        if (n < 2) {
            continue;
        }
        lo = 0; hi = 0;
        {
            int k;
            for (k = 1; k < n; k++) {
                if (cx[k] < cx[lo]) lo = k;
                if (cx[k] > cx[hi]) hi = k;
            }
        }
        {
            int xl = (int)(cx[lo] + 0.5f), xr = (int)(cx[hi] + 0.5f);
            float span = cx[hi] - cx[lo];
            for (x = xl; x <= xr; x++) {
                float f, iw, uo, vo, u, vv;
                int idx, tu, tv, r, g, bl;
                br_uint_32 texel;
                if (x < 0 || x >= RENDER_W) {
                    continue;
                }
                f = (span == 0.0f) ? 0.0f : ((float)x - cx[lo]) / span;
                iw = ciw[lo] + (ciw[hi] - ciw[lo]) * f;
                if (iw <= 0.0f) {
                    continue;
                }
                idx = y * RENDER_W + x;
                if (iw <= g_zbuf[idx]) {
                    continue;   /* farther than or equal to what's already there */
                }
                uo = cuo[lo] + (cuo[hi] - cuo[lo]) * f;
                vo = cvo[lo] + (cvo[hi] - cvo[lo]) * f;
                u = uo / iw;
                vv = vo / iw;
                tu = (int)(u * TEX_W); tu &= (TEX_W - 1);
                tv = (int)(vv * TEX_H); tv &= (TEX_H - 1);
                if (tu < 0) tu += TEX_W;
                if (tv < 0) tv += TEX_H;
                texel = BrPixelmapPixelGet(tex, tu, tv);
                r  = (int)(((texel >> 16) & 0xff) * shade);
                g  = (int)(((texel >> 8) & 0xff) * shade);
                bl = (int)((texel & 0xff) * shade);
                g_zbuf[idx] = iw;
                BrPixelmapPixelSet(pm, x, y, BR_COLOUR_RGB(r, g, bl));
            }
        }
    }
}

static void warm_cool(br_pixelmap *pm, long *warm, long *cool, long *any)
{
    int x, y;
    *warm = 0; *cool = 0; *any = 0;
    for (y = 0; y < RENDER_H; y++) {
        for (x = 0; x < RENDER_W; x++) {
            br_uint_32 c = BrPixelmapPixelGet(pm, x, y);
            int r = (int)((c >> 16) & 0xff), b = (int)(c & 0xff);
            if (c == COLOUR_BLACK) continue;
            (*any)++;
            if (r > b + 20) (*warm)++;
            else if (b > r + 20) (*cool)++;
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

int main(int argc, char **argv)
{
    const char *out_path = (argc > 1) ? argv[1] : "brender-core-texture-smoke.ppm";
    br_pixelmap *pm, *tex;
    br_actor *world, *camera_actor, *model_actor;
    br_camera *camera;
    br_model *model;
    br_matrix4 m2s;
    float lx = 0.3f, ly = 0.5f, lz = 1.0f, ll;
    long warm, cool, any;
    int i, tx, ty;

    ll = (float)sqrt(lx * lx + ly * ly + lz * lz);
    lx /= ll; ly /= ll; lz /= ll;

    if (BrBegin() != BRE_OK) return 1;

    pm = BrPixelmapAllocate(BR_PMT_RGB_888, RENDER_W, RENDER_H, NULL, BR_PMAF_NORMAL);
    if (pm == NULL || pm->pixels == NULL) { BrEnd(); return 2; }
    BrPixelmapFill(pm, COLOUR_BLACK);
    for (i = 0; i < RENDER_H * RENDER_W; i++) {
        g_zbuf[i] = 0.0f;   /* 1/w depth; larger is nearer, so 0 == empty/far */
    }

    /* Build a checkerboard texture pixelmap. */
    tex = BrPixelmapAllocate(BR_PMT_RGB_888, TEX_W, TEX_H, NULL, BR_PMAF_NORMAL);
    if (tex == NULL || tex->pixels == NULL) { BrPixelmapFree(pm); BrEnd(); return 3; }
    for (ty = 0; ty < TEX_H; ty++) {
        for (tx = 0; tx < TEX_W; tx++) {
            int check = ((tx >> 3) + (ty >> 3)) & 1;
            BrPixelmapPixelSet(tex, tx, ty, check ? CHECK_A : CHECK_B);
        }
    }

    world = BrActorAllocate(BR_ACTOR_NONE, NULL);
    camera_actor = BrActorAllocate(BR_ACTOR_CAMERA, NULL);
    if (world == NULL || camera_actor == NULL || camera_actor->type_data == NULL) {
        BrPixelmapFree(tex); BrPixelmapFree(pm); BrEnd(); return 4;
    }
    camera = (br_camera *)camera_actor->type_data;
    camera->type = BR_CAMERA_PERSPECTIVE;
    camera->field_of_view = BR_ANGLE_DEG(60);
    camera->hither_z = BrFloatToScalar(1.0f);
    camera->yon_z = BrFloatToScalar(100.0f);
    camera->aspect = BrFloatToScalar((float)RENDER_W / (float)RENDER_H);
    BrMatrix34Translate(&camera_actor->t.t.mat,
        BrFloatToScalar(0.0f), BrFloatToScalar(0.0f), BrFloatToScalar(5.0f));
    BrActorAdd(world, camera_actor);

    model = BrModelAllocate("cube", 8, 12);
    if (model == NULL || model->vertices == NULL) {
        BrPixelmapFree(tex); BrPixelmapFree(pm); BrEnd(); return 5;
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

    model_actor = BrActorAllocate(BR_ACTOR_MODEL, NULL);
    if (model_actor == NULL) { BrPixelmapFree(tex); BrPixelmapFree(pm); BrEnd(); return 6; }
    model_actor->model = model;
    BrMatrix34RotateY(&model_actor->t.t.mat, BR_ANGLE_DEG(35));
    BrMatrix34PreRotateX(&model_actor->t.t.mat, BR_ANGLE_DEG(25));
    BrActorAdd(world, model_actor);

    BrActorToScreenMatrix4(&m2s, model_actor, camera_actor);

    /* Project vertices to screen with 1/w for perspective-correct interpolation. */
    {
        int sx[8], sy[8];
        float siw[8];
        float world_p[8][3];
        for (i = 0; i < 8; i++) {
            br_vector4 clip;
            br_vector3 wpos;
            float w, ndc_x, ndc_y;
            BrMatrix4ApplyP(&clip, &model->vertices[i].p, &m2s);
            w = BrScalarToFloat(clip.v[3]);
            if (!(w > 0.0f)) { BrPixelmapFree(tex); BrPixelmapFree(pm); BrEnd(); return 7; }
            ndc_x = BrScalarToFloat(clip.v[0]) / w;
            ndc_y = BrScalarToFloat(clip.v[1]) / w;
            sx[i] = (int)lround((ndc_x * 0.5f + 0.5f) * RENDER_W);
            sy[i] = (int)lround((0.5f - ndc_y * 0.5f) * RENDER_H);
            siw[i] = 1.0f / w;
            BrMatrix34ApplyP(&wpos, &model->vertices[i].p, &model_actor->t.t.mat);
            world_p[i][0] = BrScalarToFloat(wpos.v[0]);
            world_p[i][1] = BrScalarToFloat(wpos.v[1]);
            world_p[i][2] = BrScalarToFloat(wpos.v[2]);
        }

        for (i = 0; i < 12; i++) {
            int a = CUBE_TRIS[i][0], b = CUBE_TRIS[i][1], c = CUBE_TRIS[i][2];
            const float (*uv)[2] = TRI_UV[i & 1];
            float ux = world_p[b][0] - world_p[a][0], uy = world_p[b][1] - world_p[a][1], uz = world_p[b][2] - world_p[a][2];
            float vx = world_p[c][0] - world_p[a][0], vy = world_p[c][1] - world_p[a][1], vz = world_p[c][2] - world_p[a][2];
            float nx = uy * vz - uz * vy, ny = uz * vx - ux * vz, nz = ux * vy - uy * vx;
            float nl = (float)sqrt(nx * nx + ny * ny + nz * nz), d, shade;
            tvert va, vb, vc;
            if (nl <= 0.0f) continue;
            nx /= nl; ny /= nl; nz /= nl;
            d = nx * lx + ny * ly + nz * lz; if (d < 0.0f) d = -d;
            shade = 0.45f + 0.55f * d; if (shade > 1.0f) shade = 1.0f;

            va.x = sx[a]; va.y = sy[a]; va.iw = siw[a]; va.uow = uv[0][0] * siw[a]; va.vow = uv[0][1] * siw[a];
            vb.x = sx[b]; vb.y = sy[b]; vb.iw = siw[b]; vb.uow = uv[1][0] * siw[b]; vb.vow = uv[1][1] * siw[b];
            vc.x = sx[c]; vc.y = sy[c]; vc.iw = siw[c]; vc.uow = uv[2][0] * siw[c]; vc.vow = uv[2][1] * siw[c];
            fill_triangle_tex(pm, tex, va, vb, vc, shade);
        }
    }

    warm_cool(pm, &warm, &cool, &any);

    if (any < 3000 || any >= (long)(RENDER_W * RENDER_H)) { BrPixelmapFree(tex); BrPixelmapFree(pm); BrEnd(); return 8; }
    /* Both checkerboard colours must appear: proves the texture is sampled. */
    if (warm < 300 || cool < 300) { BrPixelmapFree(tex); BrPixelmapFree(pm); BrEnd(); return 9; }

    if (!dump_ppm(pm, out_path)) { BrPixelmapFree(tex); BrPixelmapFree(pm); BrEnd(); return 10; }

    printf("brender texture smoke: %dx%d, lit=%ld warm=%ld cool=%ld (%dx%d checker texture), wrote %s\n",
        RENDER_W, RENDER_H, any, warm, cool, TEX_W, TEX_H, out_path);

    BrPixelmapFree(tex);
    BrPixelmapFree(pm);
    if (BrEnd() != BRE_OK) return 11;
    return 0;
}
"""
