from __future__ import annotations


def fill_smoke_source() -> str:
    """C source for the BRender portable-core solid-shaded render smoke.

    This is the first BRender revival milestone that produces a solid, shaded
    image rather than a wireframe, still without the assembly softrend renderer.
    It reuses the v1db scene-graph projection (camera + model actors +
    BrActorToScreenMatrix4), then rasterizes each triangle face with a small C
    scanline fill, shaded flat from the face's world-space normal. Faces are
    drawn back-to-front (painter's algorithm) so the convex cube composites
    correctly with no depth buffer, and shading uses the absolute normal-light
    dot so it is independent of triangle winding.
    """
    return r"""/*
 * BRender v1.3.2 portable-core solid-shaded render smoke.
 *
 * Turns the v1db scene-graph render from a wireframe into a solid, flat-shaded
 * image, still entirely on the pure-C path (no assembly softrend renderer):
 *
 *   BrBegin -> world/camera/model actor tree -> BrModelUpdate
 *     -> BrActorToScreenMatrix4 (engine projection)
 *     -> per vertex: BrMatrix4ApplyP (screen) + BrMatrix34ApplyP (world, for lighting)
 *     -> per face: world-space normal, flat shade by |normal . light|,
 *        C scanline triangle fill, painter's-ordered back-to-front
 *   BrEnd
 *
 * The convex cube needs no depth buffer: drawing faces far-to-near composites
 * correctly. Shading uses the absolute normal-light dot, so it does not depend
 * on triangle winding. Every pixel is written through the pure-C memory pixelmap
 * primitives.
 *
 * Self-verifying: a solid (large) lit-pixel count and at least two distinct
 * shaded grey levels prove both the fill and the shading ran. Returns 0 only
 * when every check passes.
 *
 * Usage: brender_core_fill_smoke [output.ppm]
 */
#define __BR_V1DB__ 1
#include "brender.h"

#include <math.h>
#include <stdio.h>
#include <stdlib.h>

#define RENDER_W 320
#define RENDER_H 240

#define COLOUR_BLACK BR_COLOUR_RGB(0, 0, 0)
#define COLOUR_RED   BR_COLOUR_RGB(255, 0, 0)

static const float CUBE_VERTS[8][3] = {
    {-1.0f, -1.0f, -1.0f}, { 1.0f, -1.0f, -1.0f},
    { 1.0f,  1.0f, -1.0f}, {-1.0f,  1.0f, -1.0f},
    {-1.0f, -1.0f,  1.0f}, { 1.0f, -1.0f,  1.0f},
    { 1.0f,  1.0f,  1.0f}, {-1.0f,  1.0f,  1.0f},
};

static const int CUBE_TRIS[12][3] = {
    {4, 5, 6}, {4, 6, 7},   /* front  */
    {1, 0, 3}, {1, 3, 2},   /* back   */
    {0, 4, 7}, {0, 7, 3},   /* left   */
    {5, 1, 2}, {5, 2, 6},   /* right  */
    {3, 7, 6}, {3, 6, 2},   /* top    */
    {0, 1, 5}, {0, 5, 4},   /* bottom */
};

static float g_world[8][3];   /* cube vertices in world space, for lighting */

static int lit(br_pixelmap *pm, int x, int y)
{
    return BrPixelmapPixelGet(pm, x, y) != COLOUR_BLACK;
}

/* Fill one horizontal span, clipped to the pixelmap. */
static void span(br_pixelmap *pm, int y, int xa, int xb, br_uint_32 colour)
{
    int x;

    if (y < 0 || y >= RENDER_H) {
        return;
    }
    if (xa > xb) {
        int t = xa; xa = xb; xb = t;
    }
    if (xa < 0) {
        xa = 0;
    }
    if (xb >= RENDER_W) {
        xb = RENDER_W - 1;
    }
    for (x = xa; x <= xb; x++) {
        BrPixelmapPixelSet(pm, x, y, colour);
    }
}

/* Flat-fill a screen-space triangle by scanning between its edges. */
static void fill_triangle(br_pixelmap *pm, int x0, int y0, int x1, int y1,
    int x2, int y2, br_uint_32 colour)
{
    int y, ymin, ymax;

    ymin = y0; if (y1 < ymin) ymin = y1; if (y2 < ymin) ymin = y2;
    ymax = y0; if (y1 > ymax) ymax = y1; if (y2 > ymax) ymax = y2;
    if (ymin < 0) ymin = 0;
    if (ymax >= RENDER_H) ymax = RENDER_H - 1;

    for (y = ymin; y <= ymax; y++) {
        int hits[3];
        int n = 0;
        int e;
        int ex[3][2], ey[3][2];

        ex[0][0] = x0; ey[0][0] = y0; ex[0][1] = x1; ey[0][1] = y1;
        ex[1][0] = x1; ey[1][0] = y1; ex[1][1] = x2; ey[1][1] = y2;
        ex[2][0] = x2; ey[2][0] = y2; ex[2][1] = x0; ey[2][1] = y0;

        for (e = 0; e < 3; e++) {
            int ya = ey[e][0], yb = ey[e][1];
            int xa = ex[e][0], xb = ex[e][1];
            if (ya == yb) {
                continue;
            }
            if ((y >= ya && y < yb) || (y >= yb && y < ya)) {
                int xi = xa + (int)((long)(xb - xa) * (y - ya) / (yb - ya));
                if (n < 3) {
                    hits[n++] = xi;
                }
            }
        }
        if (n >= 2) {
            int lo = hits[0], hi = hits[0];
            int k;
            for (k = 1; k < n; k++) {
                if (hits[k] < lo) lo = hits[k];
                if (hits[k] > hi) hi = hits[k];
            }
            span(pm, y, lo, hi, colour);
        }
    }
}

static br_uint_32 count_lit(br_pixelmap *pm)
{
    br_uint_32 total = 0;
    int x, y;

    for (y = 0; y < RENDER_H; y++) {
        for (x = 0; x < RENDER_W; x++) {
            if (lit(pm, x, y)) {
                total++;
            }
        }
    }
    return total;
}

/* Number of distinct grey levels among lit, non-red pixels (proves shading). */
static int distinct_greys(br_pixelmap *pm)
{
    unsigned char seen[256];
    int count = 0;
    int x, y, i;

    for (i = 0; i < 256; i++) {
        seen[i] = 0;
    }
    for (y = 0; y < RENDER_H; y++) {
        for (x = 0; x < RENDER_W; x++) {
            br_uint_32 c = BrPixelmapPixelGet(pm, x, y);
            int r = (int)((c >> 16) & 0xff);
            int g = (int)((c >> 8) & 0xff);
            int b = (int)(c & 0xff);
            if (c == COLOUR_BLACK || c == COLOUR_RED) {
                continue;
            }
            if (r == g && g == b && !seen[r]) {
                seen[r] = 1;
                count++;
            }
        }
    }
    return count;
}

static int dump_ppm(br_pixelmap *pm, const char *path)
{
    FILE *f = fopen(path, "wb");
    const unsigned char *base;
    int x, y;

    if (f == NULL) {
        return 0;
    }
    fprintf(f, "P6\n%d %d\n255\n", (int)pm->width, (int)pm->height);
    base = (const unsigned char *)pm->pixels;
    for (y = 0; y < (int)pm->height; y++) {
        const unsigned char *row = base + (long)y * pm->row_bytes;
        for (x = 0; x < (int)pm->width; x++) {
            const unsigned char *px = row + (long)x * 3;
            unsigned char rgb[3];
            rgb[0] = px[2];
            rgb[1] = px[1];
            rgb[2] = px[0];
            fwrite(rgb, 1, 3, f);
        }
    }
    fclose(f);
    return 1;
}

int main(int argc, char **argv)
{
    const char *out_path = (argc > 1) ? argv[1] : "brender-core-fill-smoke.ppm";
    br_pixelmap *pm;
    br_actor *world, *camera_actor, *model_actor;
    br_camera *camera;
    br_model *model;
    br_matrix4 model_to_screen;
    int screen_x[8];
    int screen_y[8];
    float depth[8];
    int order[12];
    float face_depth[12];
    br_uint_32 total_lit;
    int greys;
    int i, j;

    /* Light direction (world space), pointing from the upper front. */
    float lx = 0.3f, ly = 0.5f, lz = 1.0f;
    float ll = (float)sqrt(lx * lx + ly * ly + lz * lz);
    lx /= ll; ly /= ll; lz /= ll;

    if (BrBegin() != BRE_OK) {
        return 1;
    }

    pm = BrPixelmapAllocate(BR_PMT_RGB_888, RENDER_W, RENDER_H, NULL, BR_PMAF_NORMAL);
    if (pm == NULL || pm->pixels == NULL) {
        BrEnd();
        return 2;
    }
    BrPixelmapFill(pm, COLOUR_BLACK);

    world = BrActorAllocate(BR_ACTOR_NONE, NULL);
    camera_actor = BrActorAllocate(BR_ACTOR_CAMERA, NULL);
    if (world == NULL || camera_actor == NULL || camera_actor->type_data == NULL) {
        BrPixelmapFree(pm);
        BrEnd();
        return 3;
    }
    camera = (br_camera *)camera_actor->type_data;
    camera->type = BR_CAMERA_PERSPECTIVE;
    camera->field_of_view = BR_ANGLE_DEG(60);
    camera->hither_z = BrFloatToScalar(1.0f);
    camera->yon_z = BrFloatToScalar(100.0f);
    camera->aspect = BrFloatToScalar((float)RENDER_W / (float)RENDER_H);
    BrMatrix34Translate(&camera_actor->t.t.mat,
        BrFloatToScalar(0.0f), BrFloatToScalar(0.0f), BrFloatToScalar(6.0f));
    BrActorAdd(world, camera_actor);

    model = BrModelAllocate("cube", 8, 12);
    if (model == NULL || model->vertices == NULL || model->faces == NULL) {
        BrPixelmapFree(pm);
        BrEnd();
        return 4;
    }
    for (i = 0; i < 8; i++) {
        BrVector3SetFloat(&model->vertices[i].p,
            CUBE_VERTS[i][0], CUBE_VERTS[i][1], CUBE_VERTS[i][2]);
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
    if (model_actor == NULL) {
        BrPixelmapFree(pm);
        BrEnd();
        return 5;
    }
    model_actor->model = model;
    BrMatrix34RotateY(&model_actor->t.t.mat, BR_ANGLE_DEG(35));
    BrMatrix34PreRotateX(&model_actor->t.t.mat, BR_ANGLE_DEG(25));
    BrActorAdd(world, model_actor);

    BrActorToScreenMatrix4(&model_to_screen, model_actor, camera_actor);

    /* Project to screen, and transform to world space for lighting. */
    for (i = 0; i < 8; i++) {
        br_vector4 clip;
        br_vector3 wpos;
        float w, ndc_x, ndc_y;

        BrMatrix4ApplyP(&clip, &model->vertices[i].p, &model_to_screen);
        w = BrScalarToFloat(clip.v[3]);
        if (!(w > 0.0f)) {
            BrPixelmapFree(pm);
            BrEnd();
            return 6;
        }
        ndc_x = BrScalarToFloat(clip.v[0]) / w;
        ndc_y = BrScalarToFloat(clip.v[1]) / w;
        screen_x[i] = (int)lround((ndc_x * 0.5f + 0.5f) * RENDER_W);
        screen_y[i] = (int)lround((0.5f - ndc_y * 0.5f) * RENDER_H);
        depth[i] = w; /* larger w == farther from camera */

        BrMatrix34ApplyP(&wpos, &model->vertices[i].p, &model_actor->t.t.mat);
        g_world[i][0] = BrScalarToFloat(wpos.v[0]);
        g_world[i][1] = BrScalarToFloat(wpos.v[1]);
        g_world[i][2] = BrScalarToFloat(wpos.v[2]);
    }

    /* Painter's order: sort face indices by descending average depth. */
    for (i = 0; i < 12; i++) {
        int a = CUBE_TRIS[i][0], b = CUBE_TRIS[i][1], c = CUBE_TRIS[i][2];
        face_depth[i] = (depth[a] + depth[b] + depth[c]) / 3.0f;
        order[i] = i;
    }
    for (i = 0; i < 12; i++) {
        for (j = i + 1; j < 12; j++) {
            if (face_depth[order[j]] > face_depth[order[i]]) {
                int t = order[i]; order[i] = order[j]; order[j] = t;
            }
        }
    }

    /* Draw faces back-to-front, flat-shaded from the world-space normal. */
    for (i = 0; i < 12; i++) {
        int fi = order[i];
        int a = CUBE_TRIS[fi][0], b = CUBE_TRIS[fi][1], c = CUBE_TRIS[fi][2];
        float ux = g_world[b][0] - g_world[a][0];
        float uy = g_world[b][1] - g_world[a][1];
        float uz = g_world[b][2] - g_world[a][2];
        float vx = g_world[c][0] - g_world[a][0];
        float vy = g_world[c][1] - g_world[a][1];
        float vz = g_world[c][2] - g_world[a][2];
        float nx = uy * vz - uz * vy;
        float ny = uz * vx - ux * vz;
        float nz = ux * vy - uy * vx;
        float nl = (float)sqrt(nx * nx + ny * ny + nz * nz);
        float d, shade;
        int grey;
        br_uint_32 colour;

        if (nl <= 0.0f) {
            continue;
        }
        nx /= nl; ny /= nl; nz /= nl;
        d = nx * lx + ny * ly + nz * lz;
        if (d < 0.0f) {
            d = -d; /* winding-independent */
        }
        shade = 0.25f + 0.75f * d; /* ambient + diffuse */
        if (shade > 1.0f) {
            shade = 1.0f;
        }
        grey = (int)(shade * 255.0f);
        colour = BR_COLOUR_RGB(grey, grey, grey);
        fill_triangle(pm, screen_x[a], screen_y[a], screen_x[b], screen_y[b],
            screen_x[c], screen_y[c], colour);
    }

    /* Deterministic reference line with guaranteed-plotted endpoints. */
    BrPixelmapLine(pm, 0, 0, RENDER_W - 1, RENDER_H - 1, COLOUR_RED);
    if (BrPixelmapPixelGet(pm, 0, 0) != COLOUR_RED ||
        BrPixelmapPixelGet(pm, RENDER_W - 1, RENDER_H - 1) != COLOUR_RED) {
        BrPixelmapFree(pm);
        BrEnd();
        return 7;
    }

    /* A solid render lights up far more pixels than a wireframe. */
    total_lit = count_lit(pm);
    if (total_lit < 3000 || total_lit >= (br_uint_32)(RENDER_W * RENDER_H)) {
        BrPixelmapFree(pm);
        BrEnd();
        return 8;
    }

    /* Flat shading must produce at least two distinct face brightnesses. */
    greys = distinct_greys(pm);
    if (greys < 2) {
        BrPixelmapFree(pm);
        BrEnd();
        return 9;
    }

    if (!dump_ppm(pm, out_path)) {
        BrPixelmapFree(pm);
        BrEnd();
        return 10;
    }

    printf("brender fill smoke: %dx%d RGB_888, model '%s' radius %.3f, %lu lit pixels, %d grey levels, wrote %s\n",
        RENDER_W, RENDER_H, model->identifier ? model->identifier : "?",
        BrScalarToFloat(model->radius), (unsigned long)total_lit, greys, out_path);

    BrPixelmapFree(pm);

    if (BrEnd() != BRE_OK) {
        return 11;
    }

    return 0;
}
"""
