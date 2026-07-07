from __future__ import annotations


def multimodel_smoke_source() -> str:
    """C source for the BRender portable-core multi-part model render smoke.

    Loads every model chunk from a multi-part datafile with BrModelLoadMany and
    renders the assembled object depth-composited, so multi-part period assets
    (such as the coupe car, whose parts are separate model chunks) render whole
    rather than a single chunk.
    """
    return r"""/*
 * BRender v1.3.2 portable-core multi-part model render smoke.
 *
 * BrModelLoad returns only the first model chunk of a datafile. Multi-part
 * assets store each part as its own chunk, so this smoke uses BrModelLoadMany to
 * load them all, frames them together from their combined bounds, and renders
 * every part into one shared depth buffer so the whole object composites
 * correctly. Pure C, no softrend driver.
 *
 * Usage: brender_core_multimodel_smoke <model.dat> [output.ppm]
 */
#define __BR_V1DB__ 1
#include "brender.h"

#include <math.h>
#include <stdio.h>
#include <stdlib.h>

#define RENDER_W 320
#define RENDER_H 240
#define MAX_PARTS 128
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
    const char *model_path = (argc > 1) ? argv[1] : "coupe.dat";
    const char *out_path = (argc > 2) ? argv[2] : "brender-core-multimodel-smoke.ppm";
    br_pixelmap *pm;
    br_model *parts[MAX_PARTS];
    br_actor *world, *camera_actor;
    br_camera *camera;
    br_matrix34 base;
    float cx, cy, cz, radius, s;
    float lx = 0.35f, ly = 0.5f, lz = 1.0f, ll;
    br_uint_32 total_lit;
    long total_verts = 0, drawn = 0;
    int nparts, p, i;

    ll = (float)sqrt(lx*lx + ly*ly + lz*lz); lx/=ll; ly/=ll; lz/=ll;

    if (BrBegin() != BRE_OK) return 1;

    nparts = (int)BrModelLoadMany((char *)model_path, parts, MAX_PARTS);
    if (nparts < 1) { fprintf(stderr, "load failed: %s\n", model_path); BrEnd(); return 2; }

    pm = BrPixelmapAllocate(BR_PMT_RGB_888, RENDER_W, RENDER_H, NULL, BR_PMAF_NORMAL);
    if (pm == NULL || pm->pixels == NULL) { BrEnd(); return 3; }
    BrPixelmapFill(pm, COLOUR_BLACK);
    for (i = 0; i < RENDER_H * RENDER_W; i++) g_zbuf[i] = 1.0e30f;

    /* Combined bounds over every part, in shared model space. */
    cx = cy = cz = 0.0f;
    for (p = 0; p < nparts; p++) {
        br_model *m = parts[p];
        if (m == NULL || m->vertices == NULL) continue;
        for (i = 0; i < (int)m->nvertices; i++) {
            cx += BrScalarToFloat(m->vertices[i].p.v[0]);
            cy += BrScalarToFloat(m->vertices[i].p.v[1]);
            cz += BrScalarToFloat(m->vertices[i].p.v[2]);
            total_verts++;
        }
    }
    if (total_verts < 3) { BrPixelmapFree(pm); BrEnd(); return 4; }
    cx /= total_verts; cy /= total_verts; cz /= total_verts;
    radius = 0.0f;
    for (p = 0; p < nparts; p++) {
        br_model *m = parts[p];
        if (m == NULL || m->vertices == NULL) continue;
        for (i = 0; i < (int)m->nvertices; i++) {
            float dx = BrScalarToFloat(m->vertices[i].p.v[0]) - cx;
            float dy = BrScalarToFloat(m->vertices[i].p.v[1]) - cy;
            float dz = BrScalarToFloat(m->vertices[i].p.v[2]) - cz;
            float r = (float)sqrt(dx*dx + dy*dy + dz*dz);
            if (r > radius) radius = r;
        }
    }
    if (radius <= 0.0f) { BrPixelmapFree(pm); BrEnd(); return 5; }
    s = 1.6f / radius;

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

    /* One shared centre/scale/rotation transform for every part. */
    BrMatrix34RotateY(&base, BR_ANGLE_DEG(35));
    BrMatrix34PreRotateX(&base, BR_ANGLE_DEG(20));
    {
        int r, c; float lin[3][3], t0, t1, t2;
        for (r = 0; r < 3; r++) for (c = 0; c < 3; c++) lin[r][c] = BrScalarToFloat(base.m[r][c]) * s;
        t0 = -(cx*lin[0][0] + cy*lin[1][0] + cz*lin[2][0]);
        t1 = -(cx*lin[0][1] + cy*lin[1][1] + cz*lin[2][1]);
        t2 = -(cx*lin[0][2] + cy*lin[1][2] + cz*lin[2][2]);
        for (r = 0; r < 3; r++) for (c = 0; c < 3; c++) base.m[r][c] = BrFloatToScalar(lin[r][c]);
        base.m[3][0] = BrFloatToScalar(t0); base.m[3][1] = BrFloatToScalar(t1); base.m[3][2] = BrFloatToScalar(t2);
    }

    for (p = 0; p < nparts; p++) {
        br_model *m = parts[p];
        br_actor *actor;
        br_matrix4 m2s;
        int nv, nf;
        int *sx, *sy; float *sw, *wx, *wy, *wz;
        int tint = p % 3;
        if (m == NULL || m->vertices == NULL || m->faces == NULL || m->nvertices < 3) continue;
        nv = (int)m->nvertices; nf = (int)m->nfaces;

        actor = BrActorAllocate(BR_ACTOR_MODEL, NULL);
        if (actor == NULL) continue;
        actor->model = m;
        actor->t.type = BR_TRANSFORM_MATRIX34;
        actor->t.t.mat = base;
        BrActorAdd(world, actor);
        BrActorToScreenMatrix4(&m2s, actor, camera_actor);

        sx = malloc(sizeof(int)*nv); sy = malloc(sizeof(int)*nv); sw = malloc(sizeof(float)*nv);
        wx = malloc(sizeof(float)*nv); wy = malloc(sizeof(float)*nv); wz = malloc(sizeof(float)*nv);
        if (!sx||!sy||!sw||!wx||!wy||!wz) { free(sx);free(sy);free(sw);free(wx);free(wy);free(wz); continue; }

        for (i = 0; i < nv; i++) {
            br_vector4 clip; br_vector3 wp; float w, nx, ny;
            BrMatrix4ApplyP(&clip, &m->vertices[i].p, &m2s);
            w = BrScalarToFloat(clip.v[3]); sw[i] = w;
            if (w > 0.0f) {
                nx = BrScalarToFloat(clip.v[0]) / w; ny = BrScalarToFloat(clip.v[1]) / w;
                sx[i] = (int)lround((nx*0.5f + 0.5f) * RENDER_W);
                sy[i] = (int)lround((0.5f - ny*0.5f) * RENDER_H);
            } else { sx[i] = -10000; sy[i] = -10000; }
            BrMatrix34ApplyP(&wp, &m->vertices[i].p, &actor->t.t.mat);
            wx[i] = BrScalarToFloat(wp.v[0]); wy[i] = BrScalarToFloat(wp.v[1]); wz[i] = BrScalarToFloat(wp.v[2]);
        }
        for (i = 0; i < nf; i++) {
            int a = m->faces[i].vertices[0], b = m->faces[i].vertices[1], c = m->faces[i].vertices[2];
            float ux, uy, uz, vx, vy, vz, nnx, nny, nnz, nl2, dd, shade;
            int hi, mid; br_uint_32 colour;
            if (a<0||a>=nv||b<0||b>=nv||c<0||c>=nv) continue;
            if (sw[a] <= 0.0f || sw[b] <= 0.0f || sw[c] <= 0.0f) continue;
            ux=wx[b]-wx[a]; uy=wy[b]-wy[a]; uz=wz[b]-wz[a];
            vx=wx[c]-wx[a]; vy=wy[c]-wy[a]; vz=wz[c]-wz[a];
            nnx=uy*vz-uz*vy; nny=uz*vx-ux*vz; nnz=ux*vy-uy*vx;
            nl2=(float)sqrt(nnx*nnx+nny*nny+nnz*nnz);
            if (nl2 <= 0.0f) continue;
            nnx/=nl2; nny/=nl2; nnz/=nl2;
            dd = nnx*lx+nny*ly+nnz*lz; if (dd < 0.0f) dd = -dd;
            shade = 0.30f + 0.70f*dd; if (shade > 1.0f) shade = 1.0f;
            hi = (int)(shade*225.0f); mid = (int)(shade*150.0f);
            colour = (tint==0) ? BR_COLOUR_RGB(hi,mid,mid) : (tint==1) ? BR_COLOUR_RGB(mid,hi,mid) : BR_COLOUR_RGB(mid,mid,hi);
            fill_triangle_z(pm, sx[a],sy[a],sw[a], sx[b],sy[b],sw[b], sx[c],sy[c],sw[c], colour);
            drawn++;
        }
        free(sx);free(sy);free(sw);free(wx);free(wy);free(wz);
    }

    total_lit = count_lit(pm);
    if (drawn < 1 || total_lit < 800 || total_lit >= (br_uint_32)(RENDER_W*RENDER_H)) {
        BrPixelmapFree(pm); BrEnd(); return 7;
    }
    if (!dump_ppm(pm, out_path)) { BrPixelmapFree(pm); BrEnd(); return 8; }

    printf("brender multimodel smoke: '%s' loaded %d parts, %ld total verts, drew %ld faces, %lu lit, wrote %s\n",
        model_path, nparts, total_verts, drawn, (unsigned long)total_lit, out_path);

    BrPixelmapFree(pm);
    if (BrEnd() != BRE_OK) return 9;
    return 0;
}
"""
