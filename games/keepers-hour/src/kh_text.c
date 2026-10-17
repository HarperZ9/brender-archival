/* The Keeper's Hour: text on screen. See kh_text.h.
 * SPDX-License-Identifier: MIT */
#include "kh_text.h"

static int text_via_memory, scale = 1;

void kh_text_via_memory(int on) { text_via_memory = on; }

int kh_text_frame(int option, const br_pixelmap *pm)
{
    int fit = pm->width / 640 < pm->height / 400 ? pm->width / 640 : pm->height / 400;
    fit = fit < 1 ? 1 : (fit > KH_TEXT_MAX ? KH_TEXT_MAX : fit);
    scale = option == KH_TEXT_AUTO ? fit : (option < fit ? option : fit);
    return scale;
}

int kh_text_scale(void) { return scale; }
br_int_32 kh_ui(br_int_32 n) { return n * scale; }
br_int_32 kh_text_w(br_pixelmap *pm, const char *s) { return BrPixelmapTextWidth(pm, BrFontProp7x9, s) * scale; }
br_int_32 kh_text_h(br_pixelmap *pm) { return BrPixelmapTextHeight(pm, BrFontProp7x9) * scale; }

/* Text drawn straight onto the software device's 24-bit buffer does not
 * appear (BlazingRenderer ed5e7a91), so copy the strip under the text into
 * memory, write the text there, and copy it back. */
static void text_1x(br_pixelmap *pm, br_int_32 x, br_int_32 y, br_colour colour, const char *s)
{
    static br_pixelmap *strip;
    br_int_32 w = BrPixelmapTextWidth(pm, BrFontProp7x9, s), h = BrPixelmapTextHeight(pm, BrFontProp7x9);
    if (!text_via_memory) {
        BrPixelmapText(pm, x, y, colour, BrFontProp7x9, s);
        return;
    }
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

/* The glyphs into a 1x memory mask, then each run of set pixels in a row as
 * one k-high block. On the software renderer the blocks go onto a memory copy
 * of the area under the text, which goes back in one copy; on OpenGL, whose
 * device does not copy part of itself into memory, straight onto the frame. */
static void text_scaled(br_pixelmap *pm, br_int_32 x, br_int_32 y, br_colour colour, const char *s, int k)
{
    static br_pixelmap *mask, *area;
    br_int_32 w = BrPixelmapTextWidth(pm, BrFontProp7x9, s), h = BrPixelmapTextHeight(pm, BrFontProp7x9), px, py;
    br_pixelmap *dst = pm;
    br_int_32 ox = x, oy = y;
    if (w <= 0 || w > 2048 || h > 32)
        return;
    if (mask == NULL && (mask = BrPixelmapAllocate(BR_PMT_RGB_888, 2048, 32, NULL, BR_PMAF_NORMAL)) == NULL)
        return;
    BrPixelmapFill(mask, 0);
    BrPixelmapText(mask, 0, 0, 0xFFFFFF, BrFontProp7x9, s);
    if (text_via_memory && (area == NULL || area->type != pm->type || area->width < w * k || area->height < h * k)) {
        br_int_32 aw = w * k > 1024 ? w * k : 1024, ah = h * k > 64 ? h * k : 64;
        if (area) BrPixelmapFree(area);
        if ((area = BrPixelmapAllocate(pm->type, aw, ah, NULL, BR_PMAF_NORMAL)) == NULL)
            return;
    }
    if (text_via_memory) {
        if (area->type == BR_PMT_RGB_888) /* as in text_1x: a memory 24-bit map takes the colour red and blue exchanged */
            colour = ((colour & 0xFF) << 16) | (colour & 0xFF00) | ((colour >> 16) & 0xFF);
        BrPixelmapRectangleCopy(area, 0, 0, pm, x, y, w * k, h * k);
        dst = area;
        ox = oy = 0;
    }
    for (py = 0; py < h; py++) {
        const unsigned char *row = (const unsigned char *)mask->pixels + (long)py * mask->row_bytes;
        for (px = 0; px < w; px++) {
            br_int_32 run = 0;
            while (px + run < w && row[(px + run) * 3] != 0) run++;
            if (run > 0)
                BrPixelmapRectangleFill(dst, ox + px * k, oy + py * k, run * k, k, colour);
            px += run;
        }
    }
    if (dst == area)
        BrPixelmapRectangleCopy(pm, x, y, area, 0, 0, w * k, h * k);
}

void kh_text_at(br_pixelmap *pm, br_int_32 x, br_int_32 y, br_colour colour, const char *s, int k)
{
    if (k <= 1) text_1x(pm, x, y, colour, s);
    else text_scaled(pm, x, y, colour, s, k > KH_TEXT_MAX * 2 ? KH_TEXT_MAX * 2 : k);
}

void kh_text(br_pixelmap *pm, br_int_32 x, br_int_32 y, br_colour colour, const char *s) { kh_text_at(pm, x, y, colour, s, scale); }
