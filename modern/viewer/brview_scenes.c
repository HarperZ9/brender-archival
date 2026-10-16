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

/* The ramps of std.pal (stdpal.txt): first index, length, and the diffuse
 * colour each one climbs through, black at its foot and white at its top. */
static const struct { int base, range, r, g, b; } ramps[] = {
    {0, 63, 147, 147, 147}, {64, 31, 60, 60, 238}, {96, 31, 60, 238, 60}, {128, 31, 60, 238, 238},
    {160, 31, 238, 60, 60}, {192, 31, 238, 60, 238}, {224, 31, 238, 238, 60},
};

/* The std.pal ramp nearest a colour's hue: grey for the pale ones. */
static int ramp_for(int r, int g, int b)
{
    float m = (float)(r > g ? (r > b ? r : b) : (g > b ? g : b)), best = 1e9f;
    int i, pick = 0;
    if (m < 1) m = 1;
    for (i = 0; i < (int)BR_ASIZE(ramps); i++) {
        float rm = (float)(ramps[i].r > ramps[i].g ? (ramps[i].r > ramps[i].b ? ramps[i].r : ramps[i].b) : (ramps[i].g > ramps[i].b ? ramps[i].g : ramps[i].b));
        float dr = r / m - ramps[i].r / rm, dg = g / m - ramps[i].g / rm, db = b / m - ramps[i].b / rm;
        float d = dr * dr + dg * dg + db * db;
        if (d < best) { best = d; pick = i; }
    }
    return pick;
}

/* shade.tab's rows run from black (0) through the map's own colours (rows
 * 28 to 36 keep the most entries unchanged) to white (63). BRender lights a
 * textured 8-bit surface across every row of its table, so full light would
 * wash the map out toward white. The table here is shade.tab's first 37
 * rows: full light lands on row 36 and a lit map keeps its colours, as it
 * does in true colour. */
#define SHADE_ROWS 37

/* An 8-bit map as stored, and shade.tab, for the period look. */
static br_pixelmap *load_texture8(const char *name)
{
    char path[1024];
    br_pixelmap *tex;
    resolve(name, path, sizeof(path));
    if ((tex = BrPixelmapLoad(path)) == NULL || tex->type != BR_PMT_INDEX_8)
        return NULL;
    tex->identifier = BrResSprintf(tex, "%s-8bit", name);
    return tex;
}

static br_pixelmap *shade_table(void)
{
    static br_pixelmap *shade;
    char path[1024];
    br_pixelmap *full;
    int y;
    if (shade == NULL) {
        resolve("shade.tab", path, sizeof(path));
        if ((full = BrPixelmapLoad(path)) == NULL || full->type != BR_PMT_INDEX_8 || full->height < SHADE_ROWS)
            return NULL;
        if ((shade = BrPixelmapAllocate(BR_PMT_INDEX_8, full->width, SHADE_ROWS, NULL, BR_PMAF_NORMAL)) != NULL) {
            for (y = 0; y < SHADE_ROWS; y++)
                memcpy((char *)shade->pixels + (long)y * shade->row_bytes, (char *)full->pixels + (long)y * full->row_bytes,
                       (size_t)full->width);
            shade->identifier = "shade.tab";
            BrTableAdd(shade);
        }
        BrPixelmapFree(full);
    }
    return shade;
}

br_pixelmap *BrViewScenePalette(void)
{
    static br_pixelmap *palette;
    char path[1024];
    if (palette == NULL) {
        resolve("std.pal", path, sizeof(path));
        palette = BrPixelmapLoad(path);
    }
    return palette;
}

static void set_material(br_material *material, const scene *s, br_boolean textured, br_boolean period)
{
    br_pixelmap *tex = NULL;
    int ramp = ramp_for(s->r, s->g, s->b);
    if (textured && s->texture)
        tex = period ? load_texture8(s->texture) : load_texture(s->texture);
    if (tex != NULL)
        BrMapAdd(tex);
    material->colour_map = tex;
    /* 8-bit: an untextured surface climbs its std.pal ramp with the light; a
     * textured one is lit through shade.tab, row by row */
    material->index_base = (br_uint_8)(tex ? 0 : ramps[ramp].base);
    material->index_range = (br_uint_8)(tex ? 63 : ramps[ramp].range);
    material->index_shade = period && tex ? shade_table() : NULL;
    material->colour = BR_COLOUR_RGB(s->r, s->g, s->b);
    material->flags = BR_MATF_LIGHT | BR_MATF_SMOOTH | BR_MATF_PERSPECTIVE;
    material->ka = BR_UFRACTION(0.25);
    material->kd = BR_UFRACTION(0.75);
    material->ks = BR_UFRACTION(0.35);
    material->power = BR_SCALAR(24);
    BrMaterialUpdate(material, BR_MATU_ALL);
}

br_error BrViewSceneLoad(int index, br_actor *parent, br_material *material, br_boolean textured, br_boolean period,
                         char *err, size_t err_len)
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
    set_material(material, s, textured, period);
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
