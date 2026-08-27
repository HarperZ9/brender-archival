from __future__ import annotations

from PIL import Image, ImageDraw

from scripts.generate_brender_release_media import (
    PIPELINE_BOUNDARY_TEXT,
    PIPELINE_BOUNDARY_TEXT_BOX,
    _font,
    _wrap_lines,
)


def test_pipeline_boundary_text_wraps_inside_release_box():
    image = Image.new("RGB", (1280, 720))
    draw = ImageDraw.Draw(image)
    font = _font(18)
    x0, y0, x1, y1 = PIPELINE_BOUNDARY_TEXT_BOX
    lines = _wrap_lines(draw, PIPELINE_BOUNDARY_TEXT, font, x1 - x0)

    assert len(lines) >= 2
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        assert bbox[2] - bbox[0] <= x1 - x0

    line_height = draw.textbbox((0, 0), "Ag", font=font)[3]
    total_height = line_height * len(lines) + 8 * (len(lines) - 1)
    assert y0 + total_height <= y1
