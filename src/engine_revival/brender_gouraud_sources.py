from __future__ import annotations


def gouraud_smoke_source() -> str:
    """C source for the BRender portable-core Gouraud-shaded render smoke.

    Where the fill/model smokes shade each face flat, this smoke computes a
    per-vertex normal for a loaded model (by averaging adjacent face normals),
    shades per vertex, and interpolates the shade smoothly across each triangle
    (Gouraud shading), depth-buffered. On a sphere the facets vanish into a
    smooth gradient.
    """
    return r"""/*
 * BRender v1.3.2 portable-core Gouraud-shaded render smoke.
 *
 * Smooth (Gouraud) shading over the depth-buffered rasterizer: per-vertex
 * normals are accumulated from the loaded model's faces, shaded per vertex, and
 * the shade is interpolated across each triangle so a faceted sphere renders as
 * a smooth gradient. Pure C, no softrend driver.
 *
 * Usage: brender_core_gouraud_smoke <model.dat> [output.ppm]
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

typedef struct { int x, y; float iw, sh; } gvert;  /* screen x,y; 1/w depth; shade */

static int lit(br_pixelmap *pm, int x, int y)
{
    return BrPixelmapPixelGet(pm, x, y) != COLOUR_BLACK;
}

/* Depth-tested triangle fill with a per-vertex shade interpolated across it. */
static void fill_triangle_gouraud(br_pixelmap *pm, gvert a, gvert b, gvert c)
{
    gvert v[3];
    int y, ymin, ymax;
    v[0] = a; v[1] = b; v[2] = c;
    ymin = v[0].y; if (v[1].y < ymin) ymin = v[1].y; if (v[2].y < ymin) ymin = v[2].y;
    ymax = v[0].y; if (v[1].y > ymax) ymax = v[1].y; if (v[2].y > ymax) ymax = v[2].y;
    if (ymin < 0) ymin = 0;
    if (ymax >= RENDER_H) ymax = RENDER_H - 1;
    for (y = ymin; y <= ymax; y++) {
        float cx[3], ciw[3], csh[3];
        int n = 0, e, lo, hi, x;
        for (e = 0; e < 3; e++) {
            gvert p0 = v[e], p1 = v[(e + 1) % 3];
            int ya = p0.y, yb = p1.y;
            if (ya == yb) continue;
            if ((y >= ya && y < yb) || (y >= yb && y < ya)) {
                float t = (float)(y - ya) / (float)(yb - ya);
                if (n < 3) {
                    cx[n]  = p0.x  + (p1.x  - p0.x)  * t;
                    ciw[n] = p0.iw + (p1.iw - p0.iw) * t;
                    csh[n] = p0.sh + (p1.sh - p0.sh) * t;
                    n++;
                }
            }
        }
        if (n < 2) continue;
        lo = 0; hi = 0;
        { int k; for (k = 1; k < n; k++) { if (cx[k] < cx[lo]) lo = k; if (cx[k] > cx[hi]) hi = k; } }
        {
            int xl = (int)(cx[lo] + 0.5f), xr = (int)(cx[hi] + 0.5f);
            float span = cx[hi] - cx[lo];
            for (x = xl; x <= xr; x++) {
                float f, iw, sh; int idx, g;
                if (x < 0 || x >= RENDER_W) continue;
                f = (span == 0.0f) ? 0.0f : ((float)x - cx[lo]) / span;
                iw = ciw[lo] + (ciw[hi] - ciw[lo]) * f;
                if (iw <= 0.0f) continue;
                idx = y * RENDER_W + x;
                if (iw <= g_zbuf[idx]) continue;
                sh = csh[lo] + (csh[hi] - csh[lo]) * f;
                if (sh < 0.0f) sh = 0.0f; if (sh > 1.0f) sh = 1.0f;
                g = (int)(sh * 235.0f);
                g_zbuf[idx] = iw;
                BrPixelmapPixelSet(pm, x, y, BR_COLOUR_RGB(g, g, (int)(g * 0.9f)));
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

static int distinct_greys(br_pixelmap *pm)
{
    unsigned char seen[256]; int count = 0, x, y, i;
    for (i = 0; i < 256; i++) seen[i] = 0;
    for (y = 0; y < RENDER_H; y++) for (x = 0; x < RENDER_W; x++) {
        br_uint_32 c = BrPixelmapPixelGet(pm, x, y);
        int r = (int)((c >> 16) & 0xff);
        if (c == COLOUR_BLACK) continue;
        if (!seen[r]) { seen[r] = 1; count++; }
    }
    return count;
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
    const char *model_path = (argc > 1) ? argv[1] : "sph32.dat";
    const char *out_path = (argc > 2) ? argv[2] : "brender-core-gouraud-smoke.ppm";
    br_pixelmap *pm;
    br_actor *world, *camera_actor, *model_actor;
    br_camera *camera;
    br_model *model;
    br_matrix4 m2s;
    br_matrix34 mm;
    int *sx = NULL, *sy = NULL; float *sw = NULL, *vsh = NULL;
    float *vnx = NULL, *vny = NULL, *vnz = NULL;
    float cx, cy, cz, radius, s;
    float lx = 0.4f, ly = 0.5f, lz = 0.9f, ll;
    br_uint_32 total_lit; int greys;
    long drawn = 0;
    int i, nv, nf;

    ll = (float)sqrt(lx*lx + ly*ly + lz*lz); lx/=ll; ly/=ll; lz/=ll;

    if (BrBegin() != BRE_OK) return 1;
    model = BrModelLoad((char *)model_path);
    if (model == NULL || model->nvertices < 3 || model->vertices == NULL || model->faces == NULL) {
        fprintf(stderr, "model load failed: %s\n", model_path); BrEnd(); return 2;
    }
    nv = (int)model->nvertices; nf = (int)model->nfaces;

    pm = BrPixelmapAllocate(BR_PMT_RGB_888, RENDER_W, RENDER_H, NULL, BR_PMAF_NORMAL);
    if (pm == NULL || pm->pixels == NULL) { BrEnd(); return 3; }
    BrPixelmapFill(pm, COLOUR_BLACK);
    for (i = 0; i < RENDER_H * RENDER_W; i++) g_zbuf[i] = 0.0f;

    /* Bounds. */
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
    s = 1.7f / radius;

    vnx = calloc(nv, sizeof(float)); vny = calloc(nv, sizeof(float)); vnz = calloc(nv, sizeof(float));
    if (!vnx || !vny || !vnz) { free(vnx);free(vny);free(vnz); BrPixelmapFree(pm); BrEnd(); return 5; }

    /* Per-vertex normals: accumulate model-space face normals at each vertex. */
    for (i = 0; i < nf; i++) {
        int a = model->faces[i].vertices[0], b = model->faces[i].vertices[1], c = model->faces[i].vertices[2];
        float ax, ay, az, bx, by, bz, ccx, ccy, ccz, ux, uy, uz, vx, vy, vz, nx, ny, nz;
        if (a<0||a>=nv||b<0||b>=nv||c<0||c>=nv) continue;
        ax=BrScalarToFloat(model->vertices[a].p.v[0]); ay=BrScalarToFloat(model->vertices[a].p.v[1]); az=BrScalarToFloat(model->vertices[a].p.v[2]);
        bx=BrScalarToFloat(model->vertices[b].p.v[0]); by=BrScalarToFloat(model->vertices[b].p.v[1]); bz=BrScalarToFloat(model->vertices[b].p.v[2]);
        ccx=BrScalarToFloat(model->vertices[c].p.v[0]); ccy=BrScalarToFloat(model->vertices[c].p.v[1]); ccz=BrScalarToFloat(model->vertices[c].p.v[2]);
        ux=bx-ax; uy=by-ay; uz=bz-az; vx=ccx-ax; vy=ccy-ay; vz=ccz-az;
        nx=uy*vz-uz*vy; ny=uz*vx-ux*vz; nz=ux*vy-uy*vx;
        vnx[a]+=nx; vny[a]+=ny; vnz[a]+=nz;
        vnx[b]+=nx; vny[b]+=ny; vnz[b]+=nz;
        vnx[c]+=nx; vny[c]+=ny; vnz[c]+=nz;
    }
    for (i = 0; i < nv; i++) {
        float l = (float)sqrt(vnx[i]*vnx[i] + vny[i]*vny[i] + vnz[i]*vnz[i]);
        if (l > 0.0f) { vnx[i]/=l; vny[i]/=l; vnz[i]/=l; }
    }

    world = BrActorAllocate(BR_ACTOR_NONE, NULL);
    camera_actor = BrActorAllocate(BR_ACTOR_CAMERA, NULL);
    if (world == NULL || camera_actor == NULL || camera_actor->type_data == NULL) {
        free(vnx);free(vny);free(vnz); BrPixelmapFree(pm); BrEnd(); return 6;
    }
    camera = (br_camera *)camera_actor->type_data;
    camera->type = BR_CAMERA_PERSPECTIVE;
    camera->field_of_view = BR_ANGLE_DEG(50);
    camera->hither_z = BrFloatToScalar(0.5f);
    camera->yon_z = BrFloatToScalar(500.0f);
    camera->aspect = BrFloatToScalar((float)RENDER_W / (float)RENDER_H);
    BrMatrix34Translate(&camera_actor->t.t.mat,
        BrFloatToScalar(0.0f), BrFloatToScalar(0.0f), BrFloatToScalar(5.0f));
    BrActorAdd(world, camera_actor);

    model_actor = BrActorAllocate(BR_ACTOR_MODEL, NULL);
    if (model_actor == NULL) { free(vnx);free(vny);free(vnz); BrPixelmapFree(pm); BrEnd(); return 7; }
    model_actor->model = model;
    BrMatrix34RotateY(&mm, BR_ANGLE_DEG(20));
    BrMatrix34PreRotateX(&mm, BR_ANGLE_DEG(-10));
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

    sx = malloc(sizeof(int)*nv); sy = malloc(sizeof(int)*nv); sw = malloc(sizeof(float)*nv); vsh = malloc(sizeof(float)*nv);
    if (!sx||!sy||!sw||!vsh) { free(sx);free(sy);free(sw);free(vsh);free(vnx);free(vny);free(vnz); BrPixelmapFree(pm); BrEnd(); return 8; }

    BrActorToScreenMatrix4(&m2s, model_actor, camera_actor);

    for (i = 0; i < nv; i++) {
        br_vector4 clip; br_vector3 nrm, wn; float w, nx, ny, dval;
        BrMatrix4ApplyP(&clip, &model->vertices[i].p, &m2s);
        w = BrScalarToFloat(clip.v[3]); sw[i] = w;
        if (w > 0.0f) {
            nx = BrScalarToFloat(clip.v[0]) / w; ny = BrScalarToFloat(clip.v[1]) / w;
            sx[i] = (int)lround((nx*0.5f + 0.5f) * RENDER_W);
            sy[i] = (int)lround((0.5f - ny*0.5f) * RENDER_H);
        } else { sx[i] = -10000; sy[i] = -10000; }
        /* Transform the vertex normal to world space, shade by the light. */
        BrVector3SetFloat(&nrm, vnx[i], vny[i], vnz[i]);
        BrMatrix34ApplyV(&wn, &nrm, &model_actor->t.t.mat);
        {
            float wx = BrScalarToFloat(wn.v[0]), wy = BrScalarToFloat(wn.v[1]), wz = BrScalarToFloat(wn.v[2]);
            float wl = (float)sqrt(wx*wx+wy*wy+wz*wz);
            if (wl > 0.0f) { wx/=wl; wy/=wl; wz/=wl; }
            dval = wx*lx + wy*ly + wz*lz; if (dval < 0.0f) dval = -dval;
            vsh[i] = 0.20f + 0.80f * dval;
        }
    }

    for (i = 0; i < nf; i++) {
        int a = model->faces[i].vertices[0], b = model->faces[i].vertices[1], c = model->faces[i].vertices[2];
        gvert va, vb, vc;
        if (a<0||a>=nv||b<0||b>=nv||c<0||c>=nv) continue;
        if (sw[a] <= 0.0f || sw[b] <= 0.0f || sw[c] <= 0.0f) continue;
        va.x=sx[a]; va.y=sy[a]; va.iw=1.0f/sw[a]; va.sh=vsh[a];
        vb.x=sx[b]; vb.y=sy[b]; vb.iw=1.0f/sw[b]; vb.sh=vsh[b];
        vc.x=sx[c]; vc.y=sy[c]; vc.iw=1.0f/sw[c]; vc.sh=vsh[c];
        fill_triangle_gouraud(pm, va, vb, vc);
        drawn++;
    }

    free(sx);free(sy);free(sw);free(vsh);free(vnx);free(vny);free(vnz);

    total_lit = count_lit(pm);
    greys = distinct_greys(pm);
    if (drawn < 1 || total_lit < 1500 || total_lit >= (br_uint_32)(RENDER_W*RENDER_H)) {
        BrPixelmapFree(pm); BrEnd(); return 9;
    }
    /* Smooth shading yields a wide, continuous range of grey levels. */
    if (greys < 20) { BrPixelmapFree(pm); BrEnd(); return 10; }
    if (!dump_ppm(pm, out_path)) { BrPixelmapFree(pm); BrEnd(); return 11; }

    printf("brender gouraud smoke: model '%s' (%dv/%df) smooth-shaded, %lu lit, %d grey levels, wrote %s\n",
        model_path, nv, nf, (unsigned long)total_lit, greys, out_path);

    BrPixelmapFree(pm);
    if (BrEnd() != BRE_OK) return 12;
    return 0;
}
"""
