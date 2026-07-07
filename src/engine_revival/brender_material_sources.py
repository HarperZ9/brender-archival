from __future__ import annotations


def material_smoke_source() -> str:
    """C source for the BRender portable-core textured-model render smoke.

    Renders a real loaded model (`sph32.dat`) textured through the model's OWN UV
    coordinates (br_vertex.map), depth-buffered and perspective-correct. The
    texture is generated in a BRender pixelmap so the smoke is self-contained and
    deterministic; the point it proves is that a datafile model's real UVs drive
    per-pixel texture sampling on the portable path.

    Loading period `.pix` textures directly is a known fidelity follow-up: the
    indexed variants (e.g. earth.pix) carry no embedded palette and need an
    external `.pal`, and the 15-bit variants (earth15.pix) load only partially
    through BrPixelmapLoad in this harness. This smoke therefore textures the
    real model with a generated map and records the `.pix` decode as future work.
    """
    return r"""/*
 * BRender v1.3.2 portable-core textured-model render smoke.
 *
 * Loads a real model from the period dat/ library and textures it through the
 * model's own UV coordinates, depth-buffered and perspective-correct, on the
 * pure-C path (no softrend driver):
 *
 *   BrBegin
 *     -> model = BrModelLoad("<...>/dat/sph32.dat")   (has per-vertex UVs)
 *     -> tex   = generated land/sea pixelmap
 *     -> per vertex: BrActorToScreenMatrix4 + model->vertices[i].map UVs
 *     -> per pixel: perspective-correct u/w,v/w,1/w texel, z-test, shade
 *   BrEnd
 *
 * The model's real UV coordinates wrap the texture around the loaded geometry,
 * proving datafile models carry usable texture coordinates.
 *
 * Usage: brender_core_material_smoke <model.dat> [output.ppm]
 */
#define __BR_V1DB__ 1
#include "brender.h"

#include <math.h>
#include <stdio.h>
#include <stdlib.h>

#define RENDER_W 320
#define RENDER_H 240
#define TEX_W 128
#define TEX_H 128
#define COLOUR_BLACK BR_COLOUR_RGB(0, 0, 0)

static float g_zbuf[RENDER_H * RENDER_W];

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
        float cx[3], ciw[3], cuo[3], cvo[3];
        int n = 0, e, lo, hi, x;
        for (e = 0; e < 3; e++) {
            tvert p0 = v[e], p1 = v[(e + 1) % 3];
            int ya = p0.y, yb = p1.y;
            if (ya == yb) continue;
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
        if (n < 2) continue;
        lo = 0; hi = 0;
        { int k; for (k = 1; k < n; k++) { if (cx[k] < cx[lo]) lo = k; if (cx[k] > cx[hi]) hi = k; } }
        {
            int xl = (int)(cx[lo] + 0.5f), xr = (int)(cx[hi] + 0.5f);
            float span = cx[hi] - cx[lo];
            for (x = xl; x <= xr; x++) {
                float f, iw, uo, vo, u, vv;
                int idx, tu, tv, r, g, bl;
                br_uint_32 texel;
                if (x < 0 || x >= RENDER_W) continue;
                f = (span == 0.0f) ? 0.0f : ((float)x - cx[lo]) / span;
                iw = ciw[lo] + (ciw[hi] - ciw[lo]) * f;
                if (iw <= 0.0f) continue;
                idx = y * RENDER_W + x;
                if (iw <= g_zbuf[idx]) continue;
                uo = cuo[lo] + (cuo[hi] - cuo[lo]) * f;
                vo = cvo[lo] + (cvo[hi] - cvo[lo]) * f;
                u = uo / iw; vv = vo / iw;
                tu = (int)(u * TEX_W); tu &= (TEX_W - 1);
                tv = (int)(vv * TEX_H); tv &= (TEX_H - 1);
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

static br_uint_32 count_lit(br_pixelmap *pm)
{
    br_uint_32 t = 0; int x, y;
    for (y = 0; y < RENDER_H; y++) for (x = 0; x < RENDER_W; x++) if (lit(pm, x, y)) t++;
    return t;
}

static int distinct_hues(br_pixelmap *pm)
{
    unsigned char seen[512];
    int count = 0, x, y, i;
    for (i = 0; i < 512; i++) seen[i] = 0;
    for (y = 0; y < RENDER_H; y++) for (x = 0; x < RENDER_W; x++) {
        br_uint_32 c = BrPixelmapPixelGet(pm, x, y);
        int r = (int)((c >> 16) & 0xff), g = (int)((c >> 8) & 0xff), b = (int)(c & 0xff), bucket;
        if (c == COLOUR_BLACK) continue;
        bucket = ((r >> 5) << 6) | ((g >> 5) << 3) | (b >> 5);
        if (bucket < 512 && !seen[bucket]) { seen[bucket] = 1; count++; }
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

/* A generated land/sea globe texture, with a lat/long grid so the UV wrap on
   the loaded sphere is visible. */
static void build_texture(br_pixelmap *tex)
{
    int tx, ty;
    for (ty = 0; ty < TEX_H; ty++) {
        for (tx = 0; tx < TEX_W; tx++) {
            int land = (((tx * 5) / TEX_W + (ty * 3) / TEX_H) % 2) &&
                       (((tx / 12) ^ (ty / 12)) & 1);
            int grid = (tx % 16 == 0) || (ty % 16 == 0);
            br_uint_32 c;
            if (grid) c = BR_COLOUR_RGB(20, 30, 40);
            else if (land) c = BR_COLOUR_RGB(70, 150, 60);      /* land */
            else c = BR_COLOUR_RGB(30, 80, 170);                /* sea */
            BrPixelmapPixelSet(tex, tx, ty, c);
        }
    }
}

int main(int argc, char **argv)
{
    const char *model_path = (argc > 1) ? argv[1] : "sph32.dat";
    const char *out_path = (argc > 2) ? argv[2] : "brender-core-material-smoke.ppm";
    br_pixelmap *pm, *tex;
    br_actor *world, *camera_actor, *model_actor;
    br_camera *camera;
    br_model *model;
    br_matrix4 m2s;
    br_matrix34 mm;
    int *sx = NULL, *sy = NULL; float *sw = NULL, *su = NULL, *sv = NULL;
    float *wx = NULL, *wy = NULL, *wz = NULL;
    float cx, cy, cz, radius, s;
    float lx = 0.3f, ly = 0.4f, lz = 1.0f, ll;
    br_uint_32 total_lit; int hues;
    long drawn = 0;
    int i, nv, nf;

    ll = (float)sqrt(lx*lx + ly*ly + lz*lz); lx/=ll; ly/=ll; lz/=ll;

    if (BrBegin() != BRE_OK) return 1;

    model = BrModelLoad((char *)model_path);
    if (model == NULL || model->nvertices < 3 || model->vertices == NULL || model->faces == NULL) {
        fprintf(stderr, "model load failed: %s\n", model_path); BrEnd(); return 2;
    }
    nv = (int)model->nvertices; nf = (int)model->nfaces;

    tex = BrPixelmapAllocate(BR_PMT_RGB_888, TEX_W, TEX_H, NULL, BR_PMAF_NORMAL);
    if (tex == NULL || tex->pixels == NULL) { BrEnd(); return 3; }
    build_texture(tex);

    pm = BrPixelmapAllocate(BR_PMT_RGB_888, RENDER_W, RENDER_H, NULL, BR_PMAF_NORMAL);
    if (pm == NULL || pm->pixels == NULL) { BrPixelmapFree(tex); BrEnd(); return 4; }
    BrPixelmapFill(pm, COLOUR_BLACK);
    for (i = 0; i < RENDER_H * RENDER_W; i++) g_zbuf[i] = 0.0f;

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
    if (radius <= 0.0f) { BrPixelmapFree(tex); BrPixelmapFree(pm); BrEnd(); return 5; }
    s = 1.7f / radius;

    world = BrActorAllocate(BR_ACTOR_NONE, NULL);
    camera_actor = BrActorAllocate(BR_ACTOR_CAMERA, NULL);
    if (world == NULL || camera_actor == NULL || camera_actor->type_data == NULL) {
        BrPixelmapFree(tex); BrPixelmapFree(pm); BrEnd(); return 6;
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
    if (model_actor == NULL) { BrPixelmapFree(tex); BrPixelmapFree(pm); BrEnd(); return 7; }
    model_actor->model = model;
    BrMatrix34RotateY(&mm, BR_ANGLE_DEG(25));
    BrMatrix34PreRotateX(&mm, BR_ANGLE_DEG(-15));
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

    sx = malloc(sizeof(int)*nv); sy = malloc(sizeof(int)*nv); sw = malloc(sizeof(float)*nv);
    su = malloc(sizeof(float)*nv); sv = malloc(sizeof(float)*nv);
    wx = malloc(sizeof(float)*nv); wy = malloc(sizeof(float)*nv); wz = malloc(sizeof(float)*nv);
    if (!sx||!sy||!sw||!su||!sv||!wx||!wy||!wz) {
        free(sx);free(sy);free(sw);free(su);free(sv);free(wx);free(wy);free(wz);
        BrPixelmapFree(tex); BrPixelmapFree(pm); BrEnd(); return 8;
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
            sx[i] = (int)lround((ndc_x*0.5f + 0.5f) * RENDER_W);
            sy[i] = (int)lround((0.5f - ndc_y*0.5f) * RENDER_H);
        } else { sx[i] = -10000; sy[i] = -10000; }
        su[i] = BrScalarToFloat(model->vertices[i].map.v[0]);
        sv[i] = BrScalarToFloat(model->vertices[i].map.v[1]);
        BrMatrix34ApplyP(&wpos, &model->vertices[i].p, &model_actor->t.t.mat);
        wx[i] = BrScalarToFloat(wpos.v[0]); wy[i] = BrScalarToFloat(wpos.v[1]); wz[i] = BrScalarToFloat(wpos.v[2]);
    }

    for (i = 0; i < nf; i++) {
        int a = model->faces[i].vertices[0], b = model->faces[i].vertices[1], c = model->faces[i].vertices[2];
        float ux, uy, uz, vx, vy, vz, nx, ny, nz, nl, d, shade;
        tvert va, vb, vc;
        if (a<0||a>=nv||b<0||b>=nv||c<0||c>=nv) continue;
        if (sw[a] <= 0.0f || sw[b] <= 0.0f || sw[c] <= 0.0f) continue;
        ux = wx[b]-wx[a]; uy = wy[b]-wy[a]; uz = wz[b]-wz[a];
        vx = wx[c]-wx[a]; vy = wy[c]-wy[a]; vz = wz[c]-wz[a];
        nx = uy*vz-uz*vy; ny = uz*vx-ux*vz; nz = ux*vy-uy*vx;
        nl = (float)sqrt(nx*nx+ny*ny+nz*nz);
        if (nl <= 0.0f) continue;
        nx/=nl; ny/=nl; nz/=nl;
        d = nx*lx + ny*ly + nz*lz; if (d < 0.0f) d = -d;
        shade = 0.55f + 0.45f*d; if (shade > 1.0f) shade = 1.0f;
        va.x=sx[a]; va.y=sy[a]; va.iw=1.0f/sw[a]; va.uow=su[a]/sw[a]; va.vow=sv[a]/sw[a];
        vb.x=sx[b]; vb.y=sy[b]; vb.iw=1.0f/sw[b]; vb.uow=su[b]/sw[b]; vb.vow=sv[b]/sw[b];
        vc.x=sx[c]; vc.y=sy[c]; vc.iw=1.0f/sw[c]; vc.uow=su[c]/sw[c]; vc.vow=sv[c]/sw[c];
        fill_triangle_tex(pm, tex, va, vb, vc, shade);
        drawn++;
    }

    free(sx);free(sy);free(sw);free(su);free(sv);free(wx);free(wy);free(wz);

    total_lit = count_lit(pm);
    hues = distinct_hues(pm);
    if (drawn < 1 || total_lit < 1500 || total_lit >= (br_uint_32)(RENDER_W*RENDER_H)) {
        BrPixelmapFree(tex); BrPixelmapFree(pm); BrEnd(); return 9;
    }
    if (hues < 4) { BrPixelmapFree(tex); BrPixelmapFree(pm); BrEnd(); return 10; }
    if (!dump_ppm(pm, out_path)) { BrPixelmapFree(tex); BrPixelmapFree(pm); BrEnd(); return 11; }

    printf("brender material smoke: model '%s' (%dv/%df) textured via model UVs, %lu lit, %d hues, wrote %s\n",
        model_path, nv, nf, (unsigned long)total_lit, hues, out_path);

    BrPixelmapFree(tex);
    BrPixelmapFree(pm);
    if (BrEnd() != BRE_OK) return 12;
    return 0;
}
"""
