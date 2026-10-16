/* brdisplay: how a BRender 1.4 scene reaches the screen, shared by brview
 * and The Keeper's Hour. Pixel size, field of view, vsync and still frames,
 * applied to BlazingRenderer's brdemo window layer.
 *
 * Pixel size k > 1 draws the 3D scene into a buffer k times smaller in each
 * direction, then scales it up with whole, square pixels (nearest neighbour).
 * Text and panels drawn afterwards land at the window's own resolution, so
 * they stay sharp at every pixel size. The field of view is vertical, so a
 * wider window shows more to the sides and the same height (Hor+).
 * SPDX-License-Identifier: MIT */
#ifndef BRDISPLAY_H
#define BRDISPLAY_H

#include "brdemo.h"

#define BRD_PIXEL_MIN 1
#define BRD_PIXEL_MAX 6
#define BRD_FOV_MIN   40
#define BRD_FOV_MAX   90
#define BRD_FOV_STEP  5

/* Read <prefix>_PIXEL and <prefix>_FOV once (for example KEEPERS_PIXEL).
 * They override the saved options for this run only and are never saved. */
void brd_display_init(const char *env_prefix);

/* The pixel size and field of view in effect: the override, else the option. */
int  brd_display_pixel(int option);
int  brd_display_fov(int option);

/* Apply the field of view and vsync now. Cheap to call on every event. */
void brd_display_apply(br_demo *demo, int fov_option, int vsync_option);

/* Draw the scene at the current pixel size into demo->colour_buffer. */
void brd_display_render(br_demo *demo, int pixel_option);

/* The period look: the scene drawn by BRender's own 8-bit palette path into
 * an INDEX_8 buffer (BrZbSceneRender into a 256-colour target, the kernels
 * that 1990s games ran), then shown through `palette` at the same pixel size
 * as brd_display_render. Materials must be set up for indexed colour first
 * (index_base and index_range, 8-bit maps, index_shade). `clear` is the
 * palette index behind the scene. The software renderer only: returns -1
 * and draws nothing on OpenGL, which has no indexed target. */
int  brd_display_render_period(br_demo *demo, int pixel_option, br_pixelmap *palette, br_uint_8 clear);

/* 1 when the period look can be drawn here (the software renderer). */
int  brd_display_period_available(const br_demo *demo);

/* Free the small buffers; call when the window changes size and at exit. */
void brd_display_release(void);

/* Write a frame as a binary PPM. On OpenGL it first waits for the frame to
 * finish (glFinish), so the readback is never the previous frame. An indexed
 * (8-bit) frame without its own palette is expanded through `palette`, which
 * may be NULL otherwise. 0 on success. */
int  brd_frame_write_ppm(br_pixelmap *frame, br_pixelmap *palette, const char *path, int hw_accel);

#endif
