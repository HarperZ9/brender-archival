from __future__ import annotations


def scene_smoke_source() -> str:
    """C source for the BRender portable-core scene-graph render smoke.

    Where the render smoke hand-rolled its projection matrix, this smoke drives
    BRender's own v1db scene database: it builds a world actor tree with a camera
    actor and a model actor holding a real, engine-prepared br_model cube, asks
    the engine for the model-to-screen matrix with BrActorToScreenMatrix4, then
    projects the model's own vertices and draws its faces as a wireframe through
    the pure-C memory pixelmap path. No rendering driver is involved;
    BrActorToScreenMatrix4 is pure matrix math and BrModelUpdate is pure-C mesh
    preparation.
    """
    return r"""/*
 * BRender v1.3.2 portable-core scene-graph render smoke.
 *
 * This milestone renders a model out of BRender's own v1db scene database,
 * using the engine's actor tree and camera to derive the projection, still
 * entirely on the pure-C path (no assembly softrend driver):
 *
 *   BrBegin                                          (also starts the v1db scene db)
 *     -> world  = BrActorAllocate(BR_ACTOR_NONE)
 *     -> camera = BrActorAllocate(BR_ACTOR_CAMERA)   (default perspective camera)
 *     -> model  = BrModelAllocate("cube", 8, 12)     (8 verts, 12 triangles)
 *        model->flags = BR_MODF_UPDATEABLE; BrModelUpdate(model, BR_MODU_ALL)
 *                                                     (engine computes bounds/normals,
 *                                                      keeps the vertex/face arrays)
 *     -> BrActorToScreenMatrix4(m, model_actor, camera)   (engine transform)
 *     -> BrMatrix4ApplyP per vertex + BrPixelmapLine per face edge
 *   BrEnd                                            (tears the scene db back down)
 *
 * BrBegin starts the v1db scene database itself, so BrV1dbBegin/BrV1dbEnd are
 * not called here; BrEnd performs the matching teardown. BrActorToScreenMatrix4
 * builds the camera perspective from the br_camera type_data and relates the two
 * actors through the world tree; it touches no driver. The wireframe is drawn
 * through the memory pixelmap dispatch backed by the harness _Mem* primitives.
 *
 * Self-verifying: allocation, fill, the model arrays, the engine-computed
 * bounding radius, all eight vertices projecting in front of the camera, a
 * deterministic reference line, and a plausible lit-pixel count. Returns 0 only
 * when every check passes.
 *
 * Usage: brender_core_scene_smoke [output.ppm]
 */
#define __BR_V1DB__ 1
#include "brender.h"

#include <math.h>
#include <stdio.h>
#include <stdlib.h>

#define RENDER_W 320
#define RENDER_H 240

#define COLOUR_BLACK BR_COLOUR_RGB(0, 0, 0)
#define COLOUR_WHITE BR_COLOUR_RGB(255, 255, 255)
#define COLOUR_RED   BR_COLOUR_RGB(255, 0, 0)

static const float CUBE_VERTS[8][3] = {
    {-1.0f, -1.0f, -1.0f}, { 1.0f, -1.0f, -1.0f},
    { 1.0f,  1.0f, -1.0f}, {-1.0f,  1.0f, -1.0f},
    {-1.0f, -1.0f,  1.0f}, { 1.0f, -1.0f,  1.0f},
    { 1.0f,  1.0f,  1.0f}, {-1.0f,  1.0f,  1.0f},
};

/* Twelve triangles, two per cube face. */
static const int CUBE_TRIS[12][3] = {
    {4, 5, 6}, {4, 6, 7},   /* front  (z = +1) */
    {1, 0, 3}, {1, 3, 2},   /* back   (z = -1) */
    {0, 4, 7}, {0, 7, 3},   /* left   (x = -1) */
    {5, 1, 2}, {5, 2, 6},   /* right  (x = +1) */
    {3, 7, 6}, {3, 6, 2},   /* top    (y = +1) */
    {0, 1, 5}, {0, 5, 4},   /* bottom (y = -1) */
};

static int lit(br_pixelmap *pm, int x, int y)
{
    return BrPixelmapPixelGet(pm, x, y) != COLOUR_BLACK;
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

/* Dump RGB_888 (stored B,G,R in memory) to a binary PPM (P6, R,G,B). */
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
    const char *out_path = (argc > 1) ? argv[1] : "brender-core-scene-smoke.ppm";
    br_pixelmap *pm;
    br_actor *world, *camera_actor, *model_actor;
    br_camera *camera;
    br_model *model;
    br_matrix4 model_to_screen;
    int screen_x[8];
    int screen_y[8];
    br_uint_32 total_lit;
    int i;

    /* BrBegin also starts the v1db scene database (BrEnd tears it down). */
    if (BrBegin() != BRE_OK) {
        return 1;
    }

    pm = BrPixelmapAllocate(BR_PMT_RGB_888, RENDER_W, RENDER_H, NULL, BR_PMAF_NORMAL);
    if (pm == NULL || pm->pixels == NULL) {
        BrEnd();
        return 2;
    }
    BrPixelmapFill(pm, COLOUR_BLACK);
    if (lit(pm, 0, 0)) {
        BrPixelmapFree(pm);
        BrEnd();
        return 3;
    }

    world = BrActorAllocate(BR_ACTOR_NONE, NULL);
    if (world == NULL) {
        BrPixelmapFree(pm);
        BrEnd();
        return 4;
    }

    /*
     * Camera actor. Passing NULL type_data makes BrActorAllocate build a
     * default perspective camera; adjust it to match the pixelmap aspect and
     * pull it back along +Z so a model at the origin is in front of the camera
     * (the projection maps clip.w = -z_camera, so the model needs z_camera < 0).
     */
    camera_actor = BrActorAllocate(BR_ACTOR_CAMERA, NULL);
    if (camera_actor == NULL || camera_actor->type_data == NULL) {
        BrPixelmapFree(pm);
        BrEnd();
        return 5;
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

    /* Cube model in the scene database, prepared by the engine. */
    model = BrModelAllocate("cube", 8, 12);
    if (model == NULL || model->vertices == NULL || model->faces == NULL ||
        model->nvertices != 8 || model->nfaces != 12) {
        BrPixelmapFree(pm);
        BrEnd();
        return 6;
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
    /*
     * BR_MODF_UPDATEABLE keeps the vertex/face arrays after preparation so the
     * wireframe can still read them; without it BrModelUpdate consumes them into
     * the internal prepared representation.
     */
    model->flags = BR_MODF_UPDATEABLE;
    BrModelUpdate(model, BR_MODU_ALL);
    if (model->vertices == NULL || model->faces == NULL ||
        !(BrScalarToFloat(model->radius) > 0.0f)) {
        BrPixelmapFree(pm);
        BrEnd();
        return 7;
    }

    /* Model actor: reference the cube, give it a three-quarter view rotation. */
    model_actor = BrActorAllocate(BR_ACTOR_MODEL, NULL);
    if (model_actor == NULL) {
        BrPixelmapFree(pm);
        BrEnd();
        return 8;
    }
    model_actor->model = model;
    BrMatrix34RotateY(&model_actor->t.t.mat, BR_ANGLE_DEG(35));
    BrMatrix34PreRotateX(&model_actor->t.t.mat, BR_ANGLE_DEG(25));
    BrActorAdd(world, model_actor);

    /* Ask the engine for the model-to-screen transform. */
    BrActorToScreenMatrix4(&model_to_screen, model_actor, camera_actor);

    for (i = 0; i < 8; i++) {
        br_vector4 clip;
        float w, ndc_x, ndc_y;

        BrMatrix4ApplyP(&clip, &model->vertices[i].p, &model_to_screen);
        w = BrScalarToFloat(clip.v[3]);
        if (!(w > 0.0f)) {
            BrPixelmapFree(pm);
            BrEnd();
            return 9;
        }
        ndc_x = BrScalarToFloat(clip.v[0]) / w;
        ndc_y = BrScalarToFloat(clip.v[1]) / w;
        screen_x[i] = (int)lround((ndc_x * 0.5f + 0.5f) * RENDER_W);
        screen_y[i] = (int)lround((0.5f - ndc_y * 0.5f) * RENDER_H);
    }

    {
        int inside = 0;
        for (i = 0; i < 8; i++) {
            if (screen_x[i] >= 0 && screen_x[i] < RENDER_W &&
                screen_y[i] >= 0 && screen_y[i] < RENDER_H) {
                inside++;
            }
        }
        if (inside < 4) {
            BrPixelmapFree(pm);
            BrEnd();
            return 10;
        }
    }

    /* Draw the model's own faces as a wireframe. */
    for (i = 0; i < 12; i++) {
        int a = CUBE_TRIS[i][0];
        int b = CUBE_TRIS[i][1];
        int c = CUBE_TRIS[i][2];
        BrPixelmapLine(pm, screen_x[a], screen_y[a], screen_x[b], screen_y[b], COLOUR_WHITE);
        BrPixelmapLine(pm, screen_x[b], screen_y[b], screen_x[c], screen_y[c], COLOUR_WHITE);
        BrPixelmapLine(pm, screen_x[c], screen_y[c], screen_x[a], screen_y[a], COLOUR_WHITE);
    }

    BrPixelmapLine(pm, 0, 0, RENDER_W - 1, RENDER_H - 1, COLOUR_RED);
    if (BrPixelmapPixelGet(pm, 0, 0) != COLOUR_RED ||
        BrPixelmapPixelGet(pm, RENDER_W - 1, RENDER_H - 1) != COLOUR_RED) {
        BrPixelmapFree(pm);
        BrEnd();
        return 11;
    }

    total_lit = count_lit(pm);
    if (total_lit < 200 || total_lit >= (br_uint_32)(RENDER_W * RENDER_H)) {
        BrPixelmapFree(pm);
        BrEnd();
        return 12;
    }

    if (!dump_ppm(pm, out_path)) {
        BrPixelmapFree(pm);
        BrEnd();
        return 13;
    }

    printf("brender scene smoke: %dx%d RGB_888, model '%s' %d verts %d faces radius %.3f, %lu lit pixels, wrote %s\n",
        RENDER_W, RENDER_H, model->identifier ? model->identifier : "?",
        (int)model->nvertices, (int)model->nfaces, BrScalarToFloat(model->radius),
        (unsigned long)total_lit, out_path);
    for (i = 0; i < 8; i++) {
        printf("  vertex %d -> (%d, %d)\n", i, screen_x[i], screen_y[i]);
    }

    BrPixelmapFree(pm);

    if (BrEnd() != BRE_OK) {
        return 14;
    }

    return 0;
}
"""
