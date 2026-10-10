/*
 * SPDX-License-Identifier: MIT
 * Renderer rung for BRender 1.4 (BlazingRenderer), 64-bit.
 *
 * The period rung (brender-core-softrend-render.c) binds pentprim through the
 * 1.3.2 renderer entry points. BRender 1.4 replaces pentprim with softprim and
 * changes how a renderer is begun, so this program states the same claim
 * through the 1.4 API: softrend and softprim render a loaded, textured .dat
 * model over an eight-frame orbit, and the final frame has more than 500 lit
 * pixels and more than 500 coloured (textured, not grey) pixels.
 *
 *   BrBegin -> BrDevAddStatic(softprim, softrend)
 *   -> BrRendererBegin(colour, NULL, NULL, heap)
 *   -> per frame: BrRendererFrameBegin, BrZbSceneRender, BrRendererFrameEnd
 *   -> BrRendererEnd -> BrEnd
 *
 * Usage: brender_core_softrend_render <model.dat> <texture.pix> [palette.pal] [out.ppm]
 */
#include "brender.h"
#include "brddi.h"
#include "brsdl3dev.h"
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

struct br_device *BR_EXPORT BrDrv1SoftPrimBegin(const char *arguments);
struct br_device *BR_EXPORT BrDrv1SoftRendBegin(const char *arguments);

#define RENDER_W 320
#define RENDER_H 240

static char primitive_heap[1500 * 1024];

static long count_lit(const br_pixelmap *pm)
{
    long total = 0;
    int x, y;
    for (y = 0; y < (int)pm->height; y++) {
        const unsigned char *row = (const unsigned char *)pm->pixels + (long)y * pm->row_bytes;
        for (x = 0; x < (int)pm->width; x++) {
            const unsigned char *px = row + (long)x * 3;
            if (px[0] | px[1] | px[2]) total++;
        }
    }
    return total;
}

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

/* Centre and radius are read before BrModelUpdate, which may release the
 * vertex array once the model is prepared for rendering. */
static void model_bounds(const br_model *model, float centre[3], float *scale)
{
    float radius = 0;
    int k, nv = (int)model->nvertices;
    centre[0] = centre[1] = centre[2] = 0;
    for (k = 0; k < nv; k++) {
        centre[0] += BrScalarToFloat(model->vertices[k].p.v[0]);
        centre[1] += BrScalarToFloat(model->vertices[k].p.v[1]);
        centre[2] += BrScalarToFloat(model->vertices[k].p.v[2]);
    }
    centre[0] /= nv; centre[1] /= nv; centre[2] /= nv;
    for (k = 0; k < nv; k++) {
        float dx = BrScalarToFloat(model->vertices[k].p.v[0]) - centre[0];
        float dy = BrScalarToFloat(model->vertices[k].p.v[1]) - centre[1];
        float dz = BrScalarToFloat(model->vertices[k].p.v[2]) - centre[2];
        float rr = (float)sqrt(dx * dx + dy * dy + dz * dz);
        if (rr > radius) radius = rr;
    }
    *scale = radius > 0 ? 1.0f / radius : 1.0f;
}

/* Expand an indexed period texture through its palette into RGB_888, the
 * format the true-colour softprim rasterisers sample. */
static br_pixelmap *expand_texture(br_pixelmap *tex, br_pixelmap *pal)
{
    br_pixelmap *rgb;
    int x, y;
    if (tex->type != BR_PMT_INDEX_8 || pal == NULL) return tex;
    rgb = BrPixelmapAllocate(BR_PMT_RGB_888, tex->width, tex->height, NULL, BR_PMAF_NORMAL);
    if (rgb == NULL) return NULL;
    for (y = 0; y < (int)tex->height; y++) {
        const unsigned char *src = (const unsigned char *)tex->pixels + (long)y * tex->row_bytes;
        unsigned char *dst = (unsigned char *)rgb->pixels + (long)y * rgb->row_bytes;
        for (x = 0; x < (int)tex->width; x++) {
            const unsigned char *entry = (const unsigned char *)pal->pixels + (long)src[x] * pal->row_bytes;
            dst[x * 3 + 0] = entry[0]; dst[x * 3 + 1] = entry[1]; dst[x * 3 + 2] = entry[2];
        }
    }
    return rgb;
}

/* Pixels whose channels differ by more than 24: zero for a grey, untextured
 * render, many for the blue and green of the earth texture. */
static long count_chroma(const br_pixelmap *pm)
{
    long total = 0;
    int x, y;
    for (y = 0; y < (int)pm->height; y++) {
        const unsigned char *row = (const unsigned char *)pm->pixels + (long)y * pm->row_bytes;
        for (x = 0; x < (int)pm->width; x++) {
            int b = row[x * 3], g = row[x * 3 + 1], r = row[x * 3 + 2];
            int hi = r > g ? (r > b ? r : b) : (g > b ? g : b);
            int lo = r < g ? (r < b ? r : b) : (g < b ? g : b);
            if (hi - lo > 24) total++;
        }
    }
    return total;
}

static void place_model(br_actor *actor, const float centre[3], float s, int angle)
{
    br_matrix34 scale;
    actor->t.type = BR_TRANSFORM_MATRIX34;
    BrMatrix34Translate(&actor->t.t.mat, BrFloatToScalar(-centre[0]), BrFloatToScalar(-centre[1]), BrFloatToScalar(-centre[2]));
    BrMatrix34Scale(&scale, BrFloatToScalar(s), BrFloatToScalar(s), BrFloatToScalar(s));
    BrMatrix34Post(&actor->t.t.mat, &scale);
    BrMatrix34PostRotateX(&actor->t.t.mat, BR_ANGLE_DEG(25));
    BrMatrix34PostRotateY(&actor->t.t.mat, BR_ANGLE_DEG(angle));
}

int main(int argc, char **argv)
{
    const char *model_path = argc > 1 ? argv[1] : NULL;
    const char *tex_path = argc > 2 ? argv[2] : NULL;
    const char *pal_path = argc > 3 ? argv[3] : NULL;
    const char *out_path = argc > 4 ? argv[4] : "brender-core-softrend-render.ppm";
    br_pixelmap *screen = NULL, *colour, *depth, *tex, *pal;
    br_actor *world, *camera_actor, *model_actor, *light;
    br_camera *camera;
    br_material *material;
    br_model *model;
    long lit = 0, chroma = 0;
    float centre[3], fit;
    int frame, ok;

    if (model_path == NULL || tex_path == NULL) return 2;
    if (BrBegin() != BRE_OK) return 3;
    if (getenv("LADDER64_DEBUG")) BrLogSetLevel(BR_LOG_DEBUG);
    if (BrDevAddStatic(NULL, BrDrv1SoftPrimBegin, NULL) != BRE_OK) return 4;
    if (BrDevAddStatic(NULL, BrDrv1SoftRendBegin, NULL) != BRE_OK) return 4;

    /* 1.4 renders into a device pixelmap: an SDL3 screen (headless under
     * SDL_VIDEODRIVER=offscreen) and an offscreen buffer matched to it. */
    if (BrDevAddStatic(NULL, BrDrv1SDL3Begin, NULL) != BRE_OK) return 4;
    if (BrDevBeginVar(&screen, "SDL3", BRT_WIDTH_I32, RENDER_W, BRT_HEIGHT_I32, RENDER_H, BR_NULL_TOKEN) != BRE_OK) return 5;
    colour = BrPixelmapMatchTyped(screen, BR_PMMATCH_OFFSCREEN, BR_PMT_RGB_888);
    if (colour == NULL || (depth = BrPixelmapMatch(colour, BR_PMMATCH_DEPTH_16)) == NULL) return 5;
    colour->origin_x = depth->origin_x = RENDER_W / 2;
    colour->origin_y = depth->origin_y = RENDER_H / 2;
    BrRendererBegin(colour, NULL, NULL, primitive_heap, sizeof(primitive_heap));

    if ((tex = BrPixelmapLoad((char *)tex_path)) == NULL) return 6;
    pal = pal_path != NULL ? BrPixelmapLoad((char *)pal_path) : NULL;
    if ((tex = expand_texture(tex, pal != NULL ? pal : tex->map)) == NULL) return 6;
    tex->identifier = "ladder-texture";
    BrMapAdd(tex);
    if ((material = BrMaterialAllocate("ladder-texture")) == NULL) return 7;
    material->colour_map = tex;
    material->flags = BR_MATF_LIGHT | BR_MATF_SMOOTH;
    if ((model = BrModelLoad((char *)model_path)) == NULL || model->nvertices < 3) return 8;
    model_bounds(model, centre, &fit);

    world = BrActorAllocate(BR_ACTOR_NONE, NULL);
    camera_actor = BrActorAdd(world, BrActorAllocate(BR_ACTOR_CAMERA, NULL));
    model_actor = BrActorAdd(world, BrActorAllocate(BR_ACTOR_MODEL, NULL));
    light = BrActorAdd(world, BrActorAllocate(BR_ACTOR_LIGHT, NULL));
    if (world == NULL || camera_actor == NULL || model_actor == NULL || light == NULL) return 9;
    camera = (br_camera *)camera_actor->type_data;
    camera->type = BR_CAMERA_PERSPECTIVE_FOV;
    camera->field_of_view = BR_ANGLE_DEG(55);
    camera->hither_z = BrFloatToScalar(0.5f);
    camera->yon_z = BrFloatToScalar(100.0f);
    camera->aspect = BrFloatToScalar((float)RENDER_W / (float)RENDER_H);
    camera_actor->t.type = BR_TRANSFORM_MATRIX34;
    BrMatrix34Translate(&camera_actor->t.t.mat, 0, 0, BrFloatToScalar(2.5f));
    BrLightEnable(light);

    model_actor->model = model;
    model_actor->material = material;
    BrMapUpdate(tex, BR_MAPU_ALL);
    BrMaterialUpdate(material, BR_MATU_ALL);
    BrModelUpdate(model, BR_MODU_ALL);

    for (frame = 0; frame < 8; frame++) {
        char path[512];
        place_model(model_actor, centre, fit, 35 + frame * 45);
        BrRendererFrameBegin();
        BrPixelmapFill(colour, 0);
        BrPixelmapFill(depth, 0xFFFFFFFF);
        BrZbSceneRender(world, camera_actor, colour, depth);
        BrRendererFrameEnd();
        snprintf(path, sizeof(path), "%s.softrend-f%d.ppm", out_path, frame);
        dump_ppm(colour, path);
    }
    lit = count_lit(colour);
    chroma = count_chroma(colour);
    ok = lit > 500 && chroma > 500 && dump_ppm(colour, out_path);
    printf("{\"rung\":\"brender_core_softrend_render\",\"renderer\":\"softrend+softprim (BRender 1.4)\","
           "\"frames\":8,\"final_frame_lit\":%ld,\"final_frame_textured\":%ld,\"valid\":%s}\n",
           lit, chroma, ok ? "true" : "false");
    fflush(stdout);
    BrRendererEnd();
    BrEnd();
    return ok ? 0 : 11;
}
