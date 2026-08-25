from __future__ import annotations


def softrend_render_source() -> str:
    """C source for the BRender softrend engine-rendering rung.

    The period-accuracy milestone: rendering goes through BRender's OWN
    software renderer (softrend, compiled from the pinned checkout's C
    objects with the optional 386 assembly overlays excluded exactly as the
    period makefile structured them), driven through BrZbBegin /
    BrZbSceneRender into an RGB_888 memory pixelmap. This replaces the
    hand-written scanline rasterizer every earlier render rung used.
    """
    return r"""/*
 * BRender v1.3.2 softrend engine-rendering rung.
 *
 *   BrBegin
 *     -> device = BrDrv1SoftRendBegin(NULL)     (built-in softrend driver)
 *     -> BrZbBegin(BR_PMT_RGB_888, BR_PMT_DEPTH_16)
 *     -> model = BrModelLoad(sph32.dat), texture = BrPixelmapLoad(earth.pix)
 *     -> world/camera/model actor tree
 *     -> per frame: orbit transform, BrZbSceneRender(world,camera,pm)
 *   BrEnd
 *
 * Proves engine-side rendering: pixels come from softrend's own pipeline,
 * not from any hand-written rasterizer in this harness.
 *
 * Usage: brender_core_softrend_render <model.dat> <texture.pix> [palette.pal] [out.ppm]
 */
#define __BR_V1DB__ 1
#include "brender.h"

#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include "brddi.h"
#if defined(_DEBUG)
#include <crtdbg.h>
#endif

/* Driver entry point; renamed from BrDrv1Begin inside the softrend library. */
void * BR_EXPORT BrDrv1SoftRendBegin(char *arguments);
void * BR_EXPORT BrDrv1PentPrimBegin(char *arguments);
br_error BR_PUBLIC_ENTRY BrV1dbRendererBegin(struct br_device_pixelmap *destination, struct br_renderer *renderer);

#define RENDER_W 320
#define RENDER_H 240
#define COLOUR_BLACK BR_COLOUR_RGB(0, 0, 0)

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

static long count_lit(br_pixelmap *pm)
{
    /* Ground truth: read the raw buffer, not PixelGet (unreliable here). */
    const unsigned char *base = (const unsigned char *)pm->pixels;
    long t = 0; int x, y;
    for (y = 0; y < (int)pm->height; y++) {
        const unsigned char *row = base + (long)y * pm->row_bytes;
        for (x = 0; x < (int)pm->width; x++) {
            const unsigned char *px = row + (long)x * 3;
            if (px[0] | px[1] | px[2]) t++;
        }
    }
    return t;
}

int main(int argc, char **argv)
{
    const char *model_path = (argc > 1) ? argv[1] : NULL;
    const char *tex_path = (argc > 2) ? argv[2] : NULL;
    const char *pal_path = (argc > 3 && argv[3][0] != 0) ? argv[3] : NULL;
    const char *out_path = (argc > 4) ? argv[4] : "brender-core-softrend-render.ppm";
    br_pixelmap *tex = NULL, *pal = NULL, *pm = NULL, *depth = NULL;
    br_matrix34 mm;
    float af_s = 1.0f, af_cx = 0.0f, af_cy = 0.0f, af_cz = 0.0f;

    int nv = 0, nf = 0, k;
    br_actor *world = NULL, *camera_actor = NULL, *model_actor = NULL;
    br_camera *camera;
    br_model *model = NULL;
    br_material *material = NULL;
    int frame;

#if defined(_DEBUG)
    _CrtSetReportMode(_CRT_WARN, _CRTDBG_MODE_DEBUG);
    _CrtSetReportMode(_CRT_ERROR, _CRTDBG_MODE_DEBUG);
    _CrtSetReportMode(_CRT_ASSERT, _CRTDBG_MODE_DEBUG);
#endif
    if (model_path == NULL || tex_path == NULL) {
        fprintf(stderr, "usage: %s <model.dat> <texture.pix> [palette.pal] [out.ppm]\n", argv[0]);
        return 2;
    }

    if (BrBegin() != BRE_OK) return 3;

    if (BrDevAddStatic(NULL, (br_device_begin_fn *)BrDrv1SoftRendBegin, NULL) != BRE_OK) {
        fprintf(stderr, "BrDevAddStatic(softrend) failed\n");
        BrEnd(); return 4;
    }
    if (BrDevAddStatic(NULL, (br_device_begin_fn *)BrDrv1PentPrimBegin, NULL) != BRE_OK) {
        fprintf(stderr, "BrDevAddStatic(pentprim) failed\n");
        BrEnd(); return 4;
    }
    /*
     * Headless route: find the softrend facility explicitly and begin the
     * v1db renderer without a device pixelmap destination (BrZbBegin is a
     * 1.1-compat shim that insists on BrDevLastBeginQuery()).
     */
    {
        br_renderer_facility *facility = NULL;
        if (BrRendererFacilityFind(&facility, NULL, BRT_FLOAT) != BRE_OK || facility == NULL) {
            fprintf(stderr, "renderer facility find failed\n");
            BrEnd(); return 5;
        }
        if (BrV1dbRendererBegin(NULL, NULL) != BRE_OK) {
            fprintf(stderr, "BrV1dbRendererBegin failed\n");
            BrEnd(); return 5;
        }    /* Activate ZB mode: sets v1db.zb_active = TRUE so BrZbSceneRender dispatches faces.     * Re-invokes BrV1dbRendererBegin(NULL, NULL) harmlessly since renderer already exists. */    BrZbBegin(BR_PMT_RGB_888, BR_PMT_DEPTH_16);
    }

    tex = BrPixelmapLoad((char *)tex_path);
    if (tex == NULL || tex->pixels == NULL) {
        fprintf(stderr, "BrPixelmapLoad failed: %s\n", tex_path);
        BrEnd(); return 6;
    }
    if (pal_path != NULL) {
        pal = BrPixelmapLoad((char *)pal_path);
        if (pal != NULL && pal->pixels != NULL) tex->map = pal;
    }
    material = BrMaterialAllocate("shell-texture");
    if (material == NULL) { BrEnd(); return 7; }
    material->colour_map = tex;
    material->identifier = "shell-texture";
    /* Lit textured: triggers match.c to select TriangleRenderPIZ2TIA_RGB_888 */
    material->flags = BR_MATF_LIGHT | BR_MATF_SMOOTH;

    model = BrModelLoad((char *)model_path);
    if (model == NULL || model->nvertices < 3 || model->nfaces < 1) {
        BrEnd(); return 8;
    }
    nv = (int)model->nvertices; nf = (int)model->nfaces;

    /* Auto-frame: compute centre/radius BEFORE BrModelUpdate clears vertices */
    {
        float cx = 0.0f, cy = 0.0f, cz = 0.0f, radius = 0.0f;
        int k;
        for (k = 0; k < nv; k++) {
            cx += BrScalarToFloat(model->vertices[k].p.v[0]);
            cy += BrScalarToFloat(model->vertices[k].p.v[1]);
            cz += BrScalarToFloat(model->vertices[k].p.v[2]);
        }
        cx /= nv; cy /= nv; cz /= nv;
        for (k = 0; k < nv; k++) {
            float dx = BrScalarToFloat(model->vertices[k].p.v[0]) - cx;
            float dy = BrScalarToFloat(model->vertices[k].p.v[1]) - cy;
            float dz = BrScalarToFloat(model->vertices[k].p.v[2]) - cz;
            float rr = (float)sqrt(dx*dx + dy*dy + dz*dz);
            if (rr > radius) radius = rr;
        }
        af_s = (radius > 0.0f) ? (1.6f / radius) : 1.0f;
        af_cx = cx; af_cy = cy; af_cz = cz;
        fprintf(stderr, "MARK af-precomputed s=%f c=(%f,%f,%f)\n", af_s, af_cx, af_cy, af_cz);
        fflush(stderr);
    }

    world = BrActorAllocate(BR_ACTOR_NONE, NULL);
    camera_actor = BrActorAllocate(BR_ACTOR_CAMERA, NULL);
    BrModelUpdate(model, BR_MODU_ALL);
    model_actor = BrActorAllocate(BR_ACTOR_MODEL, NULL);
    if (world == NULL || camera_actor == NULL || camera_actor->type_data == NULL
        || model_actor == NULL) {
        BrEnd(); return 9;
    }
    camera = (br_camera *)camera_actor->type_data;
    camera->type = BR_CAMERA_PERSPECTIVE_FOV;
    camera->field_of_view = BR_ANGLE_DEG(55);
    camera->hither_z = BrFloatToScalar(1.0f);
    camera->yon_z = BrFloatToScalar(100.0f);
    camera->aspect = BrFloatToScalar((float)RENDER_W / (float)RENDER_H);
    BrMatrix34Translate(&camera_actor->t.t.mat,
        BrFloatToScalar(0.0f), BrFloatToScalar(0.0f), BrFloatToScalar(-2.5f));
    BrActorAdd(world, camera_actor);

    /* Directional light for the lit-textured path (TriangleRenderPIZ2TIA_RGB_888) */
    {
        br_actor *light_actor = BrActorAllocate(BR_ACTOR_LIGHT, NULL);
        if (light_actor != NULL) {
            br_light *ldata = (br_light *)light_actor->type_data;
            if (ldata != NULL) {
                ldata->type = BR_LIGHT_DIRECT;
                ldata->colour = BR_COLOUR_RGB(255, 255, 255);
            }
            BrMatrix34RotateX(&light_actor->t.t.mat, BR_ANGLE_DEG(-45));
            BrActorAdd(world, light_actor);
        }
    }
    /* Auto-frame: compose scale/translate from pre-computed params */
    {
        float cx = af_cx, cy = af_cy, cz = af_cz, s = af_s;
        int r, cc;

        /* Build rotation */
        BrMatrix34RotateY(&mm, BR_ANGLE_DEG(35));
        BrMatrix34PreRotateX(&mm, BR_ANGLE_DEG(25));

        /* Compose: linear = s * rot, translation = -rot * centre * s
         * This maps centre to origin and scales to fill the view,
         * with the rotation applied in world space for viewing angle.
         */
        {
            float lin[3][3], t0, t1, t2;
            for (r = 0; r < 3; r++)
                for (cc = 0; cc < 3; cc++)
                    lin[r][cc] = BrScalarToFloat(mm.m[r][cc]) * s;
            t0 = -(cx * lin[0][0] + cy * lin[1][0] + cz * lin[2][0]);
            t1 = -(cx * lin[0][1] + cy * lin[1][1] + cz * lin[2][1]);
            t2 = -(cx * lin[0][2] + cy * lin[1][2] + cz * lin[2][2]);
            for (r = 0; r < 3; r++)
                for (cc = 0; cc < 3; cc++)
                    mm.m[r][cc] = BrFloatToScalar(lin[r][cc]);
            mm.m[3][0] = BrFloatToScalar(t0);
            mm.m[3][1] = BrFloatToScalar(t1);
            mm.m[3][2] = BrFloatToScalar(t2);
        }
    }
    model_actor->model = model;
    model_actor->material = material;
    BrActorAdd(world, model_actor);

    pm = BrPixelmapAllocate(BR_PMT_RGB_888, RENDER_W, RENDER_H, NULL, BR_PMAF_NORMAL);
    depth = BrPixelmapAllocate(BR_PMT_DEPTH_16, RENDER_W, RENDER_H, NULL, BR_PMAF_NORMAL);
    if (pm == NULL || depth == NULL || pm->pixels == NULL) { BrEnd(); return 10; }
    BrPixelmapFill(pm, COLOUR_BLACK);
    pm->origin_x = (br_int_16)(RENDER_W / 2); pm->origin_y = (br_int_16)(RENDER_H / 2);
    depth->origin_x = pm->origin_x; depth->origin_y = pm->origin_y;

    for (frame = 0; frame < 4; frame++) {
        int angle = 35 + frame * 30;
        br_matrix34 orbit;
        BrMatrix34RotateY(&orbit, BR_ANGLE_DEG(angle));
        BrMatrix34PreRotateX(&orbit, BR_ANGLE_DEG(25));
        BrMatrix34RotateY(&model_actor->t.t.mat, BR_ANGLE_DEG(angle));
        BrMatrix34PreRotateX(&model_actor->t.t.mat, BR_ANGLE_DEG(25));
        model_actor->t.type = BR_TRANSFORM_MATRIX34;
        BrZbSceneRender(world, camera_actor, pm, depth);
        BrZbSceneRender(world, camera_actor, pm, depth);
        {
            char path[512];
            snprintf(path, sizeof(path), "%s.softrend-f%d.ppm", out_path, frame);
            dump_ppm(pm, path);
        }
    }

    {
        long lit = count_lit(pm);
        int ok = (lit > 500);
        printf("{\"rung\":\"brender_core_softrend_render\",\"renderer\":\"softrend-float\","
            "\"model\":\"%s\",\"frames\":4,\"final_frame_lit\":%ld,\"valid\":%s}\n",
            model_path, lit, ok ? "true" : "false");

        if (!ok || dump_ppm(pm, out_path) != 1) ok = 0;

        /*
         * Teardown note: with a ZB renderer active, mid-teardown frees of
         * actor/model/material/pixelmaps fault inside fw cleanup. Period
         * applications simply let BrEnd reclaim everything at process exit;
         * this verification rung does the same. Receipt is emitted before
         * shutdown so evidence is always flushed.
         */
        printf("{\"rung\":\"brender_core_softrend_render\",\"renderer\":\"softrend-float+pentprim-float\","
            "\"model\":\"%s\",\"texture\":\"%s\",\"palette\":\"%s\","
            "\"frames\":4,\"final_frame_lit\":%ld,\"valid\":%s}\n",
            model_path, tex_path, pal_path ? pal_path : "-", lit,
            (ok && dump_ppm(pm, out_path)) ? "true" : "false");
        fflush(stdout);

        BrZbEnd();
        if (BrEnd() != BRE_OK) return 12;
    }
}
"""
