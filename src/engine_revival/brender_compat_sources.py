from __future__ import annotations


def vector_smoke_source() -> str:
    return """#define _NO_VECTOR_MACROS 1
#include "brender.h"

int main(void)
{
    br_vector3 vector;

    BrVector3SetFloat(&vector, 1.0f, 2.0f, 3.0f);
    if (BrScalarToFloat(vector.v[2]) != 3.0f) {
        return 1;
    }

    if (BrScalarToFloat(vector.v[0]) != 1.0f) {
        return 2;
    }

    return 0;
}
"""


def startup_smoke_source() -> str:
    return """#define __BR_V1DB__ 0
#include "brender.h"

int main(void)
{
    if (BrBegin() != BRE_OK) {
        return 1;
    }

    if (BrBegin() != BRE_ALLREADY_ACTIVE) {
        BrEnd();
        return 2;
    }

    if (BrEnd() != BRE_OK) {
        return 3;
    }

    if (BrEnd() != BRE_NOT_ACTIVE) {
        return 4;
    }

    return 0;
}
"""


def portable_core_stubs_source() -> str:
    return r"""#define __BR_V1DB__ 0
#include "brender.h"

#include <string.h>

void BR_RESIDENT_ENTRY _PRO(void)
{
}

void BR_RESIDENT_ENTRY _EPI(void)
{
}

static br_uint_8 empty_widths[] = {0};
static br_uint_8 empty_glyphs[] = {0};

struct br_font BR_ASM_DATA _FontFixed3x5 = {
    0, 0, 0, 0, 0, empty_widths, NULL, empty_glyphs
};
struct br_font BR_ASM_DATA _FontProp4x6 = {
    BR_FONTF_PROPORTIONAL, 0, 0, 0, 0, empty_widths, NULL, empty_glyphs
};
struct br_font BR_ASM_DATA _FontProp7x9 = {
    BR_FONTF_PROPORTIONAL, 0, 0, 0, 0, empty_widths, NULL, empty_glyphs
};

static br_size_t pixel_bytes(br_uint_32 pixels, br_uint_32 bpp)
{
    return (br_size_t)(pixels * bpp);
}

static br_uint_32 read_pixel(char *src, br_uint_32 bytes)
{
    br_uint_32 colour = 0;
    br_uint_32 i;

    for (i = 0; i < bytes && i < sizeof(colour); i++) {
        colour |= ((br_uint_32)(br_uint_8)src[i]) << (i * 8);
    }
    return colour;
}

static void write_pixel(char *dest, br_uint_32 bytes, br_uint_32 colour)
{
    br_uint_32 i;

    for (i = 0; i < bytes && i < sizeof(colour); i++) {
        dest[i] = (char)((colour >> (i * 8)) & 0xff);
    }
}

static void copy_source_colour_key0(char *dest, char *src, br_uint_32 pixels, br_uint_32 bpp)
{
    br_uint_32 i;

    for (i = 0; i < pixels; i++) {
        char *pixel = src + pixel_bytes(i, bpp);
        if (read_pixel(pixel, bpp) != 0) {
            write_pixel(dest + pixel_bytes(i, bpp), bpp, read_pixel(pixel, bpp));
        }
    }
}

void BR_ASM_CALL _MemCopyBits_A(
    char *dest, br_uint_32 dest_qual, br_int_32 d_stride,
    br_uint_8 *src, br_uint_32 s_stride, br_uint_32 start_bit,
    br_uint_32 end_bit, br_uint_32 nrows, br_uint_32 bpp,
    br_uint_32 colour)
{
    br_uint_32 row;
    br_uint_32 bit;

    (void)dest_qual;
    for (row = 0; row < nrows; row++) {
        for (bit = start_bit; bit < end_bit; bit++) {
            br_uint_8 mask = (br_uint_8)(0x80 >> (bit & 7));
            if (src[bit >> 3] & mask) {
                write_pixel(dest + pixel_bytes(bit - start_bit, bpp), bpp, colour);
            }
        }
        dest += d_stride;
        src += s_stride;
    }
}

void BR_ASM_CALL _MemFill_A(
    char *dest, br_uint_32 dest_qual, br_uint_32 pixels,
    br_uint_32 bpp, br_uint_32 colour)
{
    br_uint_32 i;

    (void)dest_qual;
    for (i = 0; i < pixels; i++) {
        write_pixel(dest + pixel_bytes(i, bpp), bpp, colour);
    }
}

void BR_ASM_CALL _MemRectFill_A(
    char *dest, br_uint_32 dest_qual, br_uint_32 pwidth,
    br_uint_32 pheight, br_int_32 d_stride, br_uint_32 bpp,
    br_uint_32 colour)
{
    br_uint_32 row;

    for (row = 0; row < pheight; row++) {
        _MemFill_A(dest, dest_qual, pwidth, bpp, colour);
        dest += d_stride;
    }
}

void BR_ASM_CALL _MemCopy_A(
    char *dest, br_uint_32 dest_qual, char *src,
    br_uint_32 src_qualifier, br_uint_32 pixels, br_uint_32 bpp)
{
    (void)dest_qual;
    (void)src_qualifier;
    memmove(dest, src, pixel_bytes(pixels, bpp));
}

void BR_ASM_CALL _MemRectCopy_A(
    char *dest, br_uint_32 dest_qual, char *src, br_uint_32 src_qualifier,
    br_uint_32 pwidth, br_uint_32 pheight, br_int_32 d_stride,
    br_int_32 s_stride, br_uint_32 bpp)
{
    br_uint_32 row;

    for (row = 0; row < pheight; row++) {
        _MemCopy_A(dest, dest_qual, src, src_qualifier, pwidth, bpp);
        dest += d_stride;
        src += s_stride;
    }
}

void BR_ASM_CALL _MemRectCopySourceColourKey0_A(
    char *dest, br_uint_32 dest_qual, char *src, br_uint_32 src_qualifier,
    br_uint_32 pwidth, br_uint_32 pheight, br_int_32 d_stride,
    br_int_32 s_stride, br_uint_32 bpp)
{
    br_uint_32 row;

    for (row = 0; row < pheight; row++) {
        (void)dest_qual;
        (void)src_qualifier;
        copy_source_colour_key0(dest, src, pwidth, bpp);
        dest += d_stride;
        src += s_stride;
    }
}

void BR_ASM_CALL _MemCopySourceColourKey0_A(
    char *dest, br_uint_32 dest_qual, char *src,
    br_uint_32 src_qualifier, br_uint_32 pixels, br_uint_32 bpp)
{
    (void)dest_qual;
    (void)src_qualifier;
    copy_source_colour_key0(dest, src, pixels, bpp);
}

void BR_ASM_CALL _MemPixelSet(
    char *dest, br_uint_32 dest_qual, br_uint_32 bytes, br_uint_32 colour)
{
    (void)dest_qual;
    write_pixel(dest, bytes, colour);
}

br_uint_32 BR_ASM_CALL _MemPixelGet(
    char *dest, br_uint_32 dest_qual, br_uint_32 bytes)
{
    (void)dest_qual;
    return read_pixel(dest, bytes);
}

br_uint_16 BR_ASM_CALL _GetSysQual(void)
{
    return 0;
}

void BR_ASM_CALL _MemFillFPU_A(
    char *dest, br_uint_32 dest_qual, br_uint_32 pixels,
    br_uint_32 bpp, br_uint_32 colour)
{
    _MemFill_A(dest, dest_qual, pixels, bpp, colour);
}

void BR_ASM_CALL _MemRectFillFPU_A(
    char *dest, br_uint_32 dest_qual, br_uint_32 pwidth,
    br_uint_32 pheight, br_uint_32 stride, br_uint_32 bpp,
    br_uint_32 colour)
{
    _MemRectFill_A(dest, dest_qual, pwidth, pheight, stride, bpp, colour);
}

void BR_ASM_CALL _MemCopyFPU_A(
    char *dest, br_uint_32 dest_qual, char *src,
    br_uint_32 src_qualifier, br_uint_32 pixels, br_uint_32 bpp)
{
    _MemCopy_A(dest, dest_qual, src, src_qualifier, pixels, bpp);
}

void BR_ASM_CALL _MemRectCopyFPU_A(
    char *dest, br_uint_32 dest_qual, char *src, br_uint_32 src_qualifier,
    br_uint_32 pwidth, br_uint_32 pheight, br_uint_32 d_stride,
    br_uint_32 s_stride, br_uint_32 bpp)
{
    _MemRectCopy_A(
        dest, dest_qual, src, src_qualifier, pwidth, pheight,
        (br_int_32)d_stride, (br_int_32)s_stride, bpp);
}
"""
