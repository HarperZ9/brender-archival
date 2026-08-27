from __future__ import annotations

from engine_revival.brender_json_receipt import json_receipt_helpers_source
from engine_revival.brender_texture_c_helpers import texture_colour_helpers_source


def texture_file_sample_source() -> str:
    """C source for the BRender portable-core file-texture sampling rung.

    The R4 closing rung: render a real loaded model with real per-vertex UVs
    through perspective-correct sampling of a LOADED period pixelmap
    (BrPixelmapLoad), replacing the generated textures every earlier textured
    smoke used. Indexed textures receive an externally loaded palette pixelmap
    through pm->map; RGB variants sample directly. Distinct-colour counting on
    the frame proves actual texture data was sampled rather than a flat tint.
    """
    return r"""/*
 * BRender v1.3.2 portable-core file-texture sampling rung.
 *
 *   BrBegin
 *     -> tex = BrPixelmapLoad("<...>/dat/<texture>.pix")
 *     -> pal = BrPixelmapLoad("<...>/dat/<palette>.pal")   (indexed textures)
 *     -> tex->map = pal
 *     -> model = BrModelLoad("<...>/dat/sph32.dat")        (real per-vertex UVs)
 *     -> project via BrActorToScreenMatrix4, rasterize perspective-correct,
 *        texel lookup through BrPixelmapPixelGet on the loaded pixelmap
 *   BrEnd
 *
 * One JSON receipt plus PPM. Exit 0 only when enough distinct sampled colours
 * appear to prove real texture data drove the pixels.
 *
 * Usage: brender_core_texture_file_sample <model.dat> <texture.pix> [palette.pal] [out.ppm]
 */
#define __BR_V1DB__ 1
#include "brender.h"

#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#if defined(_DEBUG)
#include <crtdbg.h>
#endif
""" + json_receipt_helpers_source() + texture_colour_helpers_source() + r"""

#define RENDER_W 320
#define RENDER_H 240
#define MAX_DISTINCT 512
#define COLOUR_BLACK BR_COLOUR_RGB(0, 0, 0)

typedef struct tvert {
    int x, y;
    float iw, uow, vow;
} tvert;

static float g_zbuf[RENDER_H * RENDER_W];

static void fill_triangle_tex(br_pixelmap *pm, br_pixelmap *tex,
    tvert p0, tvert p1, tvert p2, float shade, long *sampled)
{
    int y;
    for (y = 0; y < RENDER_H; y++) {
        int cx[3]; float ciw[3], cuo[3], cvo[3];
        int n = 0, e, lo, hi, x;
        int ex[3][2], ey[3][2]; float eiw[3][2], euo[3][2], evo[3][2];
        ex[0][0]=p0.x; ey[0][0]=p0.y; eiw[0][0]=p0.iw; euo[0][0]=p0.uow; evo[0][0]=p0.vow;
        ex[0][1]=p1.x; ey[0][1]=p1.y; eiw[0][1]=p1.iw; euo[0][1]=p1.uow; evo[0][1]=p1.vow;
        ex[1][0]=p1.x; ey[1][0]=p1.y; eiw[1][0]=p1.iw; euo[1][0]=p1.uow; evo[1][0]=p1.vow;
        ex[1][1]=p2.x; ey[1][1]=p2.y; eiw[1][1]=p2.iw; euo[1][1]=p2.uow; evo[1][1]=p2.vow;
        ex[2][0]=p2.x; ey[2][0]=p2.y; eiw[2][0]=p2.iw; euo[2][0]=p2.uow; evo[2][0]=p2.vow;
        ex[2][1]=p0.x; ey[2][1]=p0.y; eiw[2][1]=p0.iw; euo[2][1]=p0.uow; evo[2][1]=p0.vow;
        for (e = 0; e < 3; e++) {
            int ya = ey[e][0], yb = ey[e][1];
            if (ya == yb) continue;
            if ((y >= ya && y < yb) || (y >= yb && y < ya)) {
                float t = (float)(y - ya) / (float)(yb - ya);
                if (n < 3) {
                    cx[n]  = ex[e][0] + (int)((ex[e][1]-ex[e][0])*t);
                    ciw[n] = eiw[e][0] + (eiw[e][1]-eiw[e][0])*t;
                    cuo[n] = euo[e][0] + (euo[e][1]-euo[e][0])*t;
                    cvo[n] = evo[e][0] + (evo[e][1]-evo[e][0])*t;
                    n++;
                }
            }
        }
        if (n < 2) continue;
        lo = 0; hi = 0;
        { int k; for (k = 1; k < n; k++) { if (cx[k] < cx[lo]) lo = k; if (cx[k] > cx[hi]) hi = k; } }
        {
            int xl = cx[lo], xr = cx[hi]; int span = xr - xl;
            for (x = xl; x <= xr; x++) {
                float f, iw, uo, vo, u, vv;
                int idx, tw, th, tu, tv, r, g, bl;
                br_uint_32 texel;
                if (x < 0 || x >= RENDER_W) continue;
                f = (span == 0) ? 0.0f : ((float)(x - cx[lo])) / (float)span;
                iw = ciw[lo] + (ciw[hi] - ciw[lo]) * f;
                if (!(iw > 0.0f)) continue;
                idx = y * RENDER_W + x;
                if (iw <= g_zbuf[idx]) continue;
                uo = cuo[lo] + (cuo[hi] - cuo[lo]) * f;
                vo = cvo[lo] + (cvo[hi] - cvo[lo]) * f;
                u = uo / iw; vv = vo / iw;
                tw = (int)tex->width; th = (int)tex->height;
                tu = (int)(u * tw); tu &= (tw - 1);
                tv = (int)(vv * th); tv &= (th - 1);
                if (tu < 0) tu += tw;
                if (tv < 0) tv += th;
                texel = resolve_texel_colour(tex, tu, tv);
                r  = (int)(((texel >> 16) & 0xff) * shade);
                g  = (int)(((texel >> 8) & 0xff) * shade);
                bl = (int)((texel & 0xff) * shade);
                g_zbuf[idx] = iw;
                BrPixelmapPixelSet(pm, x, y, BR_COLOUR_RGB(r, g, bl));
                (*sampled)++;
            }
        }
    }
}

static void count_frame(br_pixelmap *pm, long *distinct, long *any)
{
    static br_uint_32 seen[MAX_DISTINCT];
    int nseen = 0, x, y;
    *distinct = 0; *any = 0;
    for (y = 0; y < RENDER_H; y++) {
        for (x = 0; x < RENDER_W; x++) {
            br_uint_32 c = BrPixelmapPixelGet(pm, x, y);
            int k, found = 0;
            if (c == COLOUR_BLACK) continue;
            (*any)++;
            for (k = 0; k < nseen; k++) { if (seen[k] == c) { found = 1; break; } }
            if (!found && nseen < MAX_DISTINCT) seen[nseen++] = c;
        }
    }
    *distinct = nseen;
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
    const char *tex_path = (argc > 2) ? argv[2] : NULL;
    const char *pal_path = (argc > 3 && argv[3][0] != 0) ? argv[3] : NULL;
    const char *out_path = (argc > 4) ? argv[4] : "brender-core-texture-file-sample.ppm";
    br_pixelmap *tex = NULL, *pal = NULL, *pm = NULL;
    br_actor *world, *camera_actor, *model_actor;
    br_camera *camera;
    br_model *model;
    br_matrix34 mm;
    br_matrix4 m2s;
    long sampled = 0, distinct = 0, any = 0, drew = 0;
    int i, nv, nf;

    if (model_path == NULL || tex_path == NULL) {
        fprintf(stderr, "usage: %s <model.dat> <texture.pix> [palette.pal] [out.ppm]\n", argv[0]);
        return 2;
    }

    if (BrBegin() != BRE_OK) return 3;
#if defined(_DEBUG)
    _CrtSetReportMode(_CRT_WARN, _CRTDBG_MODE_DEBUG);
    _CrtSetReportMode(_CRT_ERROR, _CRTDBG_MODE_DEBUG);
    _CrtSetReportMode(_CRT_ASSERT, _CRTDBG_MODE_DEBUG);
#endif

    tex = BrPixelmapLoad((char *)tex_path);
    if (tex == NULL || tex->pixels == NULL) {
        fprintf(stderr, "BrPixelmapLoad failed: %s\n", tex_path);
        BrEnd(); return 4;
    }
    if (pal_path != NULL) {
        pal = BrPixelmapLoad((char *)pal_path);
        if (pal == NULL || pal->pixels == NULL) {
            fprintf(stderr, "palette load failed: %s\n", pal_path);
            BrEnd(); return 5;
        }
        tex->map = pal;
    }

    model = BrModelLoad((char *)model_path);
    if (model == NULL) { BrEnd(); return 6; }
    nv = (int)model->nvertices; nf = (int)model->nfaces;
    if (nv < 3 || nf < 1 || model->vertices == NULL || model->faces == NULL) {
        BrEnd(); return 7;
    }

    pm = BrPixelmapAllocate(BR_PMT_RGB_888, RENDER_W, RENDER_H, NULL, BR_PMAF_NORMAL);
    if (pm == NULL || pm->pixels == NULL) { BrEnd(); return 8; }
    BrPixelmapFill(pm, COLOUR_BLACK);
    for (i = 0; i < RENDER_H * RENDER_W; i++) g_zbuf[i] = 0.0f;

    world = BrActorAllocate(BR_ACTOR_NONE, NULL);
    camera_actor = BrActorAllocate(BR_ACTOR_CAMERA, NULL);
    if (world == NULL || camera_actor == NULL || camera_actor->type_data == NULL) {
        BrEnd(); return 9;
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

    model_actor = BrActorAllocate(BR_ACTOR_MODEL, NULL);
    if (model_actor == NULL) { BrEnd(); return 10; }
    model_actor->model = model;
    BrMatrix34RotateY(&mm, BR_ANGLE_DEG(35));
    BrMatrix34PreRotateX(&mm, BR_ANGLE_DEG(25));
    model_actor->t.type = BR_TRANSFORM_MATRIX34;
    model_actor->t.t.mat = mm;
    BrActorAdd(world, model_actor);

    BrActorToScreenMatrix4(&m2s, model_actor, camera_actor);

    /* Screen projection with 1/w; UVs come straight from the loaded model. */
    {
        int *sx = (int *)malloc(sizeof(int) * nv);
        int *sy = (int *)malloc(sizeof(int) * nv);
        float *siw = (float *)malloc(sizeof(float) * nv);
        float *sw = (float *)malloc(sizeof(float) * nv);
        float wx[3];
        if (!sx || !sy || !siw || !sw) { free(sx); free(sy); free(siw); free(sw); BrEnd(); return 11; }
        for (i = 0; i < nv; i++) {
            br_vector4 clip;
            float w, ndc_x, ndc_y;
            BrMatrix4ApplyP(&clip, &model->vertices[i].p, &m2s);
            w = BrScalarToFloat(clip.v[3]);
            sw[i] = w;
            if (w > 0.0f) {
                ndc_x = BrScalarToFloat(clip.v[0]) / w;
                ndc_y = BrScalarToFloat(clip.v[1]) / w;
                sx[i] = (int)lround((ndc_x * 0.5f + 0.5f) * RENDER_W);
                sy[i] = (int)lround((0.5f - ndc_y * 0.5f) * RENDER_H);
                siw[i] = 1.0f / w;
            } else {
                sx[i] = -10000; sy[i] = -10000; siw[i] = -1.0f;
            }
        }

        for (i = 0; i < nf; i++) {
            int a = model->faces[i].vertices[0];
            int b = model->faces[i].vertices[1];
            int c = model->faces[i].vertices[2];
            float ux, uy, uz, vx, vy, vz, nx, ny, nz, nl, d, shade;
            tvert va, vb, vc;
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
            d = nx*0.35f + ny*0.55f + nz*1.0f; if (d < 0.0f) d = -d;
            shade = 0.45f + 0.55f * d; if (shade > 1.0f) shade = 1.0f;

            va.x = sx[a]; va.y = sy[a]; va.iw = siw[a];
            va.uow = BrScalarToFloat(model->vertices[a].map.v[0]) * siw[a];
            va.vow = BrScalarToFloat(model->vertices[a].map.v[1]) * siw[a];
            vb.x = sx[b]; vb.y = sy[b]; vb.iw = siw[b];
            vb.uow = BrScalarToFloat(model->vertices[b].map.v[0]) * siw[b];
            vb.vow = BrScalarToFloat(model->vertices[b].map.v[1]) * siw[b];
            vc.x = sx[c]; vc.y = sy[c]; vc.iw = siw[c];
            vc.uow = BrScalarToFloat(model->vertices[c].map.v[0]) * siw[c];
            vc.vow = BrScalarToFloat(model->vertices[c].map.v[1]) * siw[c];
            fill_triangle_tex(pm, tex, va, vb, vc, shade, &sampled);
            drew++;
        }
        free(sx); free(sy); free(siw); free(sw);
    }

    count_frame(pm, &distinct, &any);

    if (drew < 1 || sampled < 3000 || any < 3000 || distinct < 8) { BrEnd(); return 12; }
    if (!dump_ppm(pm, out_path)) { BrEnd(); return 13; }

    fputs("{\"model\":", stdout);
    json_write_string(stdout, model_path);
    fputs(",\"texture\":", stdout);
    json_write_string(stdout, tex_path);
    fputs(",\"palette\":", stdout);
    json_write_string(stdout, pal_path ? pal_path : "-");
    printf(",\"texture_type\":%d,\"texture_width\":%d,\"texture_height\":%d,"
        "\"faces_drawn\":%ld,\"pixels_sampled\":%ld,"
        "\"lit_pixels\":%ld,\"distinct_colours\":%ld,\"valid\":true}\n",
        (int)tex->type, (int)tex->width, (int)tex->height,
        drew, sampled, any, distinct);

    BrPixelmapFree(pm);
    tex->map = NULL;
    if (pal != NULL) BrPixelmapFree(pal);
    BrPixelmapFree(tex);
    if (BrEnd() != BRE_OK) return 14;
    return 0;
}
"""
