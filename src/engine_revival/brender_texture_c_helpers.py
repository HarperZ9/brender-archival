from __future__ import annotations


def texture_colour_helpers_source() -> str:
    """C helpers for generated software texture sampling rungs."""
    return r"""

static br_uint_32 resolve_texel_colour(br_pixelmap *tex, int x, int y)
{
    br_uint_32 texel = BrPixelmapPixelGet(tex, x, y);
    switch (tex->type) {
    case BR_PMT_INDEX_8:
        if (tex->map != NULL) {
            return BrPixelmapPixelGet(tex->map, 0, texel);
        }
        return texel;
    default:
        return texel;
    }
}
"""
