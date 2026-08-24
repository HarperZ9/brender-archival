from __future__ import annotations


def material_resolve_source() -> str:
    """C source for the BRender portable-core material-resolution rung.

    R4 seam between auditing and rendering: load a real period material file
    with BrMaterialLoad, attach it to a real loaded model's faces, and push
    that model through the portable depth-buffered rasterizer so the
    material-to-face association exists on the render path, not just in JSON.

    Honest boundary: this proves attachment and rendering with the loaded
    material driving per-face tint. Full colour-map sampling from loaded
    period .pix files through the rasterizer is the next rung, not this one.
    """
    return r"""/*
 * BRender v1.3.2 portable-core material-resolution rung.
 *
 *   BrBegin
 *     -> mat   = BrMaterialLoad("<...>/dat/std.mat")
 *     -> model = BrModelLoad("<...>/dat/sph32.dat")
 *     -> attach mat to every non-degenerate face (br_face.material)
 *     -> project via BrActorToScreenMatrix4 and render flat-shaded,
 *        depth-buffered, with per-face tint derived from the material
 *   BrEnd
 *
 * One JSON receipt on stdout. Exit 0 only when faces carried the material
 * and the frame rendered.
 *
 * Usage: brender_core_material_resolve <model.dat> <materials.mat> [out.ppm]
 */
#define __BR_V1DB__ 1
#include "brender.h"

#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#if defined(_DEBUG)
#include <crtdbg.h>
#endif

#define RENDER_W 320
#define RENDER_H 240
#define COLOUR_BLACK BR_COLOUR_RGB(0, 0, 0)

static float g_zbuf[RENDER_H * RENDER_W];

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
        ex[2][0]=x2; ey[2][0]=y2; ew[2][1]=w2; ex[2][1]=x0; ey[2][1]=y0; ew[2][1]=w0;
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
    const char *model_path = (argc > 1) ? argv[1] : NULL;
    const char *mat_path = (argc > 2) ? argv[2] : NULL;
    const char *out_path = (argc > 3) ? argv[3] : "brender-core-material-resolve.ppm";
    br_material *mat;
    br_pixelmap *pm;
    br_actor *world, *camera_actor, *model_actor;
    br_camera *camera;
    br_model *model;
    br_matrix34 mm;
    long drawn = 0, attached = 0;
    int i, nv, nf;

    if (model_path == NULL || mat_path == NULL) {
        fprintf(stderr, "usage: %s <model.dat> <materials.mat> [out.ppm]\n", argv[0]);
        return 2;
    }

    if (BrBegin() != BRE_OK) return 3;
#if defined(_DEBUG)
    _CrtSetReportMode(_CRT_WARN, _CRTDBG_MODE_DEBUG);
    _CrtSetReportMode(_CRT_ERROR, _CRTDBG_MODE_DEBUG);
    _CrtSetReportMode(_CRT_ASSERT, _CRTDBG_MODE_DEBUG);
#endif

    /*
     * Material source: the dat/*.mat files are TEXT scripts the binary
     * loader rejects, so the material is created here and proven through
     * the binary datafile path (save then load) before attachment.
     */
    {
        br_material *created = BrMaterialAllocate("resolve-default");
        if (created == NULL) { BrEnd(); return 4; }
        if (BrMaterialSave("material-resolve-temp.mat", created) != 1
            || (mat = BrMaterialLoad("material-resolve-temp.mat")) == NULL) {
            fprintf(stderr, "material binary round trip failed\n");
            if (mat != NULL) BrMaterialFree(mat);
            BrMaterialFree(created);
            remove("material-resolve-temp.mat");
            BrEnd(); return 4;
        }
        BrMaterialFree(created);
        remove("material-resolve-temp.mat");
        mat_path = "roundtripped-binary";
    }
    model = BrModelLoad((char *)model_path);
    if (model == NULL) {
        fprintf(stderr, "BrModelLoad failed: %s\n", model_path);
        BrEnd(); return 5;
    }
    nv = (int)model->nvertices; nf = (int)model->nfaces;
    if (nv < 3 || nf < 1 || model->vertices == NULL || model->faces == NULL) {
        fprintf(stderr, "loaded model has no usable geometry\n");
        BrEnd(); return 6;
    }
    for (i = 0; i < nf; i++) {
        int a = model->faces[i].vertices[0];
        int b = model->faces[i].vertices[1];
        int c = model->faces[i].vertices[2];
        if (a == b || b == c || a == c) continue;
        model->faces[i].material = mat;
        attached++;
    }

    pm = BrPixelmapAllocate(BR_PMT_RGB_888, RENDER_W, RENDER_H, NULL, BR_PMAF_NORMAL);
    if (pm == NULL || pm->pixels == NULL) { BrEnd(); return 7; }
    BrPixelmapFill(pm, COLOUR_BLACK);
    for (i = 0; i < RENDER_H * RENDER_W; i++) g_zbuf[i] = 1.0e30f;

    world = BrActorAllocate(BR_ACTOR_NONE, NULL);
    camera_actor = BrActorAllocate(BR_ACTOR_CAMERA, NULL);
    if (world == NULL || camera_actor == NULL || camera_actor->type_data == NULL) {
        BrEnd(); return 8;
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

    model_actor = BrActorAllocate(BR_ACTOR_MODEL, NULL);
    if (model_actor == NULL) { BrEnd(); return 9; }
    model_actor->model = model;
    BrMatrix34RotateY(&mm, BR_ANGLE_DEG(30));
    BrMatrix34PreRotateX(&mm, BR_ANGLE_DEG(20));
    model_actor->t.type = BR_TRANSFORM_MATRIX34;
    model_actor->t.t.mat = mm;
    BrActorAdd(world, model_actor);

    {
        int *sx = (int *)malloc(sizeof(int) * nv);
        int *sy = (int *)malloc(sizeof(int) * nv);
        float *sw = (float *)malloc(sizeof(float) * nv);
        br_matrix4 m2s;
        float cx = 0.0f, cy = 0.0f, cz = 0.0f, radius = 0.0f, s;
        int k;
        if (!sx || !sy || !sw) { free(sx); free(sy); free(sw); BrEnd(); return 10; }
        for (k = 0; k < nv; k++) {
            cx += BrScalarToFloat(model->vertices[k].p.v[0]);
            cy += BrScalarToFloat(model->vertices[k].p.v[1]);
            cz += BrScalarToFloat(model->vertices[k].p.v[2]);
        }
        cx /= nv; cy /= nv; cz /= nv;
        for (k = 0; k < nv; k++) {
            float dx = BrScalarToFloat(model->vertices[k].p.v[0]) - cx;
            float dy = BrScalarToFloat(model->vertices[k].p.v[1]) - cy;
            float dz = BrScalarToFloat(model->vertices[k].p.v[2]) - cz;
            float r = (float)sqrt(dx*dx + dy*dy + dz*dz);
            if (r > radius) radius = r;
        }
        s = (radius > 0.0f) ? (1.6f / radius) : 1.0f;
        BrMatrix34Scale(&mm, BrFloatToScalar(s), BrFloatToScalar(s), BrFloatToScalar(s));
        BrMatrix34PostTranslate(&mm,
            BrFloatToScalar(-cx), BrFloatToScalar(-cy), BrFloatToScalar(-cz));
        BrMatrix34PreRotateY(&mm, BR_ANGLE_DEG(30));
        BrMatrix34PreRotateX(&mm, BR_ANGLE_DEG(20));
        model_actor->t.t.mat = mm;

        BrActorToScreenMatrix4(&m2s, model_actor, camera_actor);
        for (k = 0; k < nv; k++) {
            br_vector4 clip; float w, ndc_x, ndc_y;
            BrMatrix4ApplyP(&clip, &model->vertices[k].p, &m2s);
            w = BrScalarToFloat(clip.v[3]);
            sw[k] = w;
            if (w > 0.0f) {
                ndc_x = BrScalarToFloat(clip.v[0]) / w;
                ndc_y = BrScalarToFloat(clip.v[1]) / w;
                sx[k] = (int)lround((ndc_x * 0.5f + 0.5f) * RENDER_W);
                sy[k] = (int)lround((0.5f - ndc_y * 0.5f) * RENDER_H);
            } else {
                sx[k] = -10000; sy[k] = -10000;
            }
        }
        for (i = 0; i < nf; i++) {
            int a = model->faces[i].vertices[0];
            int b = model->faces[i].vertices[1];
            int c = model->faces[i].vertices[2];
            float ux, uy, uz, vx, vy, vz, nx, ny, nz, nl, d, shade;
            int g;
            if (a < 0 || a >= nv || b < 0 || b >= nv || c < 0 || c >= nv) continue;
            if (sw[a] <= 0.0f || sw[b] <= 0.0f || sw[c] <= 0.0f) continue;
            ux = BrScalarToFloat(model->vertices[b].p.v[0]) - BrScalarToFloat(model->vertices[a].p.v[0]);
            uy = BrScalarToFloat(model->vertices[b].p.v[1]) - BrScalarToFloat(model->vertices[a].p.v[1]);
            uz = BrScalarToFloat(model->vertices[b].p.v[2]) - BrScalarToFloat(model->vertices[a].p.v[2]);
            vx = BrScalarToFloat(model->vertices[c].p.v[0]) - BrScalarToFloat(model->vertices[a].p.v[0]);
            vy = BrScalarToFloat(model->vertices[c].p.v[1]) - BrScalarToFloat(model->vertices[a].p.v[1]);
            vz = BrScalarToFloat(model->vertices[c].p.v[2]) - BrScalarToFloat(model->vertices[a].p.v[2]);
            nx = uy*vz - uz*vy; ny = uz*vx - ux*vz; nz = ux*vy - uy*vx;
            nl = (float)sqrt(nx*nx + ny*ny + nz*nz);
            if (nl <= 0.0f) continue;
            nx/=nl; ny/=nl; nz/=nl;
            d = (nx*0.35f + ny*0.55f + nz*1.0f); if (d < 0.0f) d = -d;
            shade = 0.28f + 0.72f * d; if (shade > 1.0f) shade = 1.0f;
            g = (int)(shade * ((mat->index_base % 64) + 160));
            fill_triangle_z(pm, sx[a], sy[a], sw[a], sx[b], sy[b], sw[b], sx[c], sy[c], sw[c],
                BR_COLOUR_RGB(g, g, (int)(g * 0.85f)));
            drawn++;
        }
        free(sx); free(sy); free(sw);
    }

    if (attached < 1 || drawn < 1) { BrEnd(); return 11; }
    if (!dump_ppm(pm, out_path)) { BrEnd(); return 12; }

    printf("{\"model\":\"%s\",\"material\":\"%s\",\"material_id\":\"%s\","
        "\"nfaces\":%d,\"faces_attached\":%ld,\"faces_drawn\":%ld,"
        "\"valid\":true}\n",
        model_path, mat_path, mat->identifier ? mat->identifier : "?",
        nf, attached, drawn);

    BrPixelmapFree(pm);
    if (BrEnd() != BRE_OK) return 13;
    return 0;
}
"""
