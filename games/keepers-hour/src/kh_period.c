/* The Keeper's Hour: the period look. See kh_period.h.
 *
 * The palette, 256 entries:
 *   0         black: behind everything, and never a texel (0 is transparent)
 *   1..15     the glows and the night skies, each its own colour, unlit
 *   16..127   seven ramps of 16 for the plain lit surfaces: wood, brass,
 *             rust, stone and the rest, black at the bottom of each
 *   128..255  the colours of the pictures and the stone and board maps,
 *             chosen by median cut over every texel the game draws
 * A lit surface takes the ramp nearest its hue, and only the part of it up
 * to its own brightness, so a dark board stays darker than a pale one under
 * the same light. A picture is lit through a 64-row shade table: row r holds,
 * for each palette colour, the palette entry nearest that colour at r/63 of
 * full light.
 * SPDX-License-Identifier: MIT */
#include <string.h>

#include <SDL3/SDL.h>
#include "kh_period.h"
#include "kh_period_cut.h"
#include "kh_rooms.h"

#define MAX_MATERIALS 96
#define GLOW_FIRST    1
#define GLOW_COUNT    15
#define RAMP_FIRST    16
#define RAMP_LEN      16
#define RAMP_COUNT    7
#define TEX_FIRST     128
#define TEX_COUNT     128
#define SHADE_ROWS    64
/* The 8-bit path takes light as intensity only, and the rooms are lit by
 * a dim fill and the lamp; this brings the ramps' tops to the brightness the
 * true-colour rooms show under the same lights. */
#define RAMP_TOP      0.92f
#define SHADE_TOP     1.15f

typedef struct entry {
    br_material   *m;
    kh_period_kind kind;
    int            r, g, b;
    br_pixelmap   *rgb_map, *map8;
    int            base, range;
} entry;

static struct {
    entry        e[MAX_MATERIALS];
    int          n, built;
    unsigned char pal[256][3]; /* r, g, b */
    br_pixelmap *palette, *shade;
} P;

void kh_period_register(br_material *m, kh_period_kind kind, int r, int g, int b)
{
    entry *e;
    if (P.n >= MAX_MATERIALS)
        return;
    e = &P.e[P.n++];
    memset(e, 0, sizeof(*e));
    e->m = m;
    e->kind = kind;
    e->r = r; e->g = g; e->b = b;
    if (m != NULL && kind == KH_PERIOD_TEXTURED)
        e->rgb_map = m->colour_map;
}

static long dist(int r0, int g0, int b0, int r1, int g1, int b1)
{
    long dr = r0 - r1, dg = g0 - g1, db = b0 - b1;
    return dr * dr * 3 + dg * dg * 4 + db * db * 2;
}

static int nearest(int r, int g, int b, int first, int last)
{
    long best = -1;
    int i, at = first;
    for (i = first; i <= last; i++) {
        long d = dist(r, g, b, P.pal[i][0], P.pal[i][1], P.pal[i][2]);
        if (best < 0 || d < best) { best = d; at = i; }
    }
    return at;
}

br_uint_8 kh_period_index(int r, int g, int b) { return (br_uint_8)nearest(r, g, b, 1, 255); }

static int maxc(int r, int g, int b) { return r > g ? (r > b ? r : b) : (g > b ? g : b); }

/* ---- 1..15: glows and skies ---- */
static void build_glows(void)
{
    int used = 0, i, k;
    for (i = 0; i < P.n; i++) {
        entry *e = &P.e[i];
        if (e->kind != KH_PERIOD_GLOW)
            continue;
        for (k = 0; k < used; k++)
            if (P.pal[GLOW_FIRST + k][0] == e->r && P.pal[GLOW_FIRST + k][1] == e->g && P.pal[GLOW_FIRST + k][2] == e->b)
                break;
        if (k == used && used < GLOW_COUNT) {
            P.pal[GLOW_FIRST + used][0] = (unsigned char)e->r;
            P.pal[GLOW_FIRST + used][1] = (unsigned char)e->g;
            P.pal[GLOW_FIRST + used][2] = (unsigned char)e->b;
            used++;
        }
    }
    for (i = 0; i < P.n; i++)
        if (P.e[i].kind == KH_PERIOD_GLOW)
            P.e[i].base = nearest(P.e[i].r, P.e[i].g, P.e[i].b, GLOW_FIRST, GLOW_FIRST + (used ? used : 1) - 1);
}

/* ---- 16..127: ramps by hue ---- */
static void hue(const entry *e, float h[3])
{
    float m = (float)maxc(e->r, e->g, e->b);
    if (m < 1.0f) m = 1.0f;
    h[0] = e->r / m; h[1] = e->g / m; h[2] = e->b / m;
}

static float hue_dist(const float a[3], const float b[3])
{
    return (a[0] - b[0]) * (a[0] - b[0]) + (a[1] - b[1]) * (a[1] - b[1]) + (a[2] - b[2]) * (a[2] - b[2]);
}

static void build_ramps(void)
{
    float seed[RAMP_COUNT][3];
    int top[RAMP_COUNT][3], nseeds = 0, i, s, j;
    /* farthest-point seeds over the lit colours' hues, the first being the brightest */
    for (s = 0; s < RAMP_COUNT; s++) {
        float best = -1.0f, h[3];
        int pick = -1;
        for (i = 0; i < P.n; i++) {
            float d = 1e9f;
            if (P.e[i].kind != KH_PERIOD_LIT) continue;
            hue(&P.e[i], h);
            for (j = 0; j < nseeds; j++) { float q = hue_dist(h, seed[j]); d = q < d ? q : d; }
            if (nseeds == 0) d = (float)maxc(P.e[i].r, P.e[i].g, P.e[i].b);
            if (d > best) { best = d; pick = i; }
        }
        if (pick < 0 || (nseeds > 0 && best < 0.004f)) break;
        hue(&P.e[pick], seed[nseeds++]);
    }
    if (nseeds == 0) { seed[0][0] = seed[0][1] = seed[0][2] = 1.0f; nseeds = 1; }
    /* each ramp's top: the brightest colour among the surfaces that take it */
    for (s = 0; s < nseeds; s++) top[s][0] = top[s][1] = top[s][2] = 0;
    for (i = 0; i < P.n; i++) {
        float h[3], best = 1e9f;
        entry *e = &P.e[i];
        if (e->kind != KH_PERIOD_LIT) continue;
        hue(e, h);
        for (s = 0; s < nseeds; s++) { float q = hue_dist(h, seed[s]); if (q < best) { best = q; e->base = s; } }
        if (maxc(e->r, e->g, e->b) > maxc(top[e->base][0], top[e->base][1], top[e->base][2])) {
            top[e->base][0] = e->r; top[e->base][1] = e->g; top[e->base][2] = e->b;
        }
    }
    for (s = 0; s < RAMP_COUNT; s++)
        for (j = 0; j < RAMP_LEN; j++) {
            int k = s < nseeds ? s : 0, c;
            for (c = 0; c < 3; c++)
                P.pal[RAMP_FIRST + s * RAMP_LEN + j][c] = (unsigned char)(top[k][c] * RAMP_TOP * j / (RAMP_LEN - 1) + 0.5f);
        }
    for (i = 0; i < P.n; i++) {
        entry *e = &P.e[i];
        int t, s0 = e->base;
        if (e->kind != KH_PERIOD_LIT) continue;
        t = maxc(top[s0][0], top[s0][1], top[s0][2]);
        e->base = RAMP_FIRST + s0 * RAMP_LEN;
        e->range = t > 0 ? (RAMP_LEN - 1) * maxc(e->r, e->g, e->b) / t : RAMP_LEN - 1;
        if (e->range < 1) e->range = 1;
    }
}

static br_pixelmap *map8_of(br_pixelmap *rgb)
{
    br_pixelmap *pm = BrPixelmapAllocate(BR_PMT_INDEX_8, rgb->width, rgb->height, NULL, BR_PMAF_NORMAL);
    int x, y;
    if (pm == NULL) return NULL;
    for (y = 0; y < rgb->height; y++) {
        const unsigned char *src = (const unsigned char *)rgb->pixels + (long)y * rgb->row_bytes;
        unsigned char *dst = (unsigned char *)pm->pixels + (long)y * pm->row_bytes;
        for (x = 0; x < rgb->width; x++)
            dst[x] = (unsigned char)nearest(src[x * 3 + 2], src[x * 3 + 1], src[x * 3], TEX_FIRST, 255);
    }
    pm->identifier = BrResSprintf(pm, "%s-8bit", rgb->identifier ? rgb->identifier : "map");
    pm->map = P.palette;
    BrMapAdd(pm);
    return pm;
}

static void build_shade(void)
{
    int r, t;
    P.shade = BrPixelmapAllocate(BR_PMT_INDEX_8, 256, SHADE_ROWS, NULL, BR_PMAF_NORMAL);
    if (P.shade == NULL) return;
    for (r = 0; r < SHADE_ROWS; r++) {
        unsigned char *row = (unsigned char *)P.shade->pixels + (long)r * P.shade->row_bytes;
        float s = SHADE_TOP * r / (SHADE_ROWS - 1);
        row[0] = 0;
        for (t = 1; t < 256; t++) {
            int c[3], k;
            for (k = 0; k < 3; k++) { c[k] = (int)(P.pal[t][k] * s + 0.5f); c[k] = c[k] > 255 ? 255 : c[k]; }
            row[t] = (unsigned char)nearest(c[0], c[1], c[2], 1, 255);
        }
    }
    P.shade->identifier = "keepers-shade";
    BrTableAdd(P.shade);
}

int kh_period_build(void)
{
    br_pixelmap *maps[16];
    int nmaps = 0, i, k;
    if (P.built)
        return 0;
    for (i = 0; i < kh_room_count; i++) /* the skies are drawn as they are, like the glows */
        kh_period_register(NULL, KH_PERIOD_GLOW, kh_rooms[i].sky[0], kh_rooms[i].sky[1], kh_rooms[i].sky[2]);
    memset(P.pal, 0, sizeof(P.pal));
    build_glows();
    build_ramps();
    for (i = 0; i < P.n; i++) {
        br_pixelmap *m = P.e[i].rgb_map;
        if (m == NULL || m->type != BR_PMT_RGB_888) continue;
        for (k = 0; k < nmaps && maps[k] != m; k++) {}
        if (k == nmaps && nmaps < 16) maps[nmaps++] = m;
    }
    kh_period_cut(maps, nmaps, &P.pal[TEX_FIRST], TEX_COUNT);
    if ((P.palette = BrPixelmapAllocate(BR_PMT_RGBX_888, 1, 256, NULL, BR_PMAF_NORMAL)) == NULL)
        return -1;
    for (i = 0; i < 256; i++) {
        unsigned char *e = (unsigned char *)P.palette->pixels + (long)i * P.palette->row_bytes;
        e[0] = P.pal[i][2]; e[1] = P.pal[i][1]; e[2] = P.pal[i][0]; e[3] = 0;
    }
    P.palette->identifier = "keepers-palette";
    for (k = 0; k < nmaps; k++) {
        br_pixelmap *m8 = map8_of(maps[k]);
        for (i = 0; i < P.n; i++)
            if (P.e[i].rgb_map == maps[k]) P.e[i].map8 = m8;
    }
    build_shade();
    P.built = 1;
    return P.shade != NULL ? 0 : -1;
}

br_pixelmap *kh_period_palette(void) { return P.palette; }

void kh_period_apply(int on)
{
    int i;
    if (!P.built)
        return;
    for (i = 0; i < P.n; i++) {
        entry *e = &P.e[i];
        if (e->m == NULL) continue;
        if (e->kind == KH_PERIOD_TEXTURED) {
            e->m->colour_map = on && e->map8 ? e->map8 : e->rgb_map;
            e->m->index_shade = on ? P.shade : NULL;
            e->m->index_base = 0;
            e->m->index_range = SHADE_ROWS - 1;
        } else {
            e->m->index_base = (br_uint_8)e->base;
            e->m->index_range = (br_uint_8)e->range;
        }
        BrMaterialUpdate(e->m, BR_MATU_ALL);
    }
}
