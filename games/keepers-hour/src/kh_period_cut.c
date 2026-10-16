/* The Keeper's Hour, period look: median cut over the texels of the game's
 * RGB_888 maps, giving the colours the 8-bit maps are drawn in. See
 * kh_period.c for where they sit in the palette.
 * SPDX-License-Identifier: MIT */
#include <string.h>

#include <SDL3/SDL.h>
#include "kh_period_cut.h"

typedef struct box { int first, count; } box;

static int texels_of(br_pixelmap **maps, int nmaps, unsigned char (*out)[3], int cap)
{
    int m, x, y, n = 0;
    for (m = 0; m < nmaps; m++)
        for (y = 0; y < maps[m]->height; y++) {
            const unsigned char *row = (const unsigned char *)maps[m]->pixels + (long)y * maps[m]->row_bytes;
            for (x = 0; x < maps[m]->width && n < cap; x++, n++) { /* RGB_888 is stored B, G, R */
                out[n][0] = row[x * 3 + 2]; out[n][1] = row[x * 3 + 1]; out[n][2] = row[x * 3];
            }
        }
    return n;
}

static int sort_channel;
static int by_channel(const void *a, const void *b)
{
    return ((const unsigned char *)a)[sort_channel] - ((const unsigned char *)b)[sort_channel];
}

static int widest(unsigned char (*px)[3], const box *bx, int *range)
{
    int lo[3] = {255, 255, 255}, hi[3] = {0, 0, 0}, i, c, w = 0;
    for (i = bx->first; i < bx->first + bx->count; i++)
        for (c = 0; c < 3; c++) { lo[c] = px[i][c] < lo[c] ? px[i][c] : lo[c]; hi[c] = px[i][c] > hi[c] ? px[i][c] : hi[c]; }
    for (c = 1; c < 3; c++) if (hi[c] - lo[c] > hi[w] - lo[w]) w = c;
    *range = hi[w] - lo[w];
    return w;
}

void kh_period_cut(br_pixelmap **maps, int nmaps, unsigned char (*pal)[3], int count)
{
    static unsigned char px[16 * 128 * 128][3];
    static box boxes[256];
    int n = texels_of(maps, nmaps, px, (int)(sizeof(px) / sizeof(px[0]))), nb = 1, i, c;
    if (n == 0) return;
    boxes[0].first = 0;
    boxes[0].count = n;
    if (count > 256) count = 256;
    while (nb < count) {
        int pick = -1, best = 0, range, ch = 0, half;
        for (i = 0; i < nb; i++) {
            int w = widest(px, &boxes[i], &range);
            if (boxes[i].count > 1 && range * (long)boxes[i].count > (long)best) { best = range * boxes[i].count; pick = i; ch = w; }
        }
        if (pick < 0) break;
        sort_channel = ch;
        SDL_qsort(px[boxes[pick].first], (size_t)boxes[pick].count, 3, by_channel);
        half = boxes[pick].count / 2;
        boxes[nb].first = boxes[pick].first + half;
        boxes[nb].count = boxes[pick].count - half;
        boxes[pick].count = half;
        nb++;
    }
    for (i = 0; i < count; i++) {
        long sum[3] = {0, 0, 0};
        int k;
        if (i >= nb) { memcpy(pal[i], pal[0], 3); continue; }
        for (k = boxes[i].first; k < boxes[i].first + boxes[i].count; k++)
            for (c = 0; c < 3; c++) sum[c] += px[k][c];
        for (c = 0; c < 3; c++) {
            int v = (int)(sum[c] / boxes[i].count);
            pal[i][c] = (unsigned char)(v < 1 && c == 0 ? 1 : v); /* never pure black: not 0's colour */
        }
    }
}
