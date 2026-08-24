/*
 * BRender v1.3.2 softrend FLOAT-build link fallbacks (harness-side).
 *
 * Provenance, verified against the pinned checkout at d88d0ed4:
 *
 *   - averageVertices / averageVerticesOnScreen / subdivideCheck exist as C
 *     implementations only under BASED_FIXED (faceops.c); the FLOAT build
 *     sourced them from subdiv.asm, one of the seven optional 386 assembly
 *     overlays this harness excludes.
 *   - The subdivision blocks that call them are added only when a primitive
 *     block sets BR_PRIMF_SUBDIVIDE (v1model.c), and NO primitive block in
 *     the pinned tree sets that flag. These symbols are therefore
 *     link-time-only for every reachable render path.
 *
 * The stubs below keep the library linkable and would be caught by any
 * future BR_PRIMF_SUBDIVIDE adoption; porting the float kernels faithfully
 * requires resolving a calling-convention discrepancy between faceops.c's
 * six-parameter declarations and subdiv.asm's seven-parameter procs.
 */

#define __BR_V1DB__ 1
#include "brender.h"

#include "drv.h"

br_boolean BR_ASM_CALL subdivideCheck(brp_vertex *v0, brp_vertex *v1, brp_vertex *v2)
{
    (void)v0; (void)v1; (void)v2;
    return BR_FALSE;
}

void BR_ASM_CALL averageVertices(
    struct br_renderer *renderer,
    brp_vertex *d1, brp_vertex *d2, brp_vertex *d3,
    brp_vertex *s1, brp_vertex *s2)
{
    (void)renderer; (void)d1; (void)d2; (void)d3; (void)s1; (void)s2;
}

void BR_ASM_CALL averageVerticesOnScreen(
    struct br_renderer *renderer,
    brp_vertex *d1, brp_vertex *d2, brp_vertex *d3,
    brp_vertex *s1, brp_vertex *s2)
{
    (void)renderer; (void)d1; (void)d2; (void)d3; (void)s1; (void)s2;
}
