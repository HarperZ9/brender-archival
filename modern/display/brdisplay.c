/* brdisplay: pixel size, field of view, vsync and still frames. See brdisplay.h.
 * SPDX-License-Identifier: MIT */
#include <stdio.h>
#include <stdlib.h>

#include <SDL3/SDL.h>
#include "brdisplay.h"

static struct {
    int          pixel_override, fov_override;
    int          vsync_set;      /* 0 not set yet, 1 off, 2 on */
    br_pixelmap *colour, *depth; /* the small buffers, or NULL at pixel size 1 */
    int          k;              /* the pixel size the small buffers were made for */
    br_int_32    for_w, for_h;   /* the window buffer size they were made for */
    br_pixelmap *index8, *depth8, *rgb; /* the period look: 8-bit target, its depth, its colours */
    int          k8;
    br_int_32    for_w8, for_h8;
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

void brd_display_init(const char *env_prefix)
{
    char name[64];
    SDL_snprintf(name, sizeof(name), "%s_PIXEL", env_prefix);
    D.pixel_override = env_int(name, BRD_PIXEL_MIN, BRD_PIXEL_MAX);
    SDL_snprintf(name, sizeof(name), "%s_FOV", env_prefix);
    D.fov_override = env_int(name, BRD_FOV_MIN, BRD_FOV_MAX);
}

int brd_display_pixel(int option) { return D.pixel_override ? D.pixel_override : SDL_clamp(option, BRD_PIXEL_MIN, BRD_PIXEL_MAX); }
int brd_display_fov(int option) { return D.fov_override ? D.fov_override : SDL_clamp(option, BRD_FOV_MIN, BRD_FOV_MAX); }

void brd_display_apply(br_demo *demo, int fov_option, int vsync_option)
{
    br_camera *c;
    if (demo->camera != NULL) {
        c = demo->camera->type_data;
        c->field_of_view = BR_ANGLE_DEG(brd_display_fov(fov_option));
    }
    /* the software path presents through SDL surfaces and has no swap interval;
     * the interval is set only when it changes, since this runs on every event */
    if (demo->hw_accel && D.vsync_set != (vsync_option ? 2 : 1)) {
        SDL_GL_SetSwapInterval(vsync_option ? 1 : 0);
        D.vsync_set = vsync_option ? 2 : 1;
    }
}

static void release_small(void)
{
    if (D.depth) BrPixelmapFree(D.depth);
    if (D.colour) BrPixelmapFree(D.colour);
    D.colour = D.depth = NULL;
    D.k = 0;
}

static void release_period(void)
{
    if (D.depth8) BrPixelmapFree(D.depth8);
    if (D.index8) BrPixelmapFree(D.index8);
    if (D.rgb) BrPixelmapFree(D.rgb);
    D.index8 = D.depth8 = D.rgb = NULL;
    D.k8 = 0;
}

void brd_display_release(void)
{
    release_small();
    release_period();
}

/* Make the small buffers for pixel size k, or keep the ones that fit. */
static int small_buffers(br_pixelmap *full, int k)
{
    br_int_32 w = full->width / k, h = full->height / k;
    if (D.colour && D.k == k && D.for_w == full->width && D.for_h == full->height)
        return 0;
    release_small();
    if (w < 1 || h < 1)
        return -1;
    D.colour = BrPixelmapMatchSized(full, BR_PMMATCH_OFFSCREEN, w, h);
    D.depth = D.colour ? BrPixelmapMatch(D.colour, BR_PMMATCH_DEPTH_16) : NULL;
    if (D.colour == NULL || D.depth == NULL) {
        BrLogError("KEEPER", "could not make a %dx%d buffer for pixel size %d; drawing at full size", (int)w, (int)h, k);
        release_small();
        return -1;
    }
    D.colour->origin_x = (br_int_16)(w / 2);
    D.colour->origin_y = (br_int_16)(h / 2);
    D.k = k;
    D.for_w = full->width;
    D.for_h = full->height;
    return 0;
}

void brd_display_render(br_demo *demo, int pixel_option)
{
    br_pixelmap *full = demo->colour_buffer, *lo;
    int k = brd_display_pixel(pixel_option);
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

int brd_display_period_available(const br_demo *demo) { return !demo->hw_accel; }

/* The 8-bit target and its depth at 1/k of the window, matched from the
 * window so the software renderer can draw into them, and a memory RGB_888
 * buffer of the same size the indices are expanded into. */
static int period_buffers(br_pixelmap *full, int k)
{
    br_int_32 w = full->width / k, h = full->height / k;
    if (D.index8 && D.k8 == k && D.for_w8 == full->width && D.for_h8 == full->height)
        return 0;
    release_period();
    if (w < 1 || h < 1)
        return -1;
    D.index8 = BrPixelmapAllocate(BR_PMT_INDEX_8, w, h, NULL, BR_PMAF_NORMAL);
    D.depth8 = BrPixelmapAllocate(BR_PMT_DEPTH_16, w, h, NULL, BR_PMAF_NORMAL);
    D.rgb = BrPixelmapAllocate(BR_PMT_RGB_888, w, h, NULL, BR_PMAF_NORMAL);
    if (D.index8 == NULL || D.depth8 == NULL || D.rgb == NULL) {
        BrLogError("DISPLAY", "could not make a %dx%d 8-bit buffer for the period look", (int)w, (int)h);
        return -1;
    }
    D.index8->origin_x = D.depth8->origin_x = D.rgb->origin_x = (br_int_16)(w / 2);
    D.index8->origin_y = D.depth8->origin_y = D.rgb->origin_y = (br_int_16)(h / 2);
    D.k8 = k;
    D.for_w8 = full->width;
    D.for_h8 = full->height;
    return 0;
}

/* A BRender palette: 256 entries of B, G, R (and X), one per row when it is
 * one pixel wide, as the .pal files are. */
static const unsigned char *palette_entry(const br_pixelmap *palette, int index)
{
    long step = palette->width == 1 ? palette->row_bytes
                : (palette->type == BR_PMT_RGBX_888 || palette->type == BR_PMT_RGBA_8888 ? 4 : 3);
    return (const unsigned char *)palette->pixels + (long)index * step;
}

static void expand(br_pixelmap *index8, br_pixelmap *rgb, const br_pixelmap *palette)
{
    int x, y;
    BrPixelmapDirectLock(index8, BR_TRUE);
    for (y = 0; y < rgb->height; y++) {
        const unsigned char *src = (const unsigned char *)index8->pixels + (long)y * index8->row_bytes;
        unsigned char *dst = (unsigned char *)rgb->pixels + (long)y * rgb->row_bytes;
        for (x = 0; x < rgb->width; x++) {
            const unsigned char *e = palette_entry(palette, src[x]);
            dst[x * 3] = e[0]; dst[x * 3 + 1] = e[1]; dst[x * 3 + 2] = e[2];
        }
    }
    BrPixelmapDirectUnlock(index8);
}

int brd_display_render_period(br_demo *demo, int pixel_option, br_pixelmap *palette, br_uint_8 clear)
{
    br_pixelmap *full = demo->colour_buffer, *shown;
    int k = brd_display_pixel(pixel_option);
    if (demo->hw_accel || palette == NULL || palette->pixels == NULL || palette->width * palette->height < 256)
        return -1;
    if (period_buffers(full, k) != 0 || (k > 1 && small_buffers(full, k) != 0))
        return -1;
    BrRendererFrameBegin();
    BrPixelmapFill(D.index8, clear);
    BrPixelmapFill(D.depth8, 0xFFFFFFFF);
    if (demo->camera != NULL)
        BrZbSceneRender(demo->world, demo->camera, D.index8, D.depth8);
    BrRendererFrameEnd();
    expand(D.index8, D.rgb, palette);
    /* the colours reach the window's own pixel type through a same-size copy */
    shown = k > 1 ? D.colour : full;
    BrPixelmapCopy(shown, D.rgb);
    if (k > 1) {
        const unsigned char *bg = palette_entry(palette, clear); /* any strip left over */
        BrPixelmapFill(full, BR_COLOUR_RGB(bg[2], bg[1], bg[0]));
        BrPixelmapRectangleStretchCopy(full, -full->origin_x + (full->width - shown->width * k) / 2,
                                       -full->origin_y + (full->height - shown->height * k) / 2, shown->width * k,
                                       shown->height * k, shown, -shown->origin_x, -shown->origin_y, shown->width, shown->height);
    }
    return 0;
}

int brd_frame_write_ppm(br_pixelmap *frame, br_pixelmap *palette, const char *path, int hw_accel)
{
    br_pixelmap *mem, *rgb;
    FILE *f;
    int x, y;
    if (hw_accel) {
        static void (*finish)(void);
        static int looked;
        if (!looked) {
            finish = (void (*)(void))SDL_GL_GetProcAddress("glFinish");
            looked = 1;
        }
        if (finish) finish();
    }
    /* a memory copy of the same type and size: the only copy every device supports */
    if ((mem = BrPixelmapAllocate(frame->type, frame->width, frame->height, NULL, BR_PMAF_NORMAL)) == NULL)
        return -1;
    mem->origin_x = frame->origin_x;
    mem->origin_y = frame->origin_y;
    BrPixelmapCopy(mem, frame);
    if (mem->type == BR_PMT_INDEX_8 && mem->map == NULL)
        mem->map = frame->map != NULL ? frame->map : palette;
    rgb = BrPixelmapCloneTyped(mem, BR_PMT_RGB_888); /* then BRender converts it, whatever the byte order */
    BrPixelmapFree(mem);
    if (rgb == NULL || (f = fopen(path, "wb")) == NULL) {
        if (rgb) BrPixelmapFree(rgb);
        return -1;
    }
    fprintf(f, "P6\n%d %d\n255\n", rgb->width, rgb->height);
    for (y = 0; y < rgb->height; y++) {
        const unsigned char *row = (const unsigned char *)rgb->pixels + (long)y * rgb->row_bytes;
        for (x = 0; x < rgb->width; x++) { /* RGB_888 is stored B, G, R */
            unsigned char px[3] = {row[x * 3 + 2], row[x * 3 + 1], row[x * 3]};
            if (hw_accel) { unsigned char t = px[0]; px[0] = px[2]; px[2] = t; }
            fwrite(px, 1, 3, f);
        }
    }
    fclose(f);
    BrPixelmapFree(rgb);
    return 0;
}
