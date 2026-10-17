/* The Keeper's Hour: text on screen, at a size the player can read.
 *
 * All text is BRender's BrFontProp7x9, drawn at a whole-number scale: each
 * font pixel becomes a k x k block, so it stays crisp. The scale comes from
 * the Text size option and the window: Auto picks the largest scale that
 * keeps the panels on screen (one step per 640 x 400), and 1 to 3 are taken
 * as asked, up to that same limit.
 * SPDX-License-Identifier: MIT */
#ifndef KH_TEXT_H
#define KH_TEXT_H

#include <brender.h>

#define KH_TEXT_AUTO 0
#define KH_TEXT_MAX  3

/* Set the scale for this frame from the option (KH_TEXT_AUTO or 1 to 3) and
 * the target's size. Returns the scale in use. */
int kh_text_frame(int option, const br_pixelmap *pm);
int kh_text_scale(void);

/* n screen pixels at the current scale: for panel sizes and offsets. */
br_int_32 kh_ui(br_int_32 n);

br_int_32 kh_text_w(br_pixelmap *pm, const char *s);
br_int_32 kh_text_h(br_pixelmap *pm);

/* Draw at the current scale, or at scale k. */
void kh_text(br_pixelmap *pm, br_int_32 x, br_int_32 y, br_colour colour, const char *s);
void kh_text_at(br_pixelmap *pm, br_int_32 x, br_int_32 y, br_colour colour, const char *s, int k);

/* On the software renderer, text goes through a memory strip (see kh_text.c). */
void kh_text_via_memory(int on);

#endif
