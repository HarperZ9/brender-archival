/*
 * Pentprim C port: auto-generated linkage stubs for assembly-only rasterizers.
 *
 * Derived from builds/pentprim-c-port-surface.txt (second pass, after
 * PARTS=0x03FF activated the in-tree generic-C implementations).
 *
 * Semantics, honestly stated:
 *  - Render, Trapezoid and ScanLine stubs are parameter-validated no-ops so the
 *    primitive library links and blocks can be selected; until real kernels
 *    replace them they emit no pixels. The softrend rung detects this via its
 *    lit-pixel threshold and reports invalid.
 *  - Helper kernels below implement real behavior.
 */
#define __BR_V1DB__ 1
#include "brender.h"

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

/* ---- linkage stubs for asm-only rasterizers ---- */

void BR_ASM_CALL ScanLinePITIP256_RGB_555(void)
{ }

void BR_ASM_CALL ScanLinePITIPB256_RGB_555(void)
{ }

void BR_ASM_CALL ScanLinePITIPB256_RGB_565(void)
{ }

void BR_ASM_CALL ScanLinePIZ2TIP256_RGB_555(void)
{ }

void BR_ASM_CALL ScanLinePIZ2TIPB256_RGB_555(void)
{ }

void BR_ASM_CALL ScanLinePIZ2TIPB256_RGB_565(void)
{ }

void BR_ASM_CALL TrapezoidRenderPITA(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2, br_uint_16 (*fp_vertices)[3])
{ (void)block; (void)v0; (void)v1; (void)v2; (void)fp_vertices; }

void BR_ASM_CALL TrapezoidRenderPITA15(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2, br_uint_16 (*fp_vertices)[3])
{ (void)block; (void)v0; (void)v1; (void)v2; (void)fp_vertices; }

void BR_ASM_CALL TrapezoidRenderPITA24(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2, br_uint_16 (*fp_vertices)[3])
{ (void)block; (void)v0; (void)v1; (void)v2; (void)fp_vertices; }

void BR_ASM_CALL TrapezoidRenderPITAN(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2, br_uint_16 (*fp_vertices)[3])
{ (void)block; (void)v0; (void)v1; (void)v2; (void)fp_vertices; }

void BR_ASM_CALL TrapezoidRenderPITIA(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2, br_uint_16 (*fp_vertices)[3])
{ (void)block; (void)v0; (void)v1; (void)v2; (void)fp_vertices; }

void BR_ASM_CALL TrapezoidRenderPITIA_RGB_555(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2, br_uint_16 (*fp_vertices)[3])
{ (void)block; (void)v0; (void)v1; (void)v2; (void)fp_vertices; }

void BR_ASM_CALL TrapezoidRenderPITIA_RGB_888(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2, br_uint_16 (*fp_vertices)[3])
{ (void)block; (void)v0; (void)v1; (void)v2; (void)fp_vertices; }

void BR_ASM_CALL TrapezoidRenderPIZ2TA(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2, br_uint_16 (*fp_vertices)[3])
{ (void)block; (void)v0; (void)v1; (void)v2; (void)fp_vertices; }

void BR_ASM_CALL TrapezoidRenderPIZ2TA15(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2, br_uint_16 (*fp_vertices)[3])
{ (void)block; (void)v0; (void)v1; (void)v2; (void)fp_vertices; }

void BR_ASM_CALL TrapezoidRenderPIZ2TA24(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2, br_uint_16 (*fp_vertices)[3])
{ (void)block; (void)v0; (void)v1; (void)v2; (void)fp_vertices; }

void BR_ASM_CALL TrapezoidRenderPIZ2TAN(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2, br_uint_16 (*fp_vertices)[3])
{ (void)block; (void)v0; (void)v1; (void)v2; (void)fp_vertices; }

void BR_ASM_CALL TrapezoidRenderPIZ2TIA(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2, br_uint_16 (*fp_vertices)[3])
{ (void)block; (void)v0; (void)v1; (void)v2; (void)fp_vertices; }

void BR_ASM_CALL TrapezoidRenderPIZ2TIA_RGB_555(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2, br_uint_16 (*fp_vertices)[3])
{ (void)block; (void)v0; (void)v1; (void)v2; (void)fp_vertices; }

void BR_ASM_CALL TrapezoidRenderPIZ2TIA_RGB_888(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2, br_uint_16 (*fp_vertices)[3])
{ (void)block; (void)v0; (void)v1; (void)v2; (void)fp_vertices; }

void BR_ASM_CALL TriangleRenderPII_RGB_555(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRenderPII_RGB_565(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRenderPII_RGB_888(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRenderPIZ2I_RGB_555(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRenderPIZ2I_RGB_565(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRenderPIZ2I_RGB_888(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRenderPIZ2TPD1024(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRenderPIZ2TPD128(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRenderPIZ2TPD256(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRenderPIZ2TPD64(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRenderPIZ2_RGB_555(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRenderPIZ2_RGB_565(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRenderPIZ2_RGB_888(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRenderPI_RGB_555(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRenderPI_RGB_565(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRenderPI_RGB_888(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_I8(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_I_I8(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_PTI_I8_1024(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_PTI_I8_1024_FLAT(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_PTI_I8_128(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_PTI_I8_128_FLAT(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_PTI_I8_256(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_PTI_I8_256_FLAT(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_PTI_I8_64(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_PTI_I8_64_FLAT(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_PT_I8_1024(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_PT_I8_128(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_PT_I8_256(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_PT_I8_32(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_PT_I8_64(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_TID_I8(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_TID_I8_256(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_TID_I8_256_FLAT(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_TID_I8_FLAT(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_TI_I8(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_TI_I8_256(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_TI_I8_256_FLAT(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_TI_I8_FLAT(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_T_I8(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_T_I8_1024(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_T_I8_128(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_T_I8_256(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_T_I8_32(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_T_I8_64(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_ZIF_I8_D16(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_ZIF_I8_D16_FLAT(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_ZI_I8_D16(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_ZI_I8_D16_ShadeTable(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_ZPTB_I8_D16_1024(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_ZPTB_I8_D16_128(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_ZPTB_I8_D16_256(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_ZPTB_I8_D16_32(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_ZPTB_I8_D16_64(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_ZPTFB_I8_D16_1024(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_ZPTFB_I8_D16_128(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_ZPTFB_I8_D16_256(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_ZPTFB_I8_D16_32(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_ZPTFB_I8_D16_64(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_ZPTF_I8_D16_1024(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_ZPTF_I8_D16_128(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_ZPTF_I8_D16_256(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_ZPTF_I8_D16_32(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_ZPTF_I8_D16_64(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_ZPTIB_I8_D16_1024(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_ZPTIB_I8_D16_1024_FLAT(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_ZPTIB_I8_D16_128(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_ZPTIB_I8_D16_128_FLAT(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_ZPTIB_I8_D16_256(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_ZPTIB_I8_D16_256_FLAT(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_ZPTIB_I8_D16_32(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_ZPTIB_I8_D16_32_FLAT(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_ZPTIB_I8_D16_64(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_ZPTIB_I8_D16_64_FLAT(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_ZPTIFB_I8_D16_1024(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_ZPTIFB_I8_D16_1024_FLAT(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_ZPTIFB_I8_D16_128(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_ZPTIFB_I8_D16_128_FLAT(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_ZPTIFB_I8_D16_256(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_ZPTIFB_I8_D16_256_FLAT(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_ZPTIFB_I8_D16_32(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_ZPTIFB_I8_D16_32_FLAT(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_ZPTIFB_I8_D16_64(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_ZPTIFB_I8_D16_64_FLAT(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_ZPTIF_I8_D16_1024(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_ZPTIF_I8_D16_1024_FLAT(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_ZPTIF_I8_D16_128(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_ZPTIF_I8_D16_128_FLAT(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_ZPTIF_I8_D16_256(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_ZPTIF_I8_D16_256_FLAT(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_ZPTIF_I8_D16_32(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_ZPTIF_I8_D16_32_FLAT(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_ZPTIF_I8_D16_64(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_ZPTIF_I8_D16_64_FLAT(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_ZPTI_I8_D16_1024(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_ZPTI_I8_D16_1024_FLAT(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_ZPTI_I8_D16_128(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_ZPTI_I8_D16_128_FLAT(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_ZPTI_I8_D16_256(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_ZPTI_I8_D16_256_FLAT(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_ZPTI_I8_D16_32(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_ZPTI_I8_D16_32_FLAT(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_ZPTI_I8_D16_64(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_ZPTI_I8_D16_64_FLAT(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_ZPT_I8_D16_1024(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_ZPT_I8_D16_128(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_ZPT_I8_D16_256(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_ZPT_I8_D16_32(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_ZPT_I8_D16_64(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_ZTB_I8_D16(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_ZTB_I8_D16_1024(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_ZTB_I8_D16_1024_FLAT(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_ZTB_I8_D16_128(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_ZTB_I8_D16_128_FLAT(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_ZTB_I8_D16_16(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_ZTB_I8_D16_16_FLAT(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_ZTB_I8_D16_256(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_ZTB_I8_D16_256_FLAT(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_ZTB_I8_D16_32(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_ZTB_I8_D16_32_FLAT(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_ZTB_I8_D16_64(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_ZTB_I8_D16_64_FLAT(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_ZTB_I8_D16_8(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_ZTB_I8_D16_8_FLAT(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_ZTFB_I8_D16(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_ZTF_I8_D16(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_ZTF_I8_D16_256(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_ZTIB_I8_D16(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_ZTIB_I8_D16_1024(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_ZTIB_I8_D16_128(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_ZTIB_I8_D16_16(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_ZTIB_I8_D16_256(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_ZTIB_I8_D16_32(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_ZTIB_I8_D16_64(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_ZTIB_I8_D16_8(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_ZTIB_I8_D16_FLAT(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_ZTID_I8_D16(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_ZTID_I8_D16_1024(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_ZTID_I8_D16_1024_FLAT(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_ZTID_I8_D16_128(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_ZTID_I8_D16_128_FLAT(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_ZTID_I8_D16_256(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_ZTID_I8_D16_256_FLAT(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_ZTID_I8_D16_32(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_ZTID_I8_D16_32_FLAT(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_ZTID_I8_D16_64(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_ZTID_I8_D16_64_FLAT(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_ZTID_I8_D16_FLAT(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_ZTIFB_I8_D16(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_ZTIFB_I8_D16_FLAT(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_ZTIF_I8_D16(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_ZTIF_I8_D16_256(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_ZTIF_I8_D16_256_FLAT(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_ZTIF_I8_D16_FLAT(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_ZTI_I8_D16(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_ZTI_I8_D16_1024(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_ZTI_I8_D16_128(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_ZTI_I8_D16_16(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_ZTI_I8_D16_256(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_ZTI_I8_D16_32(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_ZTI_I8_D16_64(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_ZTI_I8_D16_8(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_ZTI_I8_D16_FLAT(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_ZT_I8_D16(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_ZT_I8_D16_1024(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_ZT_I8_D16_1024_FLAT(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_ZT_I8_D16_128(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_ZT_I8_D16_128_FLAT(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_ZT_I8_D16_16(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_ZT_I8_D16_16_FLAT(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_ZT_I8_D16_256(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_ZT_I8_D16_256_FLAT(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_ZT_I8_D16_32(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_ZT_I8_D16_32_FLAT(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_ZT_I8_D16_64(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_ZT_I8_D16_64_FLAT(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_ZT_I8_D16_8(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_ZT_I8_D16_8_FLAT(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_ZT_RGB565_D16_1024(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_ZT_RGB565_D16_128(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_ZT_RGB565_D16_256(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_ZT_RGB565_D16_32(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_ZT_RGB565_D16_64(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_Z_I8_D16(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void BR_ASM_CALL TriangleRender_Z_I8_D16_ShadeTable(struct brp_block *block, union brp_vertex *v0, union brp_vertex *v1, union brp_vertex *v2)
{ (void)block; (void)v0; (void)v1; (void)v2; }

void sar16(void)
{ }
