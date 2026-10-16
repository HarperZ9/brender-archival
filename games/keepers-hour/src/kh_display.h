/* The Keeper's Hour: how the scene reaches the screen. Pixel size, field of
 * view and vsync, applied to the BRender demo layer.
 *
 * Pixel size k > 1 draws the 3D scene into a buffer k times smaller in each
 * direction, then scales it up with whole, square pixels (nearest neighbour).
 * The text and panels are drawn afterwards at the window's own resolution, so
 * they stay sharp at every pixel size. The field of view is vertical, so a
 * wider window shows more to the sides and the same height (Hor+).
 * SPDX-License-Identifier: MIT */
#ifndef KH_DISPLAY_H
#define KH_DISPLAY_H

#include "brdemo.h"

#define KH_PIXEL_MIN 1
#define KH_PIXEL_MAX 6
#define KH_FOV_MIN   40
#define KH_FOV_MAX   90
#define KH_FOV_STEP  5

/* Read KEEPERS_PIXEL and KEEPERS_FOV once; they override the saved options
 * for this run only (for stills and checks) and are never saved. */
void kh_display_init(void);

/* The pixel size and field of view in effect: the override, else the option. */
int  kh_display_pixel(int option);
int  kh_display_fov(int option);

/* Apply the field of view and vsync now. Call after any options change. */
void kh_display_apply(br_demo *demo, int fov_option, int vsync_option);

/* Draw the scene at the current pixel size into demo->colour_buffer. */
void kh_display_render(br_demo *demo, int pixel_option);

/* Free the small buffers; call when the window changes size and at exit. */
void kh_display_release(void);

#endif
