/*
 * Pentprim C port: DIAGNOSTIC build - every stub prints when called.
 * This traces which rasterizer functions fire during BrZbSceneRender.
 */
#define __BR_V1DB__ 1
#include "brender.h"

#include <stdio.h>
#include "drv.h"

#if defined(_DEBUG)
#include <crtdbg.h>
#endif

/* ---- real-semantics helpers ---- */

int _sar16(int v)
{
    return v >> 16;
}

#undef BrFixedDiv
br_int_32 BrFixedDiv(br_int_32 a, br_int_32 b)
{
    if (b == 0) return (a >= 0) ? 0x7fffffff : -0x7fffffff;
    return (br_int_32)(((long long)a << 16) / b);
}

br_int_32 SafeFixedMac2Div(br_int_32 a, br_int_32 b, br_int_32 c, br_int_32 d, br_int_32 e)
{
    br_int_32 num = a * b;
    br_int_32 den = c * d;
    if (den == 0) return (num >= 0) ? 0x7fffffff : -0x7fffffff;
    return (br_int_32)(((long long)num << 16) / den);
}

void RasteriseBufferDisable(void)
{
}

/* ---- diagnostic stubs: print name when called ---- */

void BR_ASM_CALL ScanLinePITIP256_RGB_555(void)
{
    fprintf(stderr, "CALL ScanLinePITIP256_RGB_555\n"); fflush(stderr);
    
}

void BR_ASM_CALL ScanLinePITIPB256_RGB_555(void)
{
    fprintf(stderr, "CALL ScanLinePITIPB256_RGB_555\n"); fflush(stderr);
    
}

void BR_ASM_CALL ScanLinePITIPB256_RGB_565(void)
{
    fprintf(stderr, "CALL ScanLinePITIPB256_RGB_565\n"); fflush(stderr);
    
}

void BR_ASM_CALL ScanLinePIZ2TIP256_RGB_555(void)
{
    fprintf(stderr, "CALL ScanLinePIZ2TIP256_RGB_555\n"); fflush(stderr);
    
}

void BR_ASM_CALL ScanLinePIZ2TIPB256_RGB_555(void)
{
    fprintf(stderr, "CALL ScanLinePIZ2TIPB256_RGB_555\n"); fflush(stderr);
    
}

void BR_ASM_CALL ScanLinePIZ2TIPB256_RGB_565(void)
{
    fprintf(stderr, "CALL ScanLinePIZ2TIPB256_RGB_565\n"); fflush(stderr);
    
}

void BR_ASM_CALL TrapezoidRenderPITA(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2, br_uint_16 (*fp_vertices)[3])
{
    fprintf(stderr, "CALL TrapezoidRenderPITA\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2; (void)fp_vertices;
}

void BR_ASM_CALL TrapezoidRenderPITA15(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2, br_uint_16 (*fp_vertices)[3])
{
    fprintf(stderr, "CALL TrapezoidRenderPITA15\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2; (void)fp_vertices;
}

void BR_ASM_CALL TrapezoidRenderPITA24(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2, br_uint_16 (*fp_vertices)[3])
{
    fprintf(stderr, "CALL TrapezoidRenderPITA24\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2; (void)fp_vertices;
}

void BR_ASM_CALL TrapezoidRenderPITAN(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2, br_uint_16 (*fp_vertices)[3])
{
    fprintf(stderr, "CALL TrapezoidRenderPITAN\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2; (void)fp_vertices;
}

void BR_ASM_CALL TrapezoidRenderPITIA(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2, br_uint_16 (*fp_vertices)[3])
{
    fprintf(stderr, "CALL TrapezoidRenderPITIA\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2; (void)fp_vertices;
}

void BR_ASM_CALL TrapezoidRenderPITIA_RGB_555(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2, br_uint_16 (*fp_vertices)[3])
{
    fprintf(stderr, "CALL TrapezoidRenderPITIA_RGB_555\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2; (void)fp_vertices;
}

void BR_ASM_CALL TrapezoidRenderPITIA_RGB_888(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2, br_uint_16 (*fp_vertices)[3])
{
    fprintf(stderr, "CALL TrapezoidRenderPITIA_RGB_888\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2; (void)fp_vertices;
}

void BR_ASM_CALL TrapezoidRenderPIZ2TA(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2, br_uint_16 (*fp_vertices)[3])
{
    fprintf(stderr, "CALL TrapezoidRenderPIZ2TA\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2; (void)fp_vertices;
}

void BR_ASM_CALL TrapezoidRenderPIZ2TA15(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2, br_uint_16 (*fp_vertices)[3])
{
    fprintf(stderr, "CALL TrapezoidRenderPIZ2TA15\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2; (void)fp_vertices;
}

void BR_ASM_CALL TrapezoidRenderPIZ2TA24(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2, br_uint_16 (*fp_vertices)[3])
{
    fprintf(stderr, "CALL TrapezoidRenderPIZ2TA24\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2; (void)fp_vertices;
}

void BR_ASM_CALL TrapezoidRenderPIZ2TAN(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2, br_uint_16 (*fp_vertices)[3])
{
    fprintf(stderr, "CALL TrapezoidRenderPIZ2TAN\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2; (void)fp_vertices;
}

void BR_ASM_CALL TrapezoidRenderPIZ2TIA(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2, br_uint_16 (*fp_vertices)[3])
{
    fprintf(stderr, "CALL TrapezoidRenderPIZ2TIA\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2; (void)fp_vertices;
}

void BR_ASM_CALL TrapezoidRenderPIZ2TIA_RGB_555(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2, br_uint_16 (*fp_vertices)[3])
{
    fprintf(stderr, "CALL TrapezoidRenderPIZ2TIA_RGB_555\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2; (void)fp_vertices;
}

void BR_ASM_CALL TrapezoidRenderPIZ2TIA_RGB_888(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2, br_uint_16 (*fp_vertices)[3])
{
    fprintf(stderr, "CALL TrapezoidRenderPIZ2TIA_RGB_888\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2; (void)fp_vertices;
}

void BR_ASM_CALL TriangleRenderPII_RGB_555(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRenderPII_RGB_555\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRenderPII_RGB_565(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRenderPII_RGB_565\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRenderPII_RGB_888(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRenderPII_RGB_888\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRenderPIZ2I_RGB_555(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRenderPIZ2I_RGB_555\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRenderPIZ2I_RGB_565(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRenderPIZ2I_RGB_565\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRenderPIZ2I_RGB_888(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRenderPIZ2I_RGB_888\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRenderPIZ2TPD1024(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRenderPIZ2TPD1024\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRenderPIZ2TPD128(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRenderPIZ2TPD128\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRenderPIZ2TPD256(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRenderPIZ2TPD256\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRenderPIZ2TPD64(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRenderPIZ2TPD64\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRenderPIZ2_RGB_555(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRenderPIZ2_RGB_555\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRenderPIZ2_RGB_565(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRenderPIZ2_RGB_565\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}


/*
 * Real C implementation of TriangleRenderPIZ2_RGB_888.
 *
 * Ported from tt24_piz.asm RawTriangle_PIZ2_RGB_888.
 * Flat-colour Z-buffered triangle rasteriser for RGB_888 targets.
 *
 * Algorithm:
 *   1. Read fill colour from v0->comp[C_R], [C_G], [C_B]
 *   2. Sort 3 vertices by screen Y
 *   3. Walk long edge + two short edges (top/bottom trapezoids)
 *   4. Per scanline: interpolate X and Z
 *   5. Per pixel: Z-test against depth buffer, write RGB if closer
 *
 * The brp_vertex component array is accessed via the block's
 * component mapping. In FLOAT builds, comp values are br_scalar (float).
 *
 * Access to the work area (colour/depth buffers) is through the
 * extern `work` global declared in work.h.
 */
#define __BR_V1DB__ 1
#include "brender.h"

#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <string.h>

#if defined(_DEBUG)
#include <crtdbg.h>
#endif

/* Component indices from BRender */
#ifndef C_SX
#define C_SX 0
#endif
#ifndef C_SY
#define C_SY 1
#endif
#ifndef C_SZ
#define C_SZ 2
#endif
#ifndef C_I
#define C_I 3
#endif
#ifndef C_U
#define C_U 4
#endif
#ifndef C_V
#define C_V 5
#endif
#ifndef C_R
#define C_R 6
#endif
#ifndef C_G
#define C_G 7
#endif
#ifndef C_B
#define C_B 8
#endif

/* Work area accessor — pentprim's global render workspace.
 * Declared in work.h; we re-declare here to avoid pulling in
 * all of pentprim's internal headers. */

/* Helper: swap two brp_vertex pointers */
static void swap_v(union brp_vertex **a, union brp_vertex **b)
{
    union brp_vertex *t = *a;
    *a = *b;
    *b = t;
}

void BR_ASM_CALL TriangleRenderPIZ2_RGB_888(
    struct brp_block *block,
    union brp_vertex *pv0,
    union brp_vertex *pv1,
    union brp_vertex *pv2)
{
    (void)block;

    /* Fill colour from vertex 0 (flat shading) */
    int cr = (int)BrScalarToFloat(pv0->comp[C_R]);
    int cg = (int)BrScalarToFloat(pv0->comp[C_G]);
    int cb = (int)BrScalarToFloat(pv0->comp[C_B]);
    /* Clamp */
    if (cr < 0) cr = 0; if (cr > 255) cr = 255;
    if (cg < 0) cg = 0; if (cg > 255) cg = 255;
    if (cb < 0) cb = 0; if (cb > 255) cb = 255;
    /* Diagnostic: if colour is all zeros, use grey so pixels are visible */
    if (cr + cg + cb == 0) { cr = 128; cg = 128; cb = 128; }

    /* Sort vertices by screen Y (v0 = top, v2 = bottom) */
    union brp_vertex *v[3] = { pv0, pv1, pv2 };
    if (BrScalarToFloat(v[0]->comp[C_SY]) > BrScalarToFloat(v[1]->comp[C_SY]))
        swap_v(&v[0], &v[1]);
    if (BrScalarToFloat(v[1]->comp[C_SY]) > BrScalarToFloat(v[2]->comp[C_SY]))
        swap_v(&v[1], &v[2]);
    if (BrScalarToFloat(v[0]->comp[C_SY]) > BrScalarToFloat(v[1]->comp[C_SY]))
        swap_v(&v[0], &v[1]);

    float y0 = BrScalarToFloat(v[0]->comp[C_SY]);
    float y1 = BrScalarToFloat(v[1]->comp[C_SY]);
    float y2 = BrScalarToFloat(v[2]->comp[C_SY]);
    float x0 = BrScalarToFloat(v[0]->comp[C_SX]);
    float x1 = BrScalarToFloat(v[1]->comp[C_SX]);
    float x2 = BrScalarToFloat(v[2]->comp[C_SX]);
    float z0 = BrScalarToFloat(v[0]->comp[C_SZ]);
    float z1 = BrScalarToFloat(v[1]->comp[C_SZ]);
    float z2 = BrScalarToFloat(v[2]->comp[C_SZ]);

    {
        fprintf(stderr, "VERT sx=(%f,%f,%f) sy=(%f,%f,%f) sz=(%f,%f,%f) rgb=(%d,%d,%d)\n",
            BrScalarToFloat(pv0->comp[C_SX]), BrScalarToFloat(pv1->comp[C_SX]), BrScalarToFloat(pv2->comp[C_SX]),
            BrScalarToFloat(pv0->comp[C_SY]), BrScalarToFloat(pv1->comp[C_SY]), BrScalarToFloat(pv2->comp[C_SY]),
            BrScalarToFloat(pv0->comp[C_SZ]), BrScalarToFloat(pv1->comp[C_SZ]), BrScalarToFloat(pv2->comp[C_SZ]),
            cr, cg, cb);
        fflush(stderr);
    }
    {
        fprintf(stderr, "VERT sx=(%f,%f,%f) sy=(%f,%f,%f) sz=(%f,%f,%f) rgb=(%d,%d,%d)\n",
            BrScalarToFloat(pv0->comp[C_SX]), BrScalarToFloat(pv1->comp[C_SX]), BrScalarToFloat(pv2->comp[C_SX]),
            BrScalarToFloat(pv0->comp[C_SY]), BrScalarToFloat(pv1->comp[C_SY]), BrScalarToFloat(pv2->comp[C_SY]),
            BrScalarToFloat(pv0->comp[C_SZ]), BrScalarToFloat(pv1->comp[C_SZ]), BrScalarToFloat(pv2->comp[C_SZ]),
            cr, cg, cb);
        fflush(stderr);
    }
    int iy0 = (int)(y0 + 0.5f);
    int iy1 = (int)(y1 + 0.5f);
    int iy2 = (int)(y2 + 0.5f);

    if (iy0 == iy2) return; /* zero-height triangle */

    unsigned char *cbase = (unsigned char *)work.colour.base;
    int cstride = work.colour.stride_b;
    unsigned short *dbase = (unsigned short *)work.depth.base;
    int dstride = work.depth.stride_b / 2; /* in uint16 units */

    if (!cbase || !dbase) return;

    /* Walk long edge (y0 -> y2) and short edges (y0 -> y1, y1 -> y2) */
    for (int y = iy0; y <= iy2; y++) {
        if (y < 0 || y * (int)work.colour.stride_b >= (int)(work.colour.stride_b * 240)) continue;

        /* Determine which half we're in */
        float t_long, t_short;
        int xa, xb, za, zb;

        if (y < iy1) {
            /* Top half: long edge v0->v2, short edge v0->v1 */
            t_long = (iy2 != iy0) ? (float)(y - iy0) / (float)(iy2 - iy0) : 0.0f;
            t_short = (iy1 != iy0) ? (float)(y - iy0) / (float)(iy1 - iy0) : 0.0f;
        } else {
            /* Bottom half: long edge v0->v2, short edge v1->v2 */
            t_long = (iy2 != iy0) ? (float)(y - iy0) / (float)(iy2 - iy0) : 0.0f;
            t_short = (iy2 != iy1) ? (float)(y - iy1) / (float)(iy2 - iy1) : 0.0f;
        }

        /* Long edge endpoints */
        float xl_f = x0 + (x2 - x0) * t_long;
        float zl_f = z0 + (z2 - z0) * t_long;

        /* Short edge endpoints */
        float xr_f, zr_f;
        if (y < iy1) {
            xr_f = x0 + (x1 - x0) * t_short;
            zr_f = z0 + (z1 - z0) * t_short;
        } else {
            xr_f = x1 + (x2 - x1) * t_short;
            zr_f = z1 + (z2 - z1) * t_short;
        }

        /* Order left-right */
        int xl = (int)(xl_f + 0.5f);
        int xr = (int)(xr_f + 0.5f);
        float zl = zl_f, zr = zr_f;
        if (xl > xr) {
            int tmpi = xl; xl = xr; xr = tmpi;
            float tmpz = zl; zl = zr; zr = tmpz;
        }

        int span = xr - xl;
        if (span <= 0) continue;

        unsigned char *crow = cbase + y * cstride;
        unsigned short *drow = dbase + y * dstride;

        for (int x = xl; x <= xr; x++) {
            if (x < 0 || x * 3 >= (int)work.colour.stride_b) continue;

            float t = (span > 0) ? (float)(x - xl) / (float)span : 0.0f;
            int z = (int)(zl + (zr - zl) * t);

            if (z < 0) z = 0;
            if (z > 65535) z = 65535;

            if (z >= drow[x]) {
                drow[x] = (unsigned short)z;
                crow[x * 3 + 0] = (unsigned char)cb; /* BRender stores BGR */
                crow[x * 3 + 1] = (unsigned char)cg;
                crow[x * 3 + 2] = (unsigned char)cr;
            }
        }
    }
}

void BR_ASM_CALL TriangleRenderPI_RGB_555(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRenderPI_RGB_555\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRenderPI_RGB_565(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRenderPI_RGB_565\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRenderPI_RGB_888(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRenderPI_RGB_888\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_I8(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_I8\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_I_I8(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_I_I8\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_PTI_I8_1024(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_PTI_I8_1024\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_PTI_I8_1024_FLAT(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_PTI_I8_1024_FLAT\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_PTI_I8_128(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_PTI_I8_128\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_PTI_I8_128_FLAT(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_PTI_I8_128_FLAT\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_PTI_I8_256(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_PTI_I8_256\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_PTI_I8_256_FLAT(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_PTI_I8_256_FLAT\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_PTI_I8_64(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_PTI_I8_64\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_PTI_I8_64_FLAT(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_PTI_I8_64_FLAT\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_PT_I8_1024(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_PT_I8_1024\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_PT_I8_128(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_PT_I8_128\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_PT_I8_256(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_PT_I8_256\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_PT_I8_32(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_PT_I8_32\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_PT_I8_64(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_PT_I8_64\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_TID_I8(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_TID_I8\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_TID_I8_256(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_TID_I8_256\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_TID_I8_256_FLAT(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_TID_I8_256_FLAT\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_TID_I8_FLAT(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_TID_I8_FLAT\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_TI_I8(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_TI_I8\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_TI_I8_256(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_TI_I8_256\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_TI_I8_256_FLAT(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_TI_I8_256_FLAT\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_TI_I8_FLAT(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_TI_I8_FLAT\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_T_I8(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_T_I8\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_T_I8_1024(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_T_I8_1024\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_T_I8_128(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_T_I8_128\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_T_I8_256(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_T_I8_256\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_T_I8_32(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_T_I8_32\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_T_I8_64(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_T_I8_64\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_ZIF_I8_D16(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_ZIF_I8_D16\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_ZIF_I8_D16_FLAT(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_ZIF_I8_D16_FLAT\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_ZI_I8_D16(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_ZI_I8_D16\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_ZI_I8_D16_ShadeTable(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_ZI_I8_D16_ShadeTable\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_ZPTB_I8_D16_1024(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_ZPTB_I8_D16_1024\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_ZPTB_I8_D16_128(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_ZPTB_I8_D16_128\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_ZPTB_I8_D16_256(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_ZPTB_I8_D16_256\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_ZPTB_I8_D16_32(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_ZPTB_I8_D16_32\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_ZPTB_I8_D16_64(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_ZPTB_I8_D16_64\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_ZPTFB_I8_D16_1024(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_ZPTFB_I8_D16_1024\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_ZPTFB_I8_D16_128(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_ZPTFB_I8_D16_128\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_ZPTFB_I8_D16_256(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_ZPTFB_I8_D16_256\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_ZPTFB_I8_D16_32(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_ZPTFB_I8_D16_32\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_ZPTFB_I8_D16_64(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_ZPTFB_I8_D16_64\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_ZPTF_I8_D16_1024(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_ZPTF_I8_D16_1024\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_ZPTF_I8_D16_128(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_ZPTF_I8_D16_128\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_ZPTF_I8_D16_256(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_ZPTF_I8_D16_256\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_ZPTF_I8_D16_32(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_ZPTF_I8_D16_32\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_ZPTF_I8_D16_64(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_ZPTF_I8_D16_64\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_ZPTIB_I8_D16_1024(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_ZPTIB_I8_D16_1024\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_ZPTIB_I8_D16_1024_FLAT(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_ZPTIB_I8_D16_1024_FLAT\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_ZPTIB_I8_D16_128(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_ZPTIB_I8_D16_128\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_ZPTIB_I8_D16_128_FLAT(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_ZPTIB_I8_D16_128_FLAT\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_ZPTIB_I8_D16_256(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_ZPTIB_I8_D16_256\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_ZPTIB_I8_D16_256_FLAT(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_ZPTIB_I8_D16_256_FLAT\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_ZPTIB_I8_D16_32(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_ZPTIB_I8_D16_32\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_ZPTIB_I8_D16_32_FLAT(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_ZPTIB_I8_D16_32_FLAT\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_ZPTIB_I8_D16_64(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_ZPTIB_I8_D16_64\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_ZPTIB_I8_D16_64_FLAT(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_ZPTIB_I8_D16_64_FLAT\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_ZPTIFB_I8_D16_1024(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_ZPTIFB_I8_D16_1024\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_ZPTIFB_I8_D16_1024_FLAT(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_ZPTIFB_I8_D16_1024_FLAT\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_ZPTIFB_I8_D16_128(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_ZPTIFB_I8_D16_128\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_ZPTIFB_I8_D16_128_FLAT(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_ZPTIFB_I8_D16_128_FLAT\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_ZPTIFB_I8_D16_256(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_ZPTIFB_I8_D16_256\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_ZPTIFB_I8_D16_256_FLAT(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_ZPTIFB_I8_D16_256_FLAT\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_ZPTIFB_I8_D16_32(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_ZPTIFB_I8_D16_32\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_ZPTIFB_I8_D16_32_FLAT(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_ZPTIFB_I8_D16_32_FLAT\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_ZPTIFB_I8_D16_64(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_ZPTIFB_I8_D16_64\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_ZPTIFB_I8_D16_64_FLAT(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_ZPTIFB_I8_D16_64_FLAT\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_ZPTIF_I8_D16_1024(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_ZPTIF_I8_D16_1024\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_ZPTIF_I8_D16_1024_FLAT(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_ZPTIF_I8_D16_1024_FLAT\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_ZPTIF_I8_D16_128(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_ZPTIF_I8_D16_128\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_ZPTIF_I8_D16_128_FLAT(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_ZPTIF_I8_D16_128_FLAT\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_ZPTIF_I8_D16_256(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_ZPTIF_I8_D16_256\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_ZPTIF_I8_D16_256_FLAT(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_ZPTIF_I8_D16_256_FLAT\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_ZPTIF_I8_D16_32(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_ZPTIF_I8_D16_32\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_ZPTIF_I8_D16_32_FLAT(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_ZPTIF_I8_D16_32_FLAT\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_ZPTIF_I8_D16_64(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_ZPTIF_I8_D16_64\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_ZPTIF_I8_D16_64_FLAT(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_ZPTIF_I8_D16_64_FLAT\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_ZPTI_I8_D16_1024(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_ZPTI_I8_D16_1024\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_ZPTI_I8_D16_1024_FLAT(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_ZPTI_I8_D16_1024_FLAT\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_ZPTI_I8_D16_128(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_ZPTI_I8_D16_128\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_ZPTI_I8_D16_128_FLAT(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_ZPTI_I8_D16_128_FLAT\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_ZPTI_I8_D16_256(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_ZPTI_I8_D16_256\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_ZPTI_I8_D16_256_FLAT(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_ZPTI_I8_D16_256_FLAT\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_ZPTI_I8_D16_32(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_ZPTI_I8_D16_32\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_ZPTI_I8_D16_32_FLAT(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_ZPTI_I8_D16_32_FLAT\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_ZPTI_I8_D16_64(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_ZPTI_I8_D16_64\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_ZPTI_I8_D16_64_FLAT(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_ZPTI_I8_D16_64_FLAT\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_ZPT_I8_D16_1024(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_ZPT_I8_D16_1024\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_ZPT_I8_D16_128(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_ZPT_I8_D16_128\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_ZPT_I8_D16_256(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_ZPT_I8_D16_256\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_ZPT_I8_D16_32(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_ZPT_I8_D16_32\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_ZPT_I8_D16_64(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_ZPT_I8_D16_64\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_ZTB_I8_D16(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_ZTB_I8_D16\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_ZTB_I8_D16_1024(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_ZTB_I8_D16_1024\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_ZTB_I8_D16_1024_FLAT(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_ZTB_I8_D16_1024_FLAT\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_ZTB_I8_D16_128(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_ZTB_I8_D16_128\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_ZTB_I8_D16_128_FLAT(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_ZTB_I8_D16_128_FLAT\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_ZTB_I8_D16_16(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_ZTB_I8_D16_16\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_ZTB_I8_D16_16_FLAT(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_ZTB_I8_D16_16_FLAT\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_ZTB_I8_D16_256(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_ZTB_I8_D16_256\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_ZTB_I8_D16_256_FLAT(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_ZTB_I8_D16_256_FLAT\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_ZTB_I8_D16_32(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_ZTB_I8_D16_32\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_ZTB_I8_D16_32_FLAT(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_ZTB_I8_D16_32_FLAT\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_ZTB_I8_D16_64(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_ZTB_I8_D16_64\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_ZTB_I8_D16_64_FLAT(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_ZTB_I8_D16_64_FLAT\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_ZTB_I8_D16_8(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_ZTB_I8_D16_8\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_ZTB_I8_D16_8_FLAT(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_ZTB_I8_D16_8_FLAT\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_ZTFB_I8_D16(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_ZTFB_I8_D16\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_ZTF_I8_D16(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_ZTF_I8_D16\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_ZTF_I8_D16_256(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_ZTF_I8_D16_256\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_ZTIB_I8_D16(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_ZTIB_I8_D16\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_ZTIB_I8_D16_1024(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_ZTIB_I8_D16_1024\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_ZTIB_I8_D16_128(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_ZTIB_I8_D16_128\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_ZTIB_I8_D16_16(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_ZTIB_I8_D16_16\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_ZTIB_I8_D16_256(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_ZTIB_I8_D16_256\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_ZTIB_I8_D16_32(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_ZTIB_I8_D16_32\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_ZTIB_I8_D16_64(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_ZTIB_I8_D16_64\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_ZTIB_I8_D16_8(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_ZTIB_I8_D16_8\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_ZTIB_I8_D16_FLAT(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_ZTIB_I8_D16_FLAT\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_ZTID_I8_D16(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_ZTID_I8_D16\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_ZTID_I8_D16_1024(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_ZTID_I8_D16_1024\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_ZTID_I8_D16_1024_FLAT(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_ZTID_I8_D16_1024_FLAT\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_ZTID_I8_D16_128(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_ZTID_I8_D16_128\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_ZTID_I8_D16_128_FLAT(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_ZTID_I8_D16_128_FLAT\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_ZTID_I8_D16_256(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_ZTID_I8_D16_256\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_ZTID_I8_D16_256_FLAT(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_ZTID_I8_D16_256_FLAT\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_ZTID_I8_D16_32(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_ZTID_I8_D16_32\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_ZTID_I8_D16_32_FLAT(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_ZTID_I8_D16_32_FLAT\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_ZTID_I8_D16_64(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_ZTID_I8_D16_64\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_ZTID_I8_D16_64_FLAT(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_ZTID_I8_D16_64_FLAT\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_ZTID_I8_D16_FLAT(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_ZTID_I8_D16_FLAT\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_ZTIFB_I8_D16(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_ZTIFB_I8_D16\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_ZTIFB_I8_D16_FLAT(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_ZTIFB_I8_D16_FLAT\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_ZTIF_I8_D16(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_ZTIF_I8_D16\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_ZTIF_I8_D16_256(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_ZTIF_I8_D16_256\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_ZTIF_I8_D16_256_FLAT(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_ZTIF_I8_D16_256_FLAT\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_ZTIF_I8_D16_FLAT(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_ZTIF_I8_D16_FLAT\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_ZTI_I8_D16(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_ZTI_I8_D16\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_ZTI_I8_D16_1024(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_ZTI_I8_D16_1024\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_ZTI_I8_D16_128(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_ZTI_I8_D16_128\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_ZTI_I8_D16_16(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_ZTI_I8_D16_16\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_ZTI_I8_D16_256(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_ZTI_I8_D16_256\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_ZTI_I8_D16_32(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_ZTI_I8_D16_32\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_ZTI_I8_D16_64(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_ZTI_I8_D16_64\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_ZTI_I8_D16_8(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_ZTI_I8_D16_8\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_ZTI_I8_D16_FLAT(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_ZTI_I8_D16_FLAT\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_ZT_I8_D16(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_ZT_I8_D16\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_ZT_I8_D16_1024(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_ZT_I8_D16_1024\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_ZT_I8_D16_1024_FLAT(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_ZT_I8_D16_1024_FLAT\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_ZT_I8_D16_128(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_ZT_I8_D16_128\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_ZT_I8_D16_128_FLAT(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_ZT_I8_D16_128_FLAT\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_ZT_I8_D16_16(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_ZT_I8_D16_16\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_ZT_I8_D16_16_FLAT(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_ZT_I8_D16_16_FLAT\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_ZT_I8_D16_256(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_ZT_I8_D16_256\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_ZT_I8_D16_256_FLAT(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_ZT_I8_D16_256_FLAT\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_ZT_I8_D16_32(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_ZT_I8_D16_32\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_ZT_I8_D16_32_FLAT(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_ZT_I8_D16_32_FLAT\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_ZT_I8_D16_64(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_ZT_I8_D16_64\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_ZT_I8_D16_64_FLAT(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_ZT_I8_D16_64_FLAT\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_ZT_I8_D16_8(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_ZT_I8_D16_8\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_ZT_I8_D16_8_FLAT(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_ZT_I8_D16_8_FLAT\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_ZT_RGB565_D16_1024(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_ZT_RGB565_D16_1024\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_ZT_RGB565_D16_128(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_ZT_RGB565_D16_128\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_ZT_RGB565_D16_256(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_ZT_RGB565_D16_256\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_ZT_RGB565_D16_32(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_ZT_RGB565_D16_32\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_ZT_RGB565_D16_64(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_ZT_RGB565_D16_64\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_Z_I8_D16(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_Z_I8_D16\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void BR_ASM_CALL TriangleRender_Z_I8_D16_ShadeTable(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{
    fprintf(stderr, "CALL TriangleRender_Z_I8_D16_ShadeTable\n"); fflush(stderr);
    (void)block; (void)v0; (void)v1; (void)v2;
}

void sar16(void)
{
    fprintf(stderr, "CALL sar16\n"); fflush(stderr);
    
}
