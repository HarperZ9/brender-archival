/* brview scenes: the period sample models and how to frame them.
 * The .dat, .pix and .pal files are BRender v1.3.2 samples (MIT, copyright
 * 1998 Argonaut Software Limited), shipped beside the program in dat/.
 * SPDX-License-Identifier: MIT */
#include <math.h>
#include <stdio.h>
#include <string.h>

#include <SDL3/SDL.h>
#include "brview_scenes.h"

typedef struct scene {
    const char   *name;
    const char   *model;
    const char   *texture; /* NULL: plain colour */
    unsigned char r, g, b;
} scene;

static scene scenes[] = {
    {"Earth (sph32.dat, earth.pix)", "sph32.dat", "earth.pix", 255, 255, 255},
    {"Utah teapot (teapot.dat)", "teapot.dat", NULL, 214, 168, 72},
    {"Skull (skull.dat)", "skull.dat", NULL, 226, 214, 188},
    {"Argonaut logo (argo.dat)", "argo.dat", NULL, 120, 170, 230},
    {"Spaceship (ship.dat)", "ship.dat", NULL, 170, 176, 190},
    {"Duck (duck.dat)", "duck.dat", NULL, 236, 196, 40},
    {"Torus (torus.dat, rosewood.pix)", "torus.dat", "rosewood.pix", 255, 255, 255},
    {"Terrain (terrain.dat)", "terrain.dat", NULL, 96, 150, 80},
};
#define SCENE_COUNT ((int)BR_ASIZE(scenes))

static scene custom;
static int   has_custom;

int BrViewSceneCount(void) { return SCENE_COUNT + has_custom; }

static const scene *get_scene(int index)
{
    if (has_custom)
        return index == 0 ? &custom : &scenes[index - 1];
    return &scenes[index];
}

const char *BrViewSceneName(int index) { return get_scene(index)->name; }

void BrViewSceneSetCustom(const char *model_path, const char *texture_path)
{
    custom = (scene){model_path, model_path, texture_path, 220, 220, 220};
    has_custom = 1;
}

/* Bundled files live in dat/ beside the program; a path with a slash is used as given. */
static void resolve(const char *name, char *out, size_t len)
{
    if (strchr(name, '/') || strchr(name, '\\') || strchr(name, ':'))
        snprintf(out, len, "%s", name);
    else
        snprintf(out, len, "%sdat/%s", SDL_GetBasePath(), name);
}

/* Expand an indexed period texture through a palette into RGB_888. */
static br_pixelmap *load_texture(const char *name)
{
    char path[1024];
    br_pixelmap *tex, *pal, *rgb;
    int x, y;
    resolve(name, path, sizeof(path));
    if ((tex = BrPixelmapLoad(path)) == NULL)
        return NULL;
    if (tex->type != BR_PMT_INDEX_8)
        return tex;
    pal = tex->map;
    if (pal == NULL) {
        resolve("std.pal", path, sizeof(path));
        pal = BrPixelmapLoad(path);
    }
    if (pal == NULL || (rgb = BrPixelmapAllocate(BR_PMT_RGB_888, tex->width, tex->height, NULL, BR_PMAF_NORMAL)) == NULL)
        return tex;
    for (y = 0; y < (int)tex->height; y++) {
        const unsigned char *src = (const unsigned char *)tex->pixels + (long)y * tex->row_bytes;
        unsigned char *dst = (unsigned char *)rgb->pixels + (long)y * rgb->row_bytes;
        for (x = 0; x < (int)tex->width; x++) {
            const unsigned char *e = (const unsigned char *)pal->pixels + (long)src[x] * pal->row_bytes;
            dst[x * 3] = e[0]; dst[x * 3 + 1] = e[1]; dst[x * 3 + 2] = e[2];
        }
    }
    rgb->identifier = BrResStrDup(rgb, name);
    return rgb;
}

/* Centre and radius over every model, read before the models are prepared. */
static void bounds(br_model **models, int n, br_vector3 *centre, float *radius)
{
    float lo[3] = {1e30f, 1e30f, 1e30f}, hi[3] = {-1e30f, -1e30f, -1e30f}, r = 0;
    int i, k, a;
    for (i = 0; i < n; i++)
        for (k = 0; k < (int)models[i]->nvertices; k++)
            for (a = 0; a < 3; a++) {
                float v = BrScalarToFloat(models[i]->vertices[k].p.v[a]);
                lo[a] = v < lo[a] ? v : lo[a];
                hi[a] = v > hi[a] ? v : hi[a];
            }
    for (a = 0; a < 3; a++)
        centre->v[a] = BR_SCALAR((lo[a] + hi[a]) * 0.5f);
    for (i = 0; i < n; i++)
        for (k = 0; k < (int)models[i]->nvertices; k++) {
            float dx = BrScalarToFloat(models[i]->vertices[k].p.v[0]) - BrScalarToFloat(centre->v[0]);
            float dy = BrScalarToFloat(models[i]->vertices[k].p.v[1]) - BrScalarToFloat(centre->v[1]);
            float dz = BrScalarToFloat(models[i]->vertices[k].p.v[2]) - BrScalarToFloat(centre->v[2]);
            float d = sqrtf(dx * dx + dy * dy + dz * dz);
            r = d > r ? d : r;
        }
    *radius = r > 0 ? r : 1.0f;
}

static void set_material(br_material *material, const scene *s, br_boolean textured)
{
    br_pixelmap *tex = (textured && s->texture) ? load_texture(s->texture) : NULL;
    if (tex != NULL)
        BrMapAdd(tex);
    material->colour_map = tex;
    material->colour = BR_COLOUR_RGB(s->r, s->g, s->b);
    material->flags = BR_MATF_LIGHT | BR_MATF_SMOOTH | BR_MATF_PERSPECTIVE;
    material->ka = BR_UFRACTION(0.25);
    material->kd = BR_UFRACTION(0.75);
    material->ks = BR_UFRACTION(0.35);
    material->power = BR_SCALAR(24);
    BrMaterialUpdate(material, BR_MATU_ALL);
}

br_error BrViewSceneLoad(int index, br_actor *parent, br_material *material, br_boolean textured, char *err, size_t err_len)
{
    const scene *s = get_scene(index);
    br_model *models[64];
    char path[1024];
    br_vector3 centre;
    float radius, scale;
    int i, n;

    while (parent->children != NULL)
        BrActorFree(BrActorRemove(parent->children));

    resolve(s->model, path, sizeof(path));
    if ((n = (int)BrModelLoadMany(path, models, BR_ASIZE(models))) <= 0) {
        snprintf(err, err_len, "cannot load %s", path);
        return BRE_FAIL;
    }
    bounds(models, n, &centre, &radius);
    set_material(material, s, textured);
    for (i = 0; i < n; i++) {
        br_actor *a = BrActorAdd(parent, BrActorAllocate(BR_ACTOR_MODEL, NULL));
        BrModelAdd(models[i]);
        a->model = models[i];
        a->material = material;
    }
    scale = 1.0f / radius;
    parent->t.type = BR_TRANSFORM_MATRIX34;
    BrMatrix34Translate(&parent->t.t.mat, -centre.v[0], -centre.v[1], -centre.v[2]);
    BrMatrix34PostScale(&parent->t.t.mat, BR_SCALAR(scale), BR_SCALAR(scale), BR_SCALAR(scale));
    return BRE_OK;
}
