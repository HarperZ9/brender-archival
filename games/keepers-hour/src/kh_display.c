/* The Keeper's Hour: pixel size, field of view and vsync. See kh_display.h.
 * SPDX-License-Identifier: MIT */
#include <stdlib.h>

#include <SDL3/SDL.h>
#include "kh_display.h"

static struct {
    int          pixel_override, fov_override;
    int          vsync_set;      /* 0 not set yet, 1 off, 2 on */
    br_pixelmap *colour, *depth; /* the small buffers, or NULL at pixel size 1 */
    int          k;              /* the pixel size the small buffers were made for */
    br_int_32    for_w, for_h;   /* the window buffer size they were made for */
} D;

static int env_int(const char *name, int lo, int hi)
{
    const char *v = SDL_getenv(name);
    int n;
    if (v == NULL)
        return 0;
    n = atoi(v);
    return n >= lo && n <= hi ? n : 0;
}

void kh_display_init(void)
{
    D.pixel_override = env_int("KEEPERS_PIXEL", KH_PIXEL_MIN, KH_PIXEL_MAX);
    D.fov_override = env_int("KEEPERS_FOV", KH_FOV_MIN, KH_FOV_MAX);
}

int kh_display_pixel(int option) { return D.pixel_override ? D.pixel_override : SDL_clamp(option, KH_PIXEL_MIN, KH_PIXEL_MAX); }
int kh_display_fov(int option) { return D.fov_override ? D.fov_override : SDL_clamp(option, KH_FOV_MIN, KH_FOV_MAX); }

void kh_display_apply(br_demo *demo, int fov_option, int vsync_option)
{
    br_camera *c;
    if (demo->camera != NULL) {
        c = demo->camera->type_data;
        c->field_of_view = BR_ANGLE_DEG(kh_display_fov(fov_option));
    }
    /* the software path presents through SDL surfaces and has no swap interval;
     * the interval is set only when it changes, since this runs on every event */
    if (demo->hw_accel && D.vsync_set != (vsync_option ? 2 : 1)) {
        SDL_GL_SetSwapInterval(vsync_option ? 1 : 0);
        D.vsync_set = vsync_option ? 2 : 1;
    }
}

void kh_display_release(void)
{
    if (D.depth) BrPixelmapFree(D.depth);
    if (D.colour) BrPixelmapFree(D.colour);
    D.colour = D.depth = NULL;
    D.k = 0;
}

/* Make the small buffers for pixel size k, or keep the ones that fit. */
static int small_buffers(br_pixelmap *full, int k)
{
    br_int_32 w = full->width / k, h = full->height / k;
    if (D.colour && D.k == k && D.for_w == full->width && D.for_h == full->height)
        return 0;
    kh_display_release();
    if (w < 1 || h < 1)
        return -1;
    D.colour = BrPixelmapMatchSized(full, BR_PMMATCH_OFFSCREEN, w, h);
    D.depth = D.colour ? BrPixelmapMatch(D.colour, BR_PMMATCH_DEPTH_16) : NULL;
    if (D.colour == NULL || D.depth == NULL) {
        BrLogError("KEEPER", "could not make a %dx%d buffer for pixel size %d; drawing at full size", (int)w, (int)h, k);
        kh_display_release();
        return -1;
    }
    D.colour->origin_x = (br_int_16)(w / 2);
    D.colour->origin_y = (br_int_16)(h / 2);
    D.k = k;
    D.for_w = full->width;
    D.for_h = full->height;
    return 0;
}

void kh_display_render(br_demo *demo, int pixel_option)
{
    br_pixelmap *full = demo->colour_buffer, *lo;
    int k = kh_display_pixel(pixel_option);
    if (k == 1 || small_buffers(full, k) != 0) {
        BrDemoDefaultRender(demo);
        return;
    }
    lo = D.colour;
    BrRendererFrameBegin();
    BrPixelmapFill(lo, demo->clear_colour);
    BrPixelmapFill(D.depth, 0xFFFFFFFF);
    if (demo->camera != NULL)
        BrZbSceneRender(demo->world, demo->camera, lo, D.depth);
    BrRendererFrameEnd();
    /* whole pixels: the small buffer times k, centred; any remainder strip
     * (a window size not divisible by k) is filled with the sky colour */
    BrPixelmapFill(full, demo->clear_colour);
    BrPixelmapRectangleStretchCopy(full, -full->origin_x + (full->width - lo->width * k) / 2,
                                   -full->origin_y + (full->height - lo->height * k) / 2, lo->width * k, lo->height * k, lo,
                                   -lo->origin_x, -lo->origin_y, lo->width, lo->height);
}
