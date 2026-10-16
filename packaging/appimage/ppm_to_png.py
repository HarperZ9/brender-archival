"""Write a PNG from a binary PPM (P6), for the AppImage icon. Standard library only.

    python packaging/appimage/ppm_to_png.py <in.ppm> <out.png>
"""
from __future__ import annotations

import struct
import sys
import zlib
from pathlib import Path


def chunk(kind: bytes, data: bytes) -> bytes:
    return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)


def main(src: str, dst: str) -> None:
    magic, size, maxval, pixels = Path(src).read_bytes().split(b"\n", 3)
    if magic != b"P6" or maxval != b"255":
        raise SystemExit(f"{src}: not an 8-bit binary PPM")
    w, h = (int(v) for v in size.split())
    rows = b"".join(b"\x00" + pixels[y * w * 3:(y + 1) * w * 3] for y in range(h))
    png = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(rows, 9)) + chunk(b"IEND", b"")
    Path(dst).write_bytes(png)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
