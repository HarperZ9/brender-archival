/* The Keeper's Hour: pictures from data/art, as BRender texture maps.
 * SPDX-License-Identifier: MIT */
#ifndef KH_TEX_H
#define KH_TEX_H

#include <brender.h>

/* The map data/art/<name>.ppm, loaded once and registered with BRender.
 * NULL if the file is missing or not a 128 x 128 binary PPM. */
br_pixelmap *kh_tex(const char *name);

/* A lit, textured material. The texture's own colours are the surface. */
br_material *kh_tex_material(const char *name, int two_sided);

/* A colour in the encoding the target pixelmap uses: packed 16-bit for the
 * 15 and 16-bit software modes, plain RGB for 24-bit, RGBA otherwise. */
br_colour kh_px(const br_pixelmap *target, int r, int g, int b);

/* Copy a frame into a memory pixelmap and write it as a binary PPM. 0 on success.
 * swap_rb: the OpenGL device reads back with red and blue exchanged (seen on
 * BlazingRenderer ed5e7a91); the caller says when to undo that. */
int kh_frame_write(br_pixelmap *frame, const char *path, int swap_rb);

/* BrPixelmapText, or, on the software renderer, the same text written through
 * a memory strip (see kh_tex.c). Font: BrFontProp7x9. */
void kh_text(br_pixelmap *pm, br_int_32 x, br_int_32 y, br_colour colour, const char *s);
void kh_text_via_memory(int on);

#endif
