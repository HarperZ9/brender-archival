from __future__ import annotations


def model_smoke_source() -> str:
    """C source for the BRender portable-core datafile-model render smoke.

    The capstone of the portable render path: it loads a real period BRender
    model from a native .dat datafile with BrModelLoad (through BRender's own
    stdio datafile reader), auto-frames it from its computed bounds, projects it
    with the engine's BrActorToScreenMatrix4, and renders it solid, flat-shaded
    and depth-buffered with the portable rasterizer. Real BRender content renders
    again, still with no assembly renderer.
    """
    return r"""/*
 * BRender v1.3.2 portable-core datafile-model render smoke.
 *
 * Loads a real period BRender model from a native binary .dat datafile and
 * renders it, closing the loop from "the engine starts up" to "real BRender
 * content renders again", all on the pure-C path:
 *
 *   BrBegin
 *     -> model = BrModelLoad("<...>/dat/<model>.dat")   (BRender's stdio datafile reader)
 *     -> auto-frame from the model's own vertex bounds
 *     -> world/camera/model actor tree + BrActorToScreenMatrix4 (engine transform)
 *     -> flat-shaded, depth-buffered scanline rasterization of every face
 *   BrEnd
 *
 * BrModelLoad needs nothing beyond BrBegin: its chunk-handler table is static
 * and file I/O goes through BRender's default stdio filesystem. Face normals are
 * computed from the loaded geometry, so no material or texture is required.
 *
 * Usage: brender_core_model_smoke <model.dat> [output.ppm]
 */
#define __BR_V1DB__ 1
#include "brender.h"

#include <math.h>
#include <stdio.h>
#include <stdlib.h>

#define RENDER_W 320
#define RENDER_H 240
#define COLOUR_BLACK BR_COLOUR_RGB(0, 0, 0)

static float g_zbuf[RENDER_H * RENDER_W];

static int lit(br_pixelmap *pm, int x, int y)
{
    return BrPixelmapPixelGet(pm, x, y) != COLOUR_BLACK;
}

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
        int hx[3]; float hw[3];
        int n = 0, e, lo, hi, x;
        int ex[3][2], ey[3][2]; float ew[3][2];
        ex[0][0]=x0; ey[0][0]=y0; ew[0][0]=w0; ex[0][1]=x1; ey[0][1]=y1; ew[0][1]=w1;
        ex[1][0]=x1; ey[1][0]=y1; ew[1][0]=w1; ex[1][1]=x2; ey[1][1]=y2; ew[1][1]=w2;
        ex[2][0]=x2; ey[2][0]=y2; ew[2][0]=w2; ex[2][1]=x0; ey[2][1]=y0; ew[2][1]=w0;
        for (e = 0; e < 3; e++) {
            int ya = ey[e][0], yb = ey[e][1];
            if (ya == yb) continue;
            if ((y >= ya && y < yb) || (y >= yb && y < ya)) {
                float t = (float)(y - ya) / (float)(yb - ya);
                if (n < 3) { hx[n] = ex[e][0] + (int)((ex[e][1]-ex[e][0])*t); hw[n] = ew[e][0] + (ew[e][1]-ew[e][0])*t; n++; }
            }
        }
        if (n < 2) continue;
        lo = 0; hi = 0;
        { int k; for (k = 1; k < n; k++) { if (hx[k] < hx[lo]) lo = k; if (hx[k] > hx[hi]) hi = k; } }
        {
            int xl = hx[lo], xr = hx[hi]; float wl = hw[lo], wr = hw[hi]; int span = xr - xl;
            for (x = xl; x <= xr; x++) {
                float w; int idx;
                if (x < 0 || x >= RENDER_W) continue;
                w = (span == 0) ? wl : (wl + (wr - wl) * (float)(x - xl) / (float)span);
                idx = y * RENDER_W + x;
                if (w < g_zbuf[idx]) { g_zbuf[idx] = w; BrPixelmapPixelSet(pm, x, y, colour); }
            }
        }
    }
}

static br_uint_32 count_lit(br_pixelmap *pm)
{
    br_uint_32 t = 0; int x, y;
    for (y = 0; y < RENDER_H; y++) for (x = 0; x < RENDER_W; x++) if (lit(pm, x, y)) t++;
    return t;
}

static int dump_ppm(br_pixelmap *pm, const char *path)
{
    FILE *f = fopen(path, "wb");
    const unsigned char *base; int x, y;
    if (f == NULL) return 0;
    fprintf(f, "P6\n%d %d\n255\n", (int)pm->width, (int)pm->height);
    base = (const unsigned char *)pm->pixels;
    for (y = 0; y < (int)pm->height; y++) {
        const unsigned char *row = base + (long)y * pm->row_bytes;
        for (x = 0; x < (int)pm->width; x++) {
            const unsigned char *px = row + (long)x * 3;
            unsigned char rgb[3]; rgb[0]=px[2]; rgb[1]=px[1]; rgb[2]=px[0];
            fwrite(rgb, 1, 3, f);
        }
    }
    fclose(f);
    return 1;
}

int main(int argc, char **argv)
{
    const char *model_path = (argc > 1) ? argv[1] : "duck.dat";
    const char *out_path = (argc > 2) ? argv[2] : "brender-core-model-smoke.ppm";
    br_pixelmap *pm;
    br_actor *world, *camera_actor, *model_actor;
    br_camera *camera;
    br_model *model;
    br_matrix4 m2s;
    br_matrix34 mm;
    int *sx = NULL, *sy = NULL;
    float *sw = NULL, *wx = NULL, *wy = NULL, *wz = NULL;
    float cx, cy, cz, radius, s;
    float lx = 0.35f, ly = 0.55f, lz = 1.0f, ll;
    br_uint_32 total_lit;
    long drawn = 0;
    int i, nv, nf;

    ll = (float)sqrt(lx*lx + ly*ly + lz*lz); lx/=ll; ly/=ll; lz/=ll;

    if (BrBegin() != BRE_OK) return 1;

    model = BrModelLoad((char *)model_path);
    if (model == NULL) { fprintf(stderr, "BrModelLoad failed: %s\n", model_path); BrEnd(); return 2; }
    nv = (int)model->nvertices; nf = (int)model->nfaces;
    if (nv < 3 || nf < 1 || model->vertices == NULL || model->faces == NULL) {
        fprintf(stderr, "loaded model has no usable geometry (nv=%d nf=%d)\n", nv, nf);
        BrEnd(); return 3;
    }

    pm = BrPixelmapAllocate(BR_PMT_RGB_888, RENDER_W, RENDER_H, NULL, BR_PMAF_NORMAL);
    if (pm == NULL || pm->pixels == NULL) { BrEnd(); return 4; }
    BrPixelmapFill(pm, COLOUR_BLACK);
    for (i = 0; i < RENDER_H * RENDER_W; i++) g_zbuf[i] = 1.0e30f;

    /* Bounds: centre + radius from the loaded vertices, to auto-frame. */
    cx = cy = cz = 0.0f;
    for (i = 0; i < nv; i++) {
        cx += BrScalarToFloat(model->vertices[i].p.v[0]);
        cy += BrScalarToFloat(model->vertices[i].p.v[1]);
        cz += BrScalarToFloat(model->vertices[i].p.v[2]);
    }
    cx /= nv; cy /= nv; cz /= nv;
    radius = 0.0f;
    for (i = 0; i < nv; i++) {
        float dx = BrScalarToFloat(model->vertices[i].p.v[0]) - cx;
        float dy = BrScalarToFloat(model->vertices[i].p.v[1]) - cy;
        float dz = BrScalarToFloat(model->vertices[i].p.v[2]) - cz;
        float r = (float)sqrt(dx*dx + dy*dy + dz*dz);
        if (r > radius) radius = r;
    }
    if (radius <= 0.0f) { BrPixelmapFree(pm); BrEnd(); return 5; }
    s = 1.6f / radius;   /* scale so the model fills roughly the view */

    world = BrActorAllocate(BR_ACTOR_NONE, NULL);
    camera_actor = BrActorAllocate(BR_ACTOR_CAMERA, NULL);
    if (world == NULL || camera_actor == NULL || camera_actor->type_data == NULL) {
        BrPixelmapFree(pm); BrEnd(); return 6;
    }
    camera = (br_camera *)camera_actor->type_data;
    camera->type = BR_CAMERA_PERSPECTIVE;
    camera->field_of_view = BR_ANGLE_DEG(55);
    camera->hither_z = BrFloatToScalar(0.5f);
    camera->yon_z = BrFloatToScalar(500.0f);
    camera->aspect = BrFloatToScalar((float)RENDER_W / (float)RENDER_H);
    BrMatrix34Translate(&camera_actor->t.t.mat,
        BrFloatToScalar(0.0f), BrFloatToScalar(0.0f), BrFloatToScalar(5.0f));
    BrActorAdd(world, camera_actor);

    /*
     * Model actor transform = centre-to-origin, uniform scale s, then a
     * three-quarter rotation. Built directly: linear part = s * R, translation
     * row = -centre . (s * R).
     */
    model_actor = BrActorAllocate(BR_ACTOR_MODEL, NULL);
    if (model_actor == NULL) { BrPixelmapFree(pm); BrEnd(); return 7; }
    model_actor->model = model;
    BrMatrix34RotateY(&mm, BR_ANGLE_DEG(30));
    BrMatrix34PreRotateX(&mm, BR_ANGLE_DEG(20));
    {
        int r, c;
        float lin[3][3], t0, t1, t2;
        for (r = 0; r < 3; r++)
            for (c = 0; c < 3; c++)
                lin[r][c] = BrScalarToFloat(mm.m[r][c]) * s;
        t0 = -(cx * lin[0][0] + cy * lin[1][0] + cz * lin[2][0]);
        t1 = -(cx * lin[0][1] + cy * lin[1][1] + cz * lin[2][1]);
        t2 = -(cx * lin[0][2] + cy * lin[1][2] + cz * lin[2][2]);
        for (r = 0; r < 3; r++)
            for (c = 0; c < 3; c++)
                mm.m[r][c] = BrFloatToScalar(lin[r][c]);
        mm.m[3][0] = BrFloatToScalar(t0);
        mm.m[3][1] = BrFloatToScalar(t1);
        mm.m[3][2] = BrFloatToScalar(t2);
    }
    model_actor->t.type = BR_TRANSFORM_MATRIX34;
    model_actor->t.t.mat = mm;
    BrActorAdd(world, model_actor);

    sx = (int *)malloc(sizeof(int) * nv);
    sy = (int *)malloc(sizeof(int) * nv);
    sw = (float *)malloc(sizeof(float) * nv);
    wx = (float *)malloc(sizeof(float) * nv);
    wy = (float *)malloc(sizeof(float) * nv);
    wz = (float *)malloc(sizeof(float) * nv);
    if (!sx || !sy || !sw || !wx || !wy || !wz) {
        free(sx); free(sy); free(sw); free(wx); free(wy); free(wz);
        BrPixelmapFree(pm); BrEnd(); return 8;
    }

    BrActorToScreenMatrix4(&m2s, model_actor, camera_actor);

    for (i = 0; i < nv; i++) {
        br_vector4 clip; br_vector3 wpos; float w, ndc_x, ndc_y;
        BrMatrix4ApplyP(&clip, &model->vertices[i].p, &m2s);
        w = BrScalarToFloat(clip.v[3]);
        sw[i] = w;
        if (w > 0.0f) {
            ndc_x = BrScalarToFloat(clip.v[0]) / w;
            ndc_y = BrScalarToFloat(clip.v[1]) / w;
            sx[i] = (int)lround((ndc_x * 0.5f + 0.5f) * RENDER_W);
            sy[i] = (int)lround((0.5f - ndc_y * 0.5f) * RENDER_H);
        } else {
            sx[i] = -10000; sy[i] = -10000;
        }
        BrMatrix34ApplyP(&wpos, &model->vertices[i].p, &model_actor->t.t.mat);
        wx[i] = BrScalarToFloat(wpos.v[0]);
        wy[i] = BrScalarToFloat(wpos.v[1]);
        wz[i] = BrScalarToFloat(wpos.v[2]);
    }

    for (i = 0; i < nf; i++) {
        int a = model->faces[i].vertices[0];
        int b = model->faces[i].vertices[1];
        int c = model->faces[i].vertices[2];
        float ux, uy, uz, vx, vy, vz, nx, ny, nz, nl, d, shade;
        int g;
        if (a < 0 || a >= nv || b < 0 || b >= nv || c < 0 || c >= nv) continue;
        if (sw[a] <= 0.0f || sw[b] <= 0.0f || sw[c] <= 0.0f) continue;
        ux = wx[b]-wx[a]; uy = wy[b]-wy[a]; uz = wz[b]-wz[a];
        vx = wx[c]-wx[a]; vy = wy[c]-wy[a]; vz = wz[c]-wz[a];
        nx = uy*vz - uz*vy; ny = uz*vx - ux*vz; nz = ux*vy - uy*vx;
        nl = (float)sqrt(nx*nx + ny*ny + nz*nz);
        if (nl <= 0.0f) continue;
        nx/=nl; ny/=nl; nz/=nl;
        d = nx*lx + ny*ly + nz*lz; if (d < 0.0f) d = -d;
        shade = 0.28f + 0.72f * d; if (shade > 1.0f) shade = 1.0f;
        g = (int)(shade * 235.0f);
        fill_triangle_z(pm, sx[a], sy[a], sw[a], sx[b], sy[b], sw[b], sx[c], sy[c], sw[c],
            BR_COLOUR_RGB(g, g, (int)(g * 0.85f)));
        drawn++;
    }

    free(sx); free(sy); free(sw); free(wx); free(wy); free(wz);

    total_lit = count_lit(pm);
    if (drawn < 1) { BrPixelmapFree(pm); BrEnd(); return 9; }
    if (total_lit < 1000 || total_lit >= (br_uint_32)(RENDER_W * RENDER_H)) {
        BrPixelmapFree(pm); BrEnd(); return 10;
    }
    if (!dump_ppm(pm, out_path)) { BrPixelmapFree(pm); BrEnd(); return 11; }

    printf("brender model smoke: loaded '%s' id='%s' verts=%d faces=%d, drew %ld faces, %lu lit pixels, wrote %s\n",
        model_path, model->identifier ? model->identifier : "?", nv, nf, drawn,
        (unsigned long)total_lit, out_path);

    BrPixelmapFree(pm);
    if (BrEnd() != BRE_OK) return 12;
    return 0;
}
"""
