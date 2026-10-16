/* The Keeper's Hour, period look: the texture colours by median cut.
 * SPDX-License-Identifier: MIT */
#ifndef KH_PERIOD_CUT_H
#define KH_PERIOD_CUT_H

#include <brender.h>

/* Split every texel of the RGB_888 maps into `count` boxes (at most 256) by
 * median cut along the widest channel, and write each box's mean colour to
 * pal[i] as r, g, b. Unused entries repeat pal[0]. A red channel of 0 becomes
 * 1, so no texture colour is pure black. */
void kh_period_cut(br_pixelmap **maps, int nmaps, unsigned char (*pal)[3], int count);

#endif
