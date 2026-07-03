from __future__ import annotations


def host_tail_stubs_source() -> str:
    return r"""
void BR_RESIDENT_ENTRY HostFarBlockWrite(
    br_uint_32 offset,
    br_uint_16 sel,
    void *block,
    br_uint_32 count)
{
    (void)offset;
    (void)sel;
    (void)block;
    (void)count;
}

void BR_RESIDENT_ENTRY HostFarBlockRead(
    br_uint_32 offset,
    br_uint_16 sel,
    void *block,
    br_uint_32 count)
{
    (void)offset;
    (void)sel;
    if (block != NULL) {
        memset(block, 0, count);
    }
}

br_uint_32 BR_RESIDENT_ENTRY HostFarStringWrite(
    br_uint_32 offset,
    br_uint_16 sel,
    br_uint_8 *string,
    br_uint_32 max)
{
    (void)offset;
    (void)sel;
    (void)string;
    (void)max;
    return 0;
}

br_uint_32 BR_RESIDENT_ENTRY HostFarStringRead(
    br_uint_32 offset,
    br_uint_16 sel,
    br_uint_8 *string,
    br_uint_32 max)
{
    (void)offset;
    (void)sel;
    if (string != NULL && max > 0) {
        string[0] = 0;
    }
    return 0;
}

void BR_RESIDENT_ENTRY HostFarBlockFill(
    br_uint_32 offset,
    br_uint_16 sel,
    br_uint_8 value,
    br_uint_32 count)
{
    (void)offset;
    (void)sel;
    (void)value;
    (void)count;
}

#define DEFINE_FAR_WRITE_STUB(name, type) \
void BR_RESIDENT_ENTRY name(br_uint_32 offset, br_uint_16 sel, type value) \
{ (void)offset; (void)sel; (void)value; }

#define DEFINE_FAR_READ_STUB(name, type) \
type BR_RESIDENT_ENTRY name(br_uint_32 offset, br_uint_16 sel) \
{ (void)offset; (void)sel; return 0; }

DEFINE_FAR_WRITE_STUB(HostFarByteWrite, br_uint_8)
DEFINE_FAR_WRITE_STUB(HostFarWordWrite, br_uint_16)
DEFINE_FAR_WRITE_STUB(HostFarDWordWrite, br_uint_32)
DEFINE_FAR_READ_STUB(HostFarByteRead, br_uint_8)
DEFINE_FAR_READ_STUB(HostFarWordRead, br_uint_16)
DEFINE_FAR_READ_STUB(HostFarDWordRead, br_uint_32)

br_error BR_RESIDENT_ENTRY HostInterruptGet(
    br_uint_8 vector,
    br_uint_32 *offp,
    br_uint_16 *selp)
{
    (void)vector;
    zero_protected_interrupt(offp, selp);
    return BRE_UNSUPPORTED;
}

br_error BR_RESIDENT_ENTRY HostInterruptSet(
    br_uint_8 vector,
    br_uint_32 off,
    br_uint_16 sel)
{
    (void)vector;
    (void)off;
    (void)sel;
    return BRE_UNSUPPORTED;
}

br_error BR_RESIDENT_ENTRY HostExceptionGet(
    br_uint_8 exception,
    br_uint_32 *offp,
    br_uint_16 *selp)
{
    (void)exception;
    zero_protected_interrupt(offp, selp);
    return BRE_UNSUPPORTED;
}

br_error BR_RESIDENT_ENTRY HostExceptionSet(
    br_uint_8 exception,
    br_uint_32 off,
    br_uint_16 sel)
{
    (void)exception;
    (void)off;
    (void)sel;
    return BRE_UNSUPPORTED;
}
"""
