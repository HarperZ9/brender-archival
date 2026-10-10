/* The Keeper's Hour: pictures from data/art, as BRender texture maps.
 * The pictures are drawn by tools/make_art.py (CC BY 4.0) and stored as PPM.
 * SPDX-License-Identifier: MIT */
#include <stdio.h>
#include <string.h>

#include <SDL3/SDL.h>
#include "kh_tex.h"

#define KH_MAX_TEX 16

static struct { char name[32]; br_pixelmap *pm; } cache[KH_MAX_TEX];
static int ncache;

static br_pixelmap *load_ppm(const char *path)
{
    size_t size = 0;
    unsigned char *data = SDL_LoadFile(path, &size);
    br_pixelmap *pm = NULL;
    int w = 0, h = 0, max = 0, header = 0, y;
    if (data == NULL)
        return NULL;
    if (sscanf((const char *)data, "P6 %d %d %d%n", &w, &h, &max, &header) == 3 && w == 128 && h == 128 && max == 255
        && (size_t)header + 1 + (size_t)w * h * 3 <= size) {
        const unsigned char *rgb = data + header + 1;
        pm = BrPixelmapAllocate(BR_PMT_RGB_888, w, h, NULL, BR_PMAF_NORMAL);
        for (y = 0; pm != NULL && y < h; y++) {
            unsigned char *row = (unsigned char *)pm->pixels + (long)y * pm->row_bytes;
            int x;
            for (x = 0; x < w; x++) { /* BRender stores RGB_888 as B, G, R */
                row[x * 3 + 0] = rgb[(y * w + x) * 3 + 2];
                row[x * 3 + 1] = rgb[(y * w + x) * 3 + 1];
                row[x * 3 + 2] = rgb[(y * w + x) * 3 + 0];
            }
        }
    }
    SDL_free(data);
    return pm;
}

br_pixelmap *kh_tex(const char *name)
{
    char path[1024];
    br_pixelmap *pm;
    int i;
    for (i = 0; i < ncache; i++)
        if (strcmp(cache[i].name, name) == 0)
            return cache[i].pm;
    snprintf(path, sizeof(path), "%sdata/art/%s.ppm", SDL_GetBasePath(), name);
    if ((pm = load_ppm(path)) == NULL) {
        BrLogError("KEEPER", "cannot read texture %s", path);
        return NULL;
    }
    pm->identifier = BrResStrDup(pm, name);
    BrMapAdd(pm);
    if (ncache < KH_MAX_TEX) {
        snprintf(cache[ncache].name, sizeof(cache[ncache].name), "%s", name);
        cache[ncache++].pm = pm;
    }
    return pm;
}

br_material *kh_tex_material(const char *name, int two_sided)
{
    br_material *m = BrMaterialAllocate(name);
    m->colour = BR_COLOUR_RGB(255, 255, 255);
    m->colour_map = kh_tex(name);
    m->flags = BR_MATF_LIGHT | BR_MATF_SMOOTH | BR_MATF_PERSPECTIVE | BR_MATF_DISABLE_COLOUR_KEY | (two_sided ? BR_MATF_TWO_SIDED : 0);
    m->ka = BR_UFRACTION(0.30);
    m->kd = BR_UFRACTION(0.80);
    m->ks = BR_UFRACTION(0.05);
    m->power = BR_SCALAR(8);
    BrMaterialAdd(m);
    return m;
}

br_colour kh_px(const br_pixelmap *target, int r, int g, int b)
{
    switch (target->type) {
    case BR_PMT_RGB_565: return BR_COLOUR_RGB_565(r, g, b);
    case BR_PMT_RGB_555: return BR_COLOUR_RGB_555(r, g, b);
    case BR_PMT_RGB_888: return ((br_colour)r << 16) | ((br_colour)g << 8) | (br_colour)b;
    default: return BR_COLOUR_RGBA(r, g, b, 255);
    }
}

int kh_frame_write(br_pixelmap *frame, const char *path, int swap_rb)
{
    /* a memory copy of the same type and size: the only copy every device supports */
    br_pixelmap *mem = BrPixelmapAllocate(frame->type, frame->width, frame->height, NULL, BR_PMAF_NORMAL), *rgb;
    FILE *f;
    int x, y;
    if (mem == NULL)
        return -1;
    mem->origin_x = frame->origin_x;
    mem->origin_y = frame->origin_y;
    BrPixelmapCopy(mem, frame);
    /* then BRender converts it to 24-bit, whatever the device's byte order */
    rgb = BrPixelmapCloneTyped(mem, BR_PMT_RGB_888);
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
            if (swap_rb) { unsigned char t = px[0]; px[0] = px[2]; px[2] = t; }
            fwrite(px, 1, 3, f);
        }
    }
    fclose(f);
    BrPixelmapFree(rgb);
    return 0;
}

static int text_via_memory;

void kh_text_via_memory(int on) { text_via_memory = on; }

void kh_text(br_pixelmap *pm, br_int_32 x, br_int_32 y, br_colour colour, const char *s)
{
    static br_pixelmap *strip;
    br_int_32 w, h;
    if (!text_via_memory) {
        BrPixelmapText(pm, x, y, colour, BrFontProp7x9, s);
        return;
    }
    /* Text drawn straight onto the software device's 24-bit buffer does not
     * appear (BlazingRenderer ed5e7a91), so copy the strip under the text into
     * memory, write the text there, and copy it back. */
    w = BrPixelmapTextWidth(pm, BrFontProp7x9, s);
    h = BrPixelmapTextHeight(pm, BrFontProp7x9);
    if (w <= 0 || w > 2048 || h > 32)
        return;
    if (strip == NULL || strip->type != pm->type)
        strip = BrPixelmapAllocate(pm->type, 2048, 32, NULL, BR_PMAF_NORMAL);
    if (strip == NULL)
        return;
    BrPixelmapRectangleCopy(strip, 0, 0, pm, x, y, w, h);
    if (pm->type == BR_PMT_RGB_888) /* text on a memory 24-bit map reads the colour with red and blue exchanged */
        colour = ((colour & 0xFF) << 16) | (colour & 0xFF00) | ((colour >> 16) & 0xFF);
    BrPixelmapText(strip, 0, 0, colour, BrFontProp7x9, s);
    BrPixelmapRectangleCopy(pm, x, y, strip, 0, 0, w, h);
}
