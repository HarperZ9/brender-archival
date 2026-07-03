from __future__ import annotations

from engine_revival.brender_host_tail_sources import host_tail_stubs_source


def portable_host_stubs_source() -> str:
    return r"""#define __BR_V1DB__ 0
#include "brender.h"
#include "host.h"
#include "host_ip.h"

#include <string.h>

br_uint_16 _RealSelector = 0;

static void clear_host_regs(union host_regs *regs)
{
    if (regs != NULL) {
        memset(regs, 0, sizeof(*regs));
    }
}

static void zero_real_interrupt(br_uint_16 *offset, br_uint_16 *segment)
{
    if (offset != NULL) {
        *offset = 0;
    }
    if (segment != NULL) {
        *segment = 0;
    }
}

static void zero_protected_interrupt(br_uint_32 *offset, br_uint_16 *selector)
{
    if (offset != NULL) {
        *offset = 0;
    }
    if (selector != NULL) {
        *selector = 0;
    }
}

br_error BR_ASM_CALL RealSelectorBegin(void)
{
    return BRE_OK;
}

void BR_ASM_CALL RealSelectorEnd(void)
{
}

void BR_ASM_CALL CPUInfo(br_token *cpu_type, br_uint_32 *features)
{
    if (cpu_type != NULL) {
        *cpu_type = BRT_INTEL_386;
    }
    if (features != NULL) {
        *features = 0;
    }
}

br_error BR_RESIDENT_ENTRY HostRealAllocate(
    struct host_real_memory *mem,
    br_uint_32 size)
{
    (void)size;
    if (mem != NULL) {
        memset(mem, 0, sizeof(*mem));
    }
    return BRE_UNSUPPORTED;
}

br_error BR_RESIDENT_ENTRY HostRealFree(struct host_real_memory *mem)
{
    if (mem != NULL) {
        memset(mem, 0, sizeof(*mem));
    }
    return BRE_OK;
}

br_error BR_RESIDENT_ENTRY HostRealInterruptGet(
    br_uint_8 vector,
    br_uint_16 *offp,
    br_uint_16 *vsegp)
{
    (void)vector;
    zero_real_interrupt(offp, vsegp);
    return BRE_UNSUPPORTED;
}

br_error BR_RESIDENT_ENTRY HostRealInterruptSet(
    br_uint_8 vector,
    br_uint_16 voff,
    br_uint_16 vseg)
{
    (void)vector;
    (void)voff;
    (void)vseg;
    return BRE_UNSUPPORTED;
}

br_error BR_RESIDENT_ENTRY HostRealInterruptCall(
    br_uint_8 vector,
    union host_regs *regs)
{
    (void)vector;
    clear_host_regs(regs);
    return BRE_UNSUPPORTED;
}

void BR_RESIDENT_ENTRY HostRealBlockWrite(
    br_uint_16 offset,
    br_uint_16 seg,
    void *block,
    br_uint_32 count)
{
    (void)offset;
    (void)seg;
    (void)block;
    (void)count;
}

void BR_RESIDENT_ENTRY HostRealBlockRead(
    br_uint_16 offset,
    br_uint_16 seg,
    void *block,
    br_uint_32 count)
{
    (void)offset;
    (void)seg;
    if (block != NULL) {
        memset(block, 0, count);
    }
}

br_uint_32 BR_RESIDENT_ENTRY HostRealStringWrite(
    br_uint_16 offset,
    br_uint_16 seg,
    br_uint_8 *string,
    br_uint_32 max)
{
    (void)offset;
    (void)seg;
    (void)string;
    (void)max;
    return 0;
}

br_uint_32 BR_RESIDENT_ENTRY HostRealStringRead(
    br_uint_16 offset,
    br_uint_16 seg,
    br_uint_8 *string,
    br_uint_32 max)
{
    (void)offset;
    (void)seg;
    if (string != NULL && max > 0) {
        string[0] = 0;
    }
    return 0;
}

void BR_RESIDENT_ENTRY HostRealBlockFill(
    br_uint_16 offset,
    br_uint_16 seg,
    br_uint_8 value,
    br_uint_32 count)
{
    (void)offset;
    (void)seg;
    (void)value;
    (void)count;
}

#define DEFINE_REAL_WRITE_STUB(name, type) \
void BR_RESIDENT_ENTRY name(br_uint_16 offset, br_uint_16 seg, type value) \
{ (void)offset; (void)seg; (void)value; }

#define DEFINE_REAL_READ_STUB(name, type) \
type BR_RESIDENT_ENTRY name(br_uint_16 offset, br_uint_16 seg) \
{ (void)offset; (void)seg; return 0; }

DEFINE_REAL_WRITE_STUB(HostRealByteWrite, br_uint_8)
DEFINE_REAL_WRITE_STUB(HostRealWordWrite, br_uint_16)
DEFINE_REAL_WRITE_STUB(HostRealDWordWrite, br_uint_32)
DEFINE_REAL_READ_STUB(HostRealByteRead, br_uint_8)
DEFINE_REAL_READ_STUB(HostRealWordRead, br_uint_16)
DEFINE_REAL_READ_STUB(HostRealDWordRead, br_uint_32)

br_error BR_RESIDENT_ENTRY HostInterruptCall(
    br_uint_8 vector,
    union host_regs *regs)
{
    (void)vector;
    clear_host_regs(regs);
    return BRE_UNSUPPORTED;
}

br_error BR_RESIDENT_ENTRY HostRegistersGet(union host_regs *regs)
{
    clear_host_regs(regs);
    return BRE_OK;
}

#define DEFINE_SELECTOR_STUB(name, value) \
br_error BR_RESIDENT_ENTRY name(br_uint_16 *selp) \
{ if (selp != NULL) { *selp = (value); } return BRE_OK; }

DEFINE_SELECTOR_STUB(HostSelectorReal, _RealSelector)
DEFINE_SELECTOR_STUB(HostSelectorDS, 0)
DEFINE_SELECTOR_STUB(HostSelectorCS, 0)
DEFINE_SELECTOR_STUB(HostSelectorSS, 0)
DEFINE_SELECTOR_STUB(HostSelectorES, 0)
""" + host_tail_stubs_source()
