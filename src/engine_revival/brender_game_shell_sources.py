from __future__ import annotations

from engine_revival.brender_json_receipt import json_receipt_helpers_source
from engine_revival.brender_texture_c_helpers import texture_colour_helpers_source


def game_shell_source() -> str:
    """C source for the BRender portable-core game-shell rung.

    First R5 rung: the smallest honest game loop. An explicit state machine
    (INIT, LOAD, RUN, TEARDOWN) drives a fixed-length, fully deterministic
    frame sequence: every frame renders the loaded, file-textured model from a
    stepped orbit and writes one numbered PPM plus a final JSON manifest.
    No input devices, no timing dependence, no hidden state: everything the
    shell does is reproducible from its arguments. Real display/input drivers
    bind here later; this rung proves the lifecycle and the loop.
    """
    return r"""/*
 * BRender v1.3.2 portable-core game-shell rung.
 *
 * States:
 *   SHELL_INIT     BrBegin, allocate framebuffer
 *   SHELL_LOAD     model + texture (+ palette) from period datafiles
 *   SHELL_RUN      fixed frame count; per-frame orbit render -> PPM
 *   SHELL_TEARDOWN free actors/model/pixelmaps, BrEnd, emit manifest
 *
 * Deterministic by construction: frame count, orbit step, and asset paths
 * come from argv; no clock, no RNG, no user input. A later rung binds real
 * drivers onto this same state machine.
 *
 * Usage: brender_core_game_shell <model.dat> <texture.pix> [palette.pal] [frames] [outdir]
 */
#define __BR_V1DB__ 1
#include "brender.h"

#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#if defined(_DEBUG)
#include <crtdbg.h>
#endif
#include <string.h>
""" + json_receipt_helpers_source() + texture_colour_helpers_source() + r"""

#define RENDER_W 320
#define RENDER_H 240
#define DEFAULT_FRAMES 8
#define MAX_FRAMES 64
#define COLOUR_BLACK BR_COLOUR_RGB(0, 0, 0)

typedef enum shell_state {
    SHELL_INIT = 0,
    SHELL_LOAD,
    SHELL_RUN,
    SHELL_TEARDOWN,
    SHELL_FAILED
} shell_state;

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
    int frames = (argc > 4) ? atoi(argv[4]) : DEFAULT_FRAMES;
    const char *outdir = (argc > 5) ? argv[5] : ".";
    shell_state state = SHELL_INIT;
    br_pixelmap *tex = NULL, *pal = NULL, *pm = NULL;
    br_actor *world = NULL, *camera_actor = NULL, *model_actor = NULL;
    br_camera *camera;
    br_model *model = NULL;
    br_matrix4 m2s;
    long total_sampled = 0;
    int frames_written = 0, i, frame;

    if (model_path == NULL || tex_path == NULL) {
        fprintf(stderr, "usage: %s <model.dat> <texture.pix> [palette.pal] [frames] [outdir]\n", argv[0]);
        return 2;
    }
    if (frames < 1) frames = 1;
    if (frames > MAX_FRAMES) frames = MAX_FRAMES;

    /* SHELL_INIT */
#if defined(_DEBUG)
    _CrtSetReportMode(_CRT_WARN, _CRTDBG_MODE_DEBUG);
    _CrtSetReportMode(_CRT_ERROR, _CRTDBG_MODE_DEBUG);
    _CrtSetReportMode(_CRT_ASSERT, _CRTDBG_MODE_DEBUG);
#endif
    if (BrBegin() != BRE_OK) { state = SHELL_FAILED; goto teardown; }
    pm = BrPixelmapAllocate(BR_PMT_RGB_888, RENDER_W, RENDER_H, NULL, BR_PMAF_NORMAL);
    if (pm == NULL || pm->pixels == NULL) { state = SHELL_FAILED; goto teardown; }
    BrPixelmapFill(pm, COLOUR_BLACK);

    /* SHELL_LOAD */
    tex = BrPixelmapLoad((char *)tex_path);
    if (tex == NULL || tex->pixels == NULL) { state = SHELL_FAILED; goto teardown; }
    if (pal_path != NULL) {
        pal = BrPixelmapLoad((char *)pal_path);
        if (pal == NULL || pal->pixels == NULL) { state = SHELL_FAILED; goto teardown; }
        tex->map = pal;
    }
    model = BrModelLoad((char *)model_path);
    if (model == NULL || model->nvertices < 3 || model->nfaces < 1
        || model->vertices == NULL || model->faces == NULL) {
        state = SHELL_FAILED; goto teardown;
    }

    world = BrActorAllocate(BR_ACTOR_NONE, NULL);
    camera_actor = BrActorAllocate(BR_ACTOR_CAMERA, NULL);
    if (world == NULL || camera_actor == NULL || camera_actor->type_data == NULL) {
        state = SHELL_FAILED; goto teardown;
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
    if (model_actor == NULL) { state = SHELL_FAILED; goto teardown; }
    model_actor->model = model;
    BrActorAdd(world, model_actor);

    /* SHELL_RUN: deterministic orbit, one PPM per frame. */
    state = SHELL_RUN;
    for (frame = 0; frame < frames; frame++) {
        int *sx, *sy; float *siw, *sw;
        br_matrix34 mm;
        int angle = 35 + frame * (360 / frames);
        char path[512];
        long sampled = 0;
        int nv = (int)model->nvertices, nf = (int)model->nfaces;

        for (i = 0; i < RENDER_H * RENDER_W; i++) g_zbuf[i] = 0.0f;
        BrPixelmapFill(pm, COLOUR_BLACK);

        BrMatrix34RotateY(&mm, BR_ANGLE_DEG(angle));
        BrMatrix34PreRotateX(&mm, BR_ANGLE_DEG(25));
        model_actor->t.type = BR_TRANSFORM_MATRIX34;
        model_actor->t.t.mat = mm;

        BrActorToScreenMatrix4(&m2s, model_actor, camera_actor);

        sx = (int *)malloc(sizeof(int) * nv);
        sy = (int *)malloc(sizeof(int) * nv);
        siw = (float *)malloc(sizeof(float) * nv);
        sw = (float *)malloc(sizeof(float) * nv);
        if (!sx || !sy || !siw || !sw) {
            free(sx); free(sy); free(siw); free(sw);
            state = SHELL_FAILED; goto teardown;
        }
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
        }
        free(sx); free(sy); free(siw); free(sw);

        {
            size_t ol = strlen(outdir);
            const char *sep = (ol > 0 && (outdir[ol-1] == '/' || outdir[ol-1] == '\\')) ? "" : "/";
            if (snprintf(path, sizeof(path), "%s%sshell-frame-%02d.ppm", outdir, sep, frame) >= (int)sizeof(path)) {
                state = SHELL_FAILED; goto teardown;
            }
        }
        if (!dump_ppm(pm, path)) {
            fprintf(stderr, "game shell: frame dump failed: %s\n", path);
            state = SHELL_FAILED; goto teardown;
        }
        frames_written++;
        total_sampled += sampled;
    }

teardown:
    /* SHELL_TEARDOWN */
    if (state == SHELL_FAILED && pm == NULL && tex == NULL && model == NULL) {
        fprintf(stderr, "game shell failed before asset load\n");
    }
    if (model_actor != NULL) BrActorRemove(model_actor);
    if (camera_actor != NULL) BrActorRemove(camera_actor);
    if (world != NULL) BrActorFree(world);
    if (model != NULL) BrModelFree(model);
    if (tex != NULL && pal != NULL) tex->map = NULL;
    if (pal != NULL) BrPixelmapFree(pal);
    if (tex != NULL) BrPixelmapFree(tex);
    if (pm != NULL) BrPixelmapFree(pm);
    if (BrEnd() != BRE_OK) return 20;

    printf("{\"shell\":\"brender-core-game-shell\",\"state\":\"%s\",",
        (state == SHELL_FAILED) ? "FAILED" : "TEARDOWN");
    fputs("\"model\":", stdout);
    json_write_string(stdout, model_path);
    fputs(",\"texture\":", stdout);
    json_write_string(stdout, tex_path);
    fputs(",\"palette\":", stdout);
    json_write_string(stdout, pal_path ? pal_path : "-");
    printf(","
        "\"frames_requested\":%d,\"frames_written\":%d,"
        "\"pixels_sampled\":%ld,\"valid\":%s}\n",
        frames, frames_written, total_sampled,
        (state != SHELL_FAILED && frames_written == frames) ? "true" : "false");

    return (state != SHELL_FAILED && frames_written == frames) ? 0 : 21;
}
"""
