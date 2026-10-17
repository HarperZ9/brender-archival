/*
 * SPDX-License-Identifier: MIT
 * brview: lighting for textured models on the software rasteriser.
 *
 * BRender's software rasteriser lights a texture only through a shade table,
 * as it did in 1998: an 8-bit map, and a table whose row r holds, for every
 * palette index, that colour at light level r. Without one it draws the map
 * unlit (modern/parity/README.md, OpenGL against software). This builds the
 * 24-bit table from std.pal: row r is each palette colour scaled by
 * r / (rows - 1), so full light gives the map's own colours, as OpenGL does.
 */
#include <string.h>

#include "brview_scenes.h"

#define RGB_SHADE_ROWS 64

br_pixelmap *BrViewSceneRGBShade(void)
{
    static br_pixelmap *shade;
    br_pixelmap *pal = BrViewScenePalette();
    int r, t, c;
    if (shade != NULL || pal == NULL || pal->pixels == NULL)
        return shade;
    if ((shade = BrPixelmapAllocate(BR_PMT_RGB_888, 256, RGB_SHADE_ROWS, NULL, BR_PMAF_NORMAL)) == NULL)
        return NULL;
    for (r = 0; r < RGB_SHADE_ROWS; r++) {
        unsigned char *row = (unsigned char *)shade->pixels + (long)r * shade->row_bytes;
        for (t = 0; t < 256; t++) {
            /* std.pal is one entry per row, stored B, G, R (and X); so is the table */
            const unsigned char *e = (const unsigned char *)pal->pixels + (long)t * pal->row_bytes;
            for (c = 0; c < 3; c++)
                row[t * 3 + c] = (unsigned char)((e[c] * r + (RGB_SHADE_ROWS - 1) / 2) / (RGB_SHADE_ROWS - 1));
        }
    }
    shade->identifier = "brview-rgb-shade";
    BrTableAdd(shade);
    return shade;
}
