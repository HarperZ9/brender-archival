/* The Keeper's Hour: the period look. The rooms drawn in 256 colours by
 * BRender's own 8-bit palette path, the way a 1990s PC game was: lit
 * surfaces step down a palette ramp, pictures are 8-bit maps lit through a
 * shade table.
 *
 * Every material the game makes is registered here as it is made. When the
 * look is turned on, each one gets its palette ramp, or its 8-bit map and the
 * shade table, and BRender prepares it again; turning it off puts back the
 * true-colour map.
 * SPDX-License-Identifier: MIT */
#ifndef KH_PERIOD_H
#define KH_PERIOD_H

#include <brender.h>

typedef enum kh_period_kind { KH_PERIOD_LIT, KH_PERIOD_GLOW, KH_PERIOD_TEXTURED } kh_period_kind;

/* Called by kh_material, kh_glow and kh_tex_material. */
void kh_period_register(br_material *m, kh_period_kind kind, int r, int g, int b);

/* Build the palette, the ramps, the 8-bit maps and the shade table from
 * everything registered. Once, after the world is built. 0 on success. */
int kh_period_build(void);

/* Set every registered material up for 8-bit (on) or true colour (off). */
void kh_period_apply(int on);

br_pixelmap *kh_period_palette(void);

/* The palette index nearest a colour: the sky behind a room. */
br_uint_8 kh_period_index(int r, int g, int b);

#endif
