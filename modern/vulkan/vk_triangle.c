/*
 * SPDX-License-Identifier: MIT
 * The first drawable triangle of a Vulkan backend for BRender, and its
 * parity check against BRender 1.4's software rasteriser
 * (docs/adr/0002-vulkan-backend.md, stage A).
 *
 * Each scene is a list of flat-coloured triangles given in pixels. The same
 * triangles are drawn twice at 320 x 240:
 *   software: as one-face models under a parallel camera whose view volume
 *             is exactly the buffer, through softrend + softprim;
 *   vulkan:   by the headless rasteriser in vk_offscreen.c.
 * Usage: vk-triangle <out-dir>. Writes <out-dir>/software/<scene>.ppm and
 * <out-dir>/vulkan/<scene>.ppm, and one JSON line per scene.
 */
#include "brender.h"
#include "brddi.h"
#include "brsdl3dev.h"
#include <stdio.h>
#include <string.h>

#include "vk_offscreen.h"

#define W 320
#define H 240
#define MAX_TRIS 16

struct br_device *BR_EXPORT BrDrv1SoftPrimBegin(const char *arguments);
struct br_device *BR_EXPORT BrDrv1SoftRendBegin(const char *arguments);
static char primitive_heap[1500 * 1024];

typedef struct tri { float p[6]; unsigned char rgb[3]; } tri;
typedef struct scene { const char *name; int n; tri t[MAX_TRIS]; } scene;

/* The scenes. "triangle" is one triangle with no edge on a pixel boundary;
 * "quad" two triangles sharing a diagonal, which tests that a shared edge is
 * drawn once (no gap, no double cover); "slivers" eight thin triangles;
 * "offset" the first triangle moved by half a pixel. */
static scene scenes[] = {
    {"triangle", 1, {{{40.25f, 30.5f, 290.75f, 60.25f, 120.5f, 220.75f}, {232, 180, 92}}}},
    {"quad", 2, {{{60, 40, 260, 40, 260, 200}, {200, 170, 110}}, {{60, 40, 260, 200, 60, 200}, {80, 120, 200}}}},
    {"slivers", 0, {{{0}}}},
    {"offset", 1, {{{40.75f, 31.0f, 291.25f, 60.75f, 121.0f, 221.25f}, {232, 180, 92}}}},
};

static void make_slivers(scene *s)
{
    int i;
    s->n = 8;
    for (i = 0; i < 8; i++) {
        tri *t = &s->t[i];
        t->p[0] = 20.0f + i * 36.0f; t->p[1] = 20.0f;
        t->p[2] = 26.0f + i * 36.0f; t->p[3] = 20.0f;
        t->p[4] = 40.0f + i * 34.0f + 0.37f * i; t->p[5] = 225.0f - 3.0f * i;
        t->rgb[0] = (unsigned char)(i % 2 ? 230 : 90);
        t->rgb[1] = (unsigned char)(120 + 10 * i);
        t->rgb[2] = (unsigned char)(i % 2 ? 80 : 220);
    }
}

static int write_ppm(const char *path, const unsigned char *rgb)
{
    FILE *f = fopen(path, "wb");
    if (f == NULL) return -1;
    fprintf(f, "P6\n%d %d\n255\n", W, H);
    fwrite(rgb, 1, (size_t)W * H * 3, f);
    return fclose(f) == 0 ? 0 : -1;
}

/* One triangle as a one-face model, in world units that the parallel camera
 * maps one to one onto pixels: x right from the centre, y up. */
static br_actor *add_triangle(br_actor *world, const tri *t, int index)
{
    char name[32];
    br_actor *a = BrActorAdd(world, BrActorAllocate(BR_ACTOR_MODEL, NULL));
    br_model *m;
    br_material *mat;
    int v;
    snprintf(name, sizeof(name), "tri%d", index);
    m = BrModelAllocate(name, 3, 1);
    mat = BrMaterialAllocate(name);
    if (a == NULL || m == NULL || mat == NULL) return NULL;
    for (v = 0; v < 3; v++) {
        m->vertices[v].p.v[0] = BrFloatToScalar(t->p[2 * v] - W / 2.0f);
        m->vertices[v].p.v[1] = BrFloatToScalar(H / 2.0f - t->p[2 * v + 1]);
        m->vertices[v].p.v[2] = 0;
        m->faces[0].vertices[v] = (br_uint_16)v;
    }
    mat->colour = BR_COLOUR_RGB(t->rgb[0], t->rgb[1], t->rgb[2]);
    mat->flags = BR_MATF_TWO_SIDED;
    BrMaterialUpdate(mat, BR_MATU_ALL);
    BrModelUpdate(m, BR_MODU_ALL);
    a->model = m;
    a->material = mat;
    return a;
}

static int draw_software(br_actor *world, br_actor *camera, br_pixelmap *colour, br_pixelmap *depth, const scene *s, unsigned char *rgb)
{
    br_actor *added[MAX_TRIS];
    int i, x, y;
    for (i = 0; i < s->n; i++)
        if ((added[i] = add_triangle(world, &s->t[i], i)) == NULL) return -1;
    BrRendererFrameBegin();
    BrPixelmapFill(colour, 0);
    BrPixelmapFill(depth, 0xFFFFFFFF);
    BrZbSceneRender(world, camera, colour, depth);
    BrRendererFrameEnd();
    for (y = 0; y < H; y++) {
        const unsigned char *row = (const unsigned char *)colour->pixels + (long)y * colour->row_bytes;
        for (x = 0; x < W; x++) { /* RGB_888 is stored B, G, R */
            rgb[(y * W + x) * 3 + 0] = row[x * 3 + 2];
            rgb[(y * W + x) * 3 + 1] = row[x * 3 + 1];
            rgb[(y * W + x) * 3 + 2] = row[x * 3 + 0];
        }
    }
    for (i = 0; i < s->n; i++) BrActorRemove(added[i]);
    return 0;
}

static int draw_vulkan(vko_context *vk, const scene *s, unsigned char *rgb)
{
    vko_vertex v[MAX_TRIS * 3];
    int i, k;
    for (i = 0; i < s->n; i++)
        for (k = 0; k < 3; k++) {
            vko_vertex *o = &v[i * 3 + k];
            o->x = s->t[i].p[2 * k];
            o->y = s->t[i].p[2 * k + 1];
            o->r = s->t[i].rgb[0] / 255.0f;
            o->g = s->t[i].rgb[1] / 255.0f;
            o->b = s->t[i].rgb[2] / 255.0f;
        }
    return vko_draw(vk, v, (uint32_t)(s->n * 3), 0, 0, 0, rgb);
}

static int begin_software(br_pixelmap **colour, br_pixelmap **depth, br_actor **world, br_actor **camera_actor)
{
    br_pixelmap *screen = NULL;
    br_camera *camera;
    if (BrBegin() != BRE_OK) return -1;
    if (BrDevAddStatic(NULL, BrDrv1SoftPrimBegin, NULL) != BRE_OK || BrDevAddStatic(NULL, BrDrv1SoftRendBegin, NULL) != BRE_OK
        || BrDevAddStatic(NULL, BrDrv1SDL3Begin, NULL) != BRE_OK)
        return -1;
    if (BrDevBeginVar(&screen, "SDL3", BRT_WIDTH_I32, W, BRT_HEIGHT_I32, H, BR_NULL_TOKEN) != BRE_OK) return -1;
    *colour = BrPixelmapMatchTyped(screen, BR_PMMATCH_OFFSCREEN, BR_PMT_RGB_888);
    *depth = *colour ? BrPixelmapMatch(*colour, BR_PMMATCH_DEPTH_16) : NULL;
    if (*colour == NULL || *depth == NULL) return -1;
    BrRendererBegin(*colour, NULL, NULL, primitive_heap, sizeof(primitive_heap));
    (*colour)->origin_x = (*depth)->origin_x = W / 2;
    (*colour)->origin_y = (*depth)->origin_y = H / 2;
    *world = BrActorAllocate(BR_ACTOR_NONE, NULL);
    *camera_actor = BrActorAdd(*world, BrActorAllocate(BR_ACTOR_CAMERA, NULL));
    camera = (br_camera *)(*camera_actor)->type_data;
    camera->type = BR_CAMERA_PARALLEL;
    camera->width = BrFloatToScalar((float)W);
    camera->height = BrFloatToScalar((float)H);
    camera->aspect = BR_SCALAR(1.0);
    camera->hither_z = BrFloatToScalar(1.0f);
    camera->yon_z = BrFloatToScalar(100.0f);
    (*camera_actor)->t.type = BR_TRANSFORM_MATRIX34;
    BrMatrix34Translate(&(*camera_actor)->t.t.mat, 0, 0, BrFloatToScalar(10.0f));
    return 0;
}

int main(int argc, char **argv)
{
    static unsigned char rgb[W * H * 3];
    const char *out = argc > 1 ? argv[1] : ".";
    char path[1024], device[256] = "";
    br_pixelmap *colour, *depth;
    br_actor *world, *camera;
    vko_context *vk;
    int i, failed = 0;
    make_slivers(&scenes[2]);
    if (begin_software(&colour, &depth, &world, &camera) != 0) {
        fprintf(stderr, "vk-triangle: BRender software setup failed\n");
        return 3;
    }
    if ((vk = vko_create(W, H, device, sizeof(device))) == NULL) return 4;
    for (i = 0; i < (int)(sizeof(scenes) / sizeof(scenes[0])); i++) {
        const scene *s = &scenes[i];
        snprintf(path, sizeof(path), "%s/software/%s.ppm", out, s->name);
        failed += draw_software(world, camera, colour, depth, s, rgb) != 0 || write_ppm(path, rgb) != 0;
        snprintf(path, sizeof(path), "%s/vulkan/%s.ppm", out, s->name);
        failed += draw_vulkan(vk, s, rgb) != 0 || write_ppm(path, rgb) != 0;
        printf("{\"scene\":\"%s\",\"triangles\":%d,\"vulkan_device\":\"%s\"}\n", s->name, s->n, device);
    }
    vko_destroy(vk);
    return failed ? 11 : 0;
}
