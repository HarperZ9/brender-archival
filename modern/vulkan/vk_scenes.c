/*
 * SPDX-License-Identifier: MIT
 * vkprim's parity check (docs/adr/0002-vulkan-backend.md, stage B): the same
 * untextured scenes rendered by softrend into softprim, or into vkprim, which
 * rasterises softprim's own screen-space vertices with Vulkan.
 *
 * Usage: vk-scenes <dat-dir> <out-dir> software|vulkan
 * Writes <out-dir>/<scene>.ppm (320 x 240) and one JSON line per scene.
 */
#include "brender.h"
#include "brddi.h"
#include "brsdl3dev.h"
#include <math.h>
#include <stdio.h>
#include <string.h>

#include "vkprim.h"

#define W 320
#define H 240

struct br_device *BR_EXPORT BrDrv1SoftPrimBegin(const char *arguments);
struct br_device *BR_EXPORT BrDrv1SoftRendBegin(const char *arguments);
static char primitive_heap[1500 * 1024];

typedef struct scene { const char *name, *model; int angle; br_uint_32 flags; int light; } scene;

static const scene scenes[] = {
    {"sphere-flat", "sph32.dat", 35, 0, 0},
    {"sphere-lit", "sph32.dat", 35, BR_MATF_LIGHT, 1},
    {"sphere-smooth", "sph32.dat", 35, BR_MATF_LIGHT | BR_MATF_SMOOTH, 1},
    {"torus-flat", "torus.dat", 60, 0, 0},
    {"torus-smooth", "torus.dat", 60, BR_MATF_LIGHT | BR_MATF_SMOOTH, 1},
    {"teapot-smooth", "teapot.dat", 20, BR_MATF_LIGHT | BR_MATF_SMOOTH, 1},
    {"control-torus-turned", "torus.dat", 85, 0, 0},
};

/* Scale the model into a unit sphere at the origin and turn it. */
static void place(br_actor *a, const br_model *m, int angle)
{
    float r = 0.0f;
    int i;
    for (i = 0; i < m->nvertices; i++) {
        const br_vector3 *p = &m->vertices[i].p;
        float d = sqrtf(BrScalarToFloat(p->v[0]) * BrScalarToFloat(p->v[0]) + BrScalarToFloat(p->v[1]) * BrScalarToFloat(p->v[1])
                        + BrScalarToFloat(p->v[2]) * BrScalarToFloat(p->v[2]));
        if (d > r) r = d;
    }
    a->t.type = BR_TRANSFORM_MATRIX34;
    BrMatrix34Scale(&a->t.t.mat, BrFloatToScalar(1.0f / r), BrFloatToScalar(1.0f / r), BrFloatToScalar(1.0f / r));
    BrMatrix34PostRotateY(&a->t.t.mat, BR_ANGLE_DEG(angle));
    BrMatrix34PostRotateX(&a->t.t.mat, BR_ANGLE_DEG(20));
}

static int write_ppm(const char *path, const br_pixelmap *pm)
{
    FILE *f = fopen(path, "wb");
    int x, y;
    if (f == NULL) return -1;
    fprintf(f, "P6\n%d %d\n255\n", W, H);
    for (y = 0; y < H; y++) {
        const unsigned char *row = (const unsigned char *)pm->pixels + (long)y * pm->row_bytes;
        for (x = 0; x < W; x++) { /* RGB_888 is stored B, G, R */
            unsigned char rgb[3] = {row[x * 3 + 2], row[x * 3 + 1], row[x * 3]};
            fwrite(rgb, 1, 3, f);
        }
    }
    return fclose(f) == 0 ? 0 : -1;
}

static int begin(int vulkan, br_pixelmap **colour, br_pixelmap **depth, char *device, size_t len)
{
    br_pixelmap *screen = NULL;
    struct br_primitive_library *plib = NULL;
    if (BrBegin() != BRE_OK) return -1;
    if (BrDevAddStatic(NULL, BrDrv1SoftPrimBegin, NULL) != BRE_OK || BrDevAddStatic(NULL, BrDrv1SoftRendBegin, NULL) != BRE_OK
        || BrDevAddStatic(NULL, BrDrv1SDL3Begin, NULL) != BRE_OK)
        return -1;
    if (BrDevBeginVar(&screen, "SDL3", BRT_WIDTH_I32, W, BRT_HEIGHT_I32, H, BR_NULL_TOKEN) != BRE_OK) return -1;
    *colour = BrPixelmapMatchTyped(screen, BR_PMMATCH_OFFSCREEN, BR_PMT_RGB_888);
    *depth = *colour ? BrPixelmapMatch(*colour, BR_PMMATCH_DEPTH_16) : NULL;
    if (*colour == NULL || *depth == NULL) return -1;
    if (vulkan) {
        if (BrPrimitiveLibraryFind(&plib, NULL, BR_SCALAR_TOKEN) != BRE_OK || plib == NULL) return -1;
        if (VkPrimBegin(W, H, device, len) != 0 || (plib = VkPrimWrap(plib)) == NULL) return -1;
        VkPrimTarget(*colour, *depth);
    }
    BrRendererBegin(*colour, NULL, plib, primitive_heap, sizeof(primitive_heap));
    (*colour)->origin_x = (*depth)->origin_x = W / 2;
    (*colour)->origin_y = (*depth)->origin_y = H / 2;
    return 0;
}

int main(int argc, char **argv)
{
    const char *dat = argc > 1 ? argv[1] : ".", *out = argc > 2 ? argv[2] : ".";
    int vulkan = argc > 3 && strcmp(argv[3], "vulkan") == 0, i, failed = 0;
    char path[1024], device[256] = "softprim";
    br_pixelmap *colour, *depth;
    br_actor *world, *camera_actor, *light_actor;
    br_camera *camera;
    if (begin(vulkan, &colour, &depth, device, sizeof(device)) != 0) {
        fprintf(stderr, "vk-scenes: setup failed\n");
        return 3;
    }
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
    BrMatrix34PostRotateX(&light_actor->t.t.mat, BR_ANGLE_DEG(-35));
    for (i = 0; i < (int)(sizeof(scenes) / sizeof(scenes[0])); i++) {
        const scene *sc = &scenes[i];
        br_actor *actor = BrActorAdd(world, BrActorAllocate(BR_ACTOR_MODEL, NULL));
        br_material *material = BrMaterialAllocate(sc->name);
        br_model *model;
        snprintf(path, sizeof(path), "%s/%s", dat, sc->model);
        if ((model = BrModelLoad(path)) == NULL) { failed++; continue; }
        place(actor, model, sc->angle);
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
        BrRendererFrameBegin();
        BrPixelmapFill(colour, 0);
        BrPixelmapFill(depth, 0xFFFFFFFF);
        BrZbSceneRender(world, camera_actor, colour, depth);
        BrRendererFrameEnd();
        snprintf(path, sizeof(path), "%s/%s.ppm", out, sc->name);
        failed += write_ppm(path, colour) != 0;
        {
            unsigned long vk = 0, sw = 0;
            if (vulkan) VkPrimCounts(&vk, &sw);
            printf("{\"scene\":\"%s\",\"rasteriser\":\"%s\",\"vulkan_triangles\":%lu,\"software_triangles\":%lu}\n", sc->name, device, vk, sw);
        }
        BrActorRemove(actor);
    }
    if (vulkan) VkPrimEnd();
    return failed ? 11 : 0;
}
