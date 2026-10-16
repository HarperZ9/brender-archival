/*
 * SPDX-License-Identifier: MIT
 * One set of scenes, drawn by two BRender software rasterisers, for a
 * measured pixel comparison (docs/ROADMAP.md, item 5).
 *
 *   period: BRender 1.3.2 (Argonaut, 1998): softrend + pentprim, built 32-bit
 *           from the public source by the materialized harness
 *           (compile with PARITY_PERIOD=1; see period/CMakeLists.txt)
 *   modern: BRender 1.4 (BlazingRenderer): softrend + softprim, 64-bit
 *           (built by modern/CMakeLists.txt as parity-scene)
 *
 * Everything that is not the rasteriser is the same: the model, the camera,
 * the model transform, the material, the light and the 320 x 240 RGB_888
 * buffer. The renderer setup differs only where the two versions' APIs
 * differ, and each side copies the setup of its own ladder rung, which is
 * known to render.
 *
 * Usage: parity-scene <dat-dir> <out-dir>
 * Writes <out-dir>/<scene>.ppm for every scene and one JSON line per scene.
 */
#include "brender.h"
#include "brddi.h"
#if !PARITY_PERIOD
#include "brsdl3dev.h"
#endif
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define W 320
#define H 240

#if PARITY_PERIOD
void *BR_EXPORT BrDrv1SoftRendBegin(char *arguments);
void *BR_EXPORT BrDrv1PentPrimBegin(char *arguments);
br_error BR_PUBLIC_ENTRY BrV1dbRendererBegin(struct br_device_pixelmap *destination, struct br_renderer *renderer);
#define DEPTH_CLEAR 0xFFFFFFFF /* far: tt24_piz.asm draws where z < *zbuf */
#else
struct br_device *BR_EXPORT BrDrv1SoftPrimBegin(const char *arguments);
struct br_device *BR_EXPORT BrDrv1SoftRendBegin(const char *arguments);
#define DEPTH_CLEAR 0xFFFFFFFF
static char primitive_heap[1500 * 1024];
#endif

typedef struct scene {
    const char *name, *model;
    int         angle;   /* model turn about Y, degrees */
    br_uint_32  flags;   /* material flags */
    int         light;   /* add a directional light */
} scene;

/* Untextured on purpose: the period build's textured path is not working yet
 * (README, "BRender: rebuilt and rendering"), so texture parity is not
 * measured here. The control scene repeats "torus-flat" turned by another
 * 25 degrees; compared with "torus-flat" it must not match. */
static const scene scenes[] = {
    {"sphere-flat", "sph32.dat", 35, 0, 0},
    {"sphere-lit", "sph32.dat", 35, BR_MATF_LIGHT, 1},
    {"sphere-smooth", "sph32.dat", 35, BR_MATF_LIGHT | BR_MATF_SMOOTH, 1},
    {"torus-flat", "torus.dat", 60, 0, 0},
    {"torus-smooth", "torus.dat", 60, BR_MATF_LIGHT | BR_MATF_SMOOTH, 1},
    {"teapot-smooth", "teapot.dat", 20, BR_MATF_LIGHT | BR_MATF_SMOOTH, 1},
    {"control-torus-turned", "torus.dat", 85, 0, 0},
};

static int dump_ppm(const br_pixelmap *pm, const char *path)
{
    FILE *f = fopen(path, "wb");
    int x, y;
    if (f == NULL) return 0;
    fprintf(f, "P6\n%d %d\n255\n", (int)pm->width, (int)pm->height);
    for (y = 0; y < (int)pm->height; y++) {
        const unsigned char *row = (const unsigned char *)pm->pixels + (long)y * pm->row_bytes;
        for (x = 0; x < (int)pm->width; x++) {
            unsigned char rgb[3];
            rgb[0] = row[x * 3 + 2]; rgb[1] = row[x * 3 + 1]; rgb[2] = row[x * 3 + 0];
            fwrite(rgb, 1, 3, f);
        }
    }
    fclose(f);
    return 1;
}

static long count_lit(const br_pixelmap *pm)
{
    long total = 0;
    int x, y;
    for (y = 0; y < (int)pm->height; y++) {
        const unsigned char *row = (const unsigned char *)pm->pixels + (long)y * pm->row_bytes;
        for (x = 0; x < (int)pm->width; x++)
            total += (row[x * 3] | row[x * 3 + 1] | row[x * 3 + 2]) != 0;
    }
    return total;
}

/* Fit the model in a unit sphere at the origin, then turn it: the same
 * matrix arithmetic on both sides, in the same order. */
static void place_model(br_actor *actor, const br_model *model, int angle)
{
    float c[3] = {0, 0, 0}, radius = 0, s;
    int k, nv = (int)model->nvertices;
    br_matrix34 scale;
    for (k = 0; k < nv; k++) {
        c[0] += BrScalarToFloat(model->vertices[k].p.v[0]);
        c[1] += BrScalarToFloat(model->vertices[k].p.v[1]);
        c[2] += BrScalarToFloat(model->vertices[k].p.v[2]);
    }
    c[0] /= nv; c[1] /= nv; c[2] /= nv;
    for (k = 0; k < nv; k++) {
        float dx = BrScalarToFloat(model->vertices[k].p.v[0]) - c[0];
        float dy = BrScalarToFloat(model->vertices[k].p.v[1]) - c[1];
        float dz = BrScalarToFloat(model->vertices[k].p.v[2]) - c[2];
        float r = (float)sqrt(dx * dx + dy * dy + dz * dz);
        if (r > radius) radius = r;
    }
    s = radius > 0 ? 1.0f / radius : 1.0f;
    actor->t.type = BR_TRANSFORM_MATRIX34;
    BrMatrix34Translate(&actor->t.t.mat, BrFloatToScalar(-c[0]), BrFloatToScalar(-c[1]), BrFloatToScalar(-c[2]));
    BrMatrix34Scale(&scale, BrFloatToScalar(s), BrFloatToScalar(s), BrFloatToScalar(s));
    BrMatrix34Post(&actor->t.t.mat, &scale);
    BrMatrix34PostRotateX(&actor->t.t.mat, BR_ANGLE_DEG(25));
    BrMatrix34PostRotateY(&actor->t.t.mat, BR_ANGLE_DEG(angle));
}

int main(int argc, char **argv)
{
    const char *dat = argc > 1 ? argv[1] : ".", *out = argc > 2 ? argv[2] : ".";
    br_pixelmap *colour, *depth;
    br_actor *world, *camera_actor, *light_actor;
    br_camera *camera;
    int i, failed = 0;

    if (BrBegin() != BRE_OK) return 3;
#if PARITY_PERIOD
    /* the setup of the period renderer rung (brender-core-softrend-render.c) */
    if (BrDevAddStatic(NULL, (br_device_begin_fn *)BrDrv1SoftRendBegin, NULL) != BRE_OK) return 4;
    if (BrDevAddStatic(NULL, (br_device_begin_fn *)BrDrv1PentPrimBegin, NULL) != BRE_OK) return 4;
    {
        br_renderer_facility *facility = NULL;
        struct br_primitive_library *plib = NULL;
        void *heap = BrMemAllocate(512 * 1024, BR_MEMORY_APPLICATION);
        if (BrRendererFacilityFind(&facility, NULL, BRT_FLOAT) != BRE_OK || facility == NULL) return 5;
        if (BrV1dbRendererBegin(NULL, NULL) != BRE_OK) return 5;
        if (heap == NULL || BrPrimitiveLibraryFind(&plib, NULL, BR_SCALAR_TOKEN) != BRE_OK || plib == NULL) return 5;
        BrRendererBegin(NULL, NULL, plib, heap, 512 * 1024);
    }
    colour = BrPixelmapAllocate(BR_PMT_RGB_888, W, H, NULL, BR_PMAF_NORMAL);
    depth = BrPixelmapAllocate(BR_PMT_DEPTH_16, W, H, NULL, BR_PMAF_NORMAL);
#else
    /* the setup of the 1.4 renderer rung (ladder64/softrend-render-14.c) */
    {
        br_pixelmap *screen = NULL;
        if (BrDevAddStatic(NULL, BrDrv1SoftPrimBegin, NULL) != BRE_OK) return 4;
        if (BrDevAddStatic(NULL, BrDrv1SoftRendBegin, NULL) != BRE_OK) return 4;
        if (BrDevAddStatic(NULL, BrDrv1SDL3Begin, NULL) != BRE_OK) return 4;
        if (BrDevBeginVar(&screen, "SDL3", BRT_WIDTH_I32, W, BRT_HEIGHT_I32, H, BR_NULL_TOKEN) != BRE_OK) return 5;
        colour = BrPixelmapMatchTyped(screen, BR_PMMATCH_OFFSCREEN, BR_PMT_RGB_888);
        depth = colour ? BrPixelmapMatch(colour, BR_PMMATCH_DEPTH_16) : NULL;
        if (colour == NULL || depth == NULL) return 5;
        BrRendererBegin(colour, NULL, NULL, primitive_heap, sizeof(primitive_heap));
    }
#endif
    if (colour == NULL || depth == NULL) return 5;
    colour->origin_x = depth->origin_x = W / 2;
    colour->origin_y = depth->origin_y = H / 2;

    world = BrActorAllocate(BR_ACTOR_NONE, NULL);
    camera_actor = BrActorAdd(world, BrActorAllocate(BR_ACTOR_CAMERA, NULL));
    camera = (br_camera *)camera_actor->type_data;
    camera->type = BR_CAMERA_PERSPECTIVE_FOV;
    camera->field_of_view = BR_ANGLE_DEG(55);
    camera->hither_z = BrFloatToScalar(1.0f);
    camera->yon_z = BrFloatToScalar(100.0f);
    camera->aspect = BrFloatToScalar((float)W / (float)H);
    camera_actor->t.type = BR_TRANSFORM_MATRIX34;
    BrMatrix34Translate(&camera_actor->t.t.mat, 0, 0, BrFloatToScalar(2.5f));
    light_actor = BrActorAdd(world, BrActorAllocate(BR_ACTOR_LIGHT, NULL));
    light_actor->t.type = BR_TRANSFORM_MATRIX34;
    BrMatrix34RotateY(&light_actor->t.t.mat, BR_ANGLE_DEG(-30));
    BrMatrix34PostRotateX(&light_actor->t.t.mat, BR_ANGLE_DEG(-20));

    for (i = 0; i < (int)(sizeof(scenes) / sizeof(scenes[0])); i++) {
        const scene *sc = &scenes[i];
        char path[1024];
        br_model *model;
        br_material *material;
        br_actor *actor;
        long lit;
        snprintf(path, sizeof(path), "%s/%s", dat, sc->model);
        if ((model = BrModelLoad(path)) == NULL || model->nvertices < 3) {
            printf("{\"scene\":\"%s\",\"error\":\"model %s did not load\"}\n", sc->name, sc->model);
            failed++;
            continue;
        }
        actor = BrActorAdd(world, BrActorAllocate(BR_ACTOR_MODEL, NULL));
        place_model(actor, model, sc->angle); /* before BrModelUpdate, which may drop the vertex array */
        material = BrMaterialAllocate(sc->name);
        material->colour = BR_COLOUR_RGB(200, 170, 110);
        material->ka = BrFloatToScalar(0.15f);
        material->kd = BrFloatToScalar(0.85f);
        material->ks = BrFloatToScalar(0.0f);
        material->flags = sc->flags;
        BrMaterialUpdate(material, BR_MATU_ALL);
        BrModelUpdate(model, BR_MODU_ALL);
        actor->model = model;
        actor->material = material;
        if (sc->light) BrLightEnable(light_actor);
        else BrLightDisable(light_actor);
#if !PARITY_PERIOD
        BrRendererFrameBegin();
#endif
        BrPixelmapFill(colour, 0);
        BrPixelmapFill(depth, DEPTH_CLEAR);
        BrZbSceneRender(world, camera_actor, colour, depth);
#if !PARITY_PERIOD
        BrRendererFrameEnd();
#endif
        lit = count_lit(colour);
        snprintf(path, sizeof(path), "%s/%s.ppm", out, sc->name);
        if (!dump_ppm(colour, path)) failed++;
        printf("{\"scene\":\"%s\",\"model\":\"%s\",\"flags\":%u,\"light\":%d,\"lit_pixels\":%ld}\n", sc->name, sc->model,
               (unsigned)sc->flags, sc->light, lit);
        BrActorRemove(actor); /* one model in the world at a time */
    }
    fflush(stdout);
    /* As the period rung does, let BrEnd reclaim the rest at exit. */
    return failed ? 11 : 0;
}
