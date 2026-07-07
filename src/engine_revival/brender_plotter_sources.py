from __future__ import annotations


def plotter_smoke_source() -> str:
    """C source for the BRender portable-core plotter render smoke.

    The first Telos Engine plotter-lane capability: a real period model is
    loaded from its native datafile, projected through the engine's own
    scene-graph transform, and rendered as a hidden-line-removed wireframe
    emitted as pen-plotter-ready SVG polylines (plus a raster preview). Edges
    shared by near-coplanar faces are dropped (crease filter) so triangulated
    quads plot as clean quads, the classic plotter aesthetic.
    """
    return r"""/*
 * BRender v1.3.2 portable-core plotter render smoke.
 *
 * Turns the revived engine into a pen-plotter art pipeline, pure C, no
 * assembly renderer:
 *
 *   BrBegin
 *     -> model = BrModelLoad("<...>/dat/teapot.dat")
 *     -> BrActorToScreenMatrix4 projection (engine scene graph)
 *     -> depth-only rasterization of every face into a z-buffer
 *     -> unique model edges, crease-filtered (near-coplanar shared edges drop)
 *     -> each edge sampled against the z-buffer; visible runs survive
 *     -> SVG polyline output (plotter artifact) + PPM preview (same segments)
 *   BrEnd
 *
 * Self-verifying: edge counts, active occlusion (hidden samples exist), a
 * visible fraction strictly between extremes, and a well-formed SVG artifact.
 *
 * Usage: brender_core_plotter_smoke <model.dat> [output.svg] [preview.ppm]
 */
#define __BR_V1DB__ 1
#include "brender.h"

#include <math.h>
#include <stdio.h>
#include <stdlib.h>

#define RENDER_W 640
#define RENDER_H 480
#define MAX_RUNS_PER_EDGE 32

#define COLOUR_PAPER BR_COLOUR_RGB(245, 244, 240)
#define COLOUR_INK   BR_COLOUR_RGB(20, 22, 28)

static float g_zbuf[RENDER_H * RENDER_W];

/* Depth-only triangle rasterization (nearer w wins). */
static void raster_depth(int x0, int y0, float w0, int x1, int y1, float w1,
    int x2, int y2, float w2)
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
                if (w < g_zbuf[idx]) g_zbuf[idx] = w;
            }
        }
    }
}

typedef struct { long key; int a, b; float nx[2], ny[2], nz[2]; int nfaces; } pedge;

static int edge_cmp(const void *pa, const void *pb)
{
    long ka = ((const pedge *)pa)->key, kb = ((const pedge *)pb)->key;
    return (ka > kb) - (ka < kb);
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
    const char *model_path = (argc > 1) ? argv[1] : "teapot.dat";
    const char *svg_path = (argc > 2) ? argv[2] : "brender-core-plotter-smoke.svg";
    const char *ppm_path = (argc > 3) ? argv[3] : "brender-core-plotter-smoke.ppm";
    br_pixelmap *pm;
    br_actor *world, *camera_actor, *model_actor;
    br_camera *camera;
    br_model *model;
    br_matrix4 m2s;
    br_matrix34 mm;
    float *sxf = NULL, *syf = NULL, *sw = NULL;
    pedge *edges = NULL;
    FILE *svg;
    float cx, cy, cz, radius, s;
    long nedges = 0, nunique = 0, nkept = 0;
    long visible_segments = 0, hidden_samples = 0, visible_samples = 0;
    int i, nv, nf;

    if (BrBegin() != BRE_OK) return 1;
    model = BrModelLoad((char *)model_path);
    if (model == NULL || model->nvertices < 3 || model->vertices == NULL || model->faces == NULL) {
        fprintf(stderr, "model load failed: %s\n", model_path); BrEnd(); return 2;
    }
    nv = (int)model->nvertices; nf = (int)model->nfaces;

    pm = BrPixelmapAllocate(BR_PMT_RGB_888, RENDER_W, RENDER_H, NULL, BR_PMAF_NORMAL);
    if (pm == NULL || pm->pixels == NULL) { BrEnd(); return 3; }
    BrPixelmapFill(pm, COLOUR_PAPER);
    for (i = 0; i < RENDER_H * RENDER_W; i++) g_zbuf[i] = 1.0e30f;

    /* Auto-frame from vertex bounds (established pattern). */
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
    if (radius <= 0.0f) { BrPixelmapFree(pm); BrEnd(); return 4; }
    s = 1.55f / radius;

    world = BrActorAllocate(BR_ACTOR_NONE, NULL);
    camera_actor = BrActorAllocate(BR_ACTOR_CAMERA, NULL);
    if (world == NULL || camera_actor == NULL || camera_actor->type_data == NULL) {
        BrPixelmapFree(pm); BrEnd(); return 5;
    }
    camera = (br_camera *)camera_actor->type_data;
    camera->type = BR_CAMERA_PERSPECTIVE;
    camera->field_of_view = BR_ANGLE_DEG(50);
    camera->hither_z = BrFloatToScalar(0.5f);
    camera->yon_z = BrFloatToScalar(500.0f);
    camera->aspect = BrFloatToScalar((float)RENDER_W / (float)RENDER_H);
    BrMatrix34Translate(&camera_actor->t.t.mat,
        BrFloatToScalar(0.0f), BrFloatToScalar(0.0f), BrFloatToScalar(5.2f));
    BrActorAdd(world, camera_actor);

    model_actor = BrActorAllocate(BR_ACTOR_MODEL, NULL);
    if (model_actor == NULL) { BrPixelmapFree(pm); BrEnd(); return 6; }
    model_actor->model = model;
    BrMatrix34RotateY(&mm, BR_ANGLE_DEG(28));
    BrMatrix34PreRotateX(&mm, BR_ANGLE_DEG(18));
    {
        int r, c; float lin[3][3], t0, t1, t2;
        for (r = 0; r < 3; r++) for (c = 0; c < 3; c++) lin[r][c] = BrScalarToFloat(mm.m[r][c]) * s;
        t0 = -(cx*lin[0][0] + cy*lin[1][0] + cz*lin[2][0]);
        t1 = -(cx*lin[0][1] + cy*lin[1][1] + cz*lin[2][1]);
        t2 = -(cx*lin[0][2] + cy*lin[1][2] + cz*lin[2][2]);
        for (r = 0; r < 3; r++) for (c = 0; c < 3; c++) mm.m[r][c] = BrFloatToScalar(lin[r][c]);
        mm.m[3][0] = BrFloatToScalar(t0); mm.m[3][1] = BrFloatToScalar(t1); mm.m[3][2] = BrFloatToScalar(t2);
    }
    model_actor->t.type = BR_TRANSFORM_MATRIX34;
    model_actor->t.t.mat = mm;
    BrActorAdd(world, model_actor);

    sxf = malloc(sizeof(float)*nv); syf = malloc(sizeof(float)*nv); sw = malloc(sizeof(float)*nv);
    edges = malloc(sizeof(pedge) * (size_t)nf * 3);
    if (!sxf || !syf || !sw || !edges) {
        free(sxf);free(syf);free(sw);free(edges);
        BrPixelmapFree(pm); BrEnd(); return 7;
    }

    BrActorToScreenMatrix4(&m2s, model_actor, camera_actor);

    for (i = 0; i < nv; i++) {
        br_vector4 clip; float w;
        BrMatrix4ApplyP(&clip, &model->vertices[i].p, &m2s);
        w = BrScalarToFloat(clip.v[3]); sw[i] = w;
        if (w > 0.0f) {
            sxf[i] = (BrScalarToFloat(clip.v[0]) / w * 0.5f + 0.5f) * RENDER_W;
            syf[i] = (0.5f - BrScalarToFloat(clip.v[1]) / w * 0.5f) * RENDER_H;
        } else { sxf[i] = -1.0e6f; syf[i] = -1.0e6f; }
    }

    /* Depth pass + edge collection with per-face model-space normals. */
    for (i = 0; i < nf; i++) {
        int a = model->faces[i].vertices[0], b = model->faces[i].vertices[1], c = model->faces[i].vertices[2];
        float ax, ay, az, bx, by, bz, ccx, ccy, ccz, ux, uy, uz, vx, vy, vz, nx, ny, nz, nl;
        int pair[3][2], e;
        if (a<0||a>=nv||b<0||b>=nv||c<0||c>=nv) continue;
        if (sw[a] <= 0.0f || sw[b] <= 0.0f || sw[c] <= 0.0f) continue;
        raster_depth((int)sxf[a], (int)syf[a], sw[a], (int)sxf[b], (int)syf[b], sw[b],
            (int)sxf[c], (int)syf[c], sw[c]);
        ax=BrScalarToFloat(model->vertices[a].p.v[0]); ay=BrScalarToFloat(model->vertices[a].p.v[1]); az=BrScalarToFloat(model->vertices[a].p.v[2]);
        bx=BrScalarToFloat(model->vertices[b].p.v[0]); by=BrScalarToFloat(model->vertices[b].p.v[1]); bz=BrScalarToFloat(model->vertices[b].p.v[2]);
        ccx=BrScalarToFloat(model->vertices[c].p.v[0]); ccy=BrScalarToFloat(model->vertices[c].p.v[1]); ccz=BrScalarToFloat(model->vertices[c].p.v[2]);
        ux=bx-ax; uy=by-ay; uz=bz-az; vx=ccx-ax; vy=ccy-ay; vz=ccz-az;
        nx=uy*vz-uz*vy; ny=uz*vx-ux*vz; nz=ux*vy-uy*vx;
        nl=(float)sqrt(nx*nx+ny*ny+nz*nz);
        if (nl > 0.0f) { nx/=nl; ny/=nl; nz/=nl; } else { nx=ny=0.0f; nz=1.0f; }
        pair[0][0]=a; pair[0][1]=b; pair[1][0]=b; pair[1][1]=c; pair[2][0]=c; pair[2][1]=a;
        for (e = 0; e < 3; e++) {
            int lo2 = pair[e][0] < pair[e][1] ? pair[e][0] : pair[e][1];
            int hi2 = pair[e][0] < pair[e][1] ? pair[e][1] : pair[e][0];
            edges[nedges].key = (long)lo2 * 65536L + hi2;
            edges[nedges].a = lo2; edges[nedges].b = hi2;
            edges[nedges].nx[0] = nx; edges[nedges].ny[0] = ny; edges[nedges].nz[0] = nz;
            edges[nedges].nfaces = 1;
            nedges++;
        }
    }
    if (nedges < 3) { free(sxf);free(syf);free(sw);free(edges); BrPixelmapFree(pm); BrEnd(); return 8; }

    /* Dedupe edges, folding adjacent-face normals together. */
    qsort(edges, (size_t)nedges, sizeof(pedge), edge_cmp);
    {
        long w2 = 0, r2;
        for (r2 = 0; r2 < nedges; r2++) {
            if (w2 > 0 && edges[w2-1].key == edges[r2].key) {
                if (edges[w2-1].nfaces < 2) {
                    edges[w2-1].nx[1] = edges[r2].nx[0];
                    edges[w2-1].ny[1] = edges[r2].ny[0];
                    edges[w2-1].nz[1] = edges[r2].nz[0];
                    edges[w2-1].nfaces = 2;
                }
            } else {
                edges[w2++] = edges[r2];
            }
        }
        nunique = w2;
    }

    svg = fopen(svg_path, "wb");
    if (svg == NULL) { free(sxf);free(syf);free(sw);free(edges); BrPixelmapFree(pm); BrEnd(); return 9; }
    fprintf(svg, "<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"%d\" height=\"%d\" viewBox=\"0 0 %d %d\">\n",
        RENDER_W, RENDER_H, RENDER_W, RENDER_H);
    fprintf(svg, "<g fill=\"none\" stroke=\"#14161c\" stroke-width=\"1.1\" stroke-linecap=\"round\">\n");

    /* Sample kept edges against the depth buffer; visible runs become lines. */
    for (i = 0; i < (int)nunique; i++) {
        int a = edges[i].a, b = edges[i].b;
        float x0, y0, x1, y1, len;
        int nsamp, k, run_open = 0;
        float run_t0 = 0.0f, run_t1 = 0.0f;
        float runs[MAX_RUNS_PER_EDGE][2];
        int nruns = 0;

        /* Crease filter: drop edges shared by near-coplanar faces. */
        if (edges[i].nfaces == 2) {
            float d = edges[i].nx[0]*edges[i].nx[1] + edges[i].ny[0]*edges[i].ny[1] + edges[i].nz[0]*edges[i].nz[1];
            if (d > 0.9995f) continue;
        }
        nkept++;

        x0 = sxf[a]; y0 = syf[a]; x1 = sxf[b]; y1 = syf[b];
        len = (float)sqrt((x1-x0)*(x1-x0) + (y1-y0)*(y1-y0));
        nsamp = (int)(len / 1.25f) + 2;
        for (k = 0; k <= nsamp; k++) {
            float t = (float)k / (float)nsamp;
            float px = x0 + (x1-x0)*t, py = y0 + (y1-y0)*t;
            float wz = sw[a] + (sw[b]-sw[a])*t;
            int ix = (int)px, iy = (int)py;
            int vis = 0;
            if (ix >= 0 && ix < RENDER_W && iy >= 0 && iy < RENDER_H) {
                float zb = g_zbuf[iy * RENDER_W + ix];
                if (wz <= zb + 0.012f * wz) vis = 1;
            }
            if (vis) { visible_samples++; } else if (ix >= 0 && ix < RENDER_W && iy >= 0 && iy < RENDER_H) { hidden_samples++; }
            if (vis && !run_open) { run_open = 1; run_t0 = t; run_t1 = t; }
            else if (vis && run_open) { run_t1 = t; }
            else if (!vis && run_open) {
                run_open = 0;
                if (nruns < MAX_RUNS_PER_EDGE && run_t1 > run_t0) { runs[nruns][0]=run_t0; runs[nruns][1]=run_t1; nruns++; }
            }
        }
        if (run_open && nruns < MAX_RUNS_PER_EDGE && run_t1 > run_t0) { runs[nruns][0]=run_t0; runs[nruns][1]=run_t1; nruns++; }

        for (k = 0; k < nruns; k++) {
            float ax2 = x0 + (x1-x0)*runs[k][0], ay2 = y0 + (y1-y0)*runs[k][0];
            float bx2 = x0 + (x1-x0)*runs[k][1], by2 = y0 + (y1-y0)*runs[k][1];
            fprintf(svg, "<line x1=\"%.2f\" y1=\"%.2f\" x2=\"%.2f\" y2=\"%.2f\"/>\n", ax2, ay2, bx2, by2);
            BrPixelmapLine(pm, (int)ax2, (int)ay2, (int)bx2, (int)by2, COLOUR_INK);
            visible_segments++;
        }
    }
    fprintf(svg, "</g>\n</svg>\n");
    fclose(svg);

    free(sxf); free(syf); free(sw); free(edges);

    /* Self-verification: real geometry, active occlusion, sane visibility. */
    if (nunique < 50 || nkept < 30) { BrPixelmapFree(pm); BrEnd(); return 10; }
    if (visible_segments < 30) { BrPixelmapFree(pm); BrEnd(); return 11; }
    if (hidden_samples < 50) { BrPixelmapFree(pm); BrEnd(); return 12; }
    {
        float frac = (float)visible_samples / (float)(visible_samples + hidden_samples);
        if (frac < 0.05f || frac > 0.95f) { BrPixelmapFree(pm); BrEnd(); return 13; }
    }
    if (!dump_ppm(pm, ppm_path)) { BrPixelmapFree(pm); BrEnd(); return 14; }

    printf("brender plotter smoke: '%s' (%dv/%df) edges unique=%ld kept=%ld, segments=%ld, samples vis=%ld hid=%ld, wrote %s + %s\n",
        model_path, nv, nf, nunique, nkept, visible_segments, visible_samples, hidden_samples, svg_path, ppm_path);

    BrPixelmapFree(pm);
    if (BrEnd() != BRE_OK) return 15;
    return 0;
}
"""
