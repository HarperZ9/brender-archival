"""Draw The Keeper's Hour's textures and write them as 128 x 128 PPM files.

    python games/keepers-hour/tools/make_art.py            # write data/art/
    python games/keepers-hour/tools/make_art.py --check    # fail if any file is stale

The pictures are drawn by this script, stroke by stroke, from a fixed seed, so
the same script always writes the same bytes and a test can hold the files to
it. Standard library only. The pictures are CC BY 4.0 (Zain Dana Harper); the
script is MIT.

No pixel is pure black: BRender treats black texels as transparent by default.
"""
from __future__ import annotations

import math
import random
import sys
from pathlib import Path

SIZE = 128
OUT = Path(__file__).resolve().parents[1] / "data" / "art"


class Canvas:
    def __init__(self, colour):
        self.px = [[list(colour) for _ in range(SIZE)] for _ in range(SIZE)]

    def put(self, x, y, colour, alpha=1.0):
        x, y = int(x) % SIZE, int(y)
        if 0 <= y < SIZE:
            p = self.px[y][x]
            for i in range(3):
                p[i] = p[i] + (colour[i] - p[i]) * alpha

    def line(self, x0, y0, x1, y1, colour, alpha=1.0):
        steps = int(max(abs(x1 - x0), abs(y1 - y0))) + 1
        for s in range(steps + 1):
            t = s / steps
            self.put(x0 + (x1 - x0) * t, y0 + (y1 - y0) * t, colour, alpha)

    def rect(self, x0, y0, x1, y1, colour, alpha=1.0):
        for y in range(int(y0), int(y1)):
            for x in range(int(x0), int(x1)):
                self.put(x, y, colour, alpha)

    def disc(self, cx, cy, r, colour, alpha=1.0):
        for y in range(int(cy - r), int(cy + r) + 1):
            for x in range(int(cx - r), int(cx + r) + 1):
                if (x - cx) ** 2 + (y - cy) ** 2 <= r * r:
                    self.put(x, y, colour, alpha)

    def grain(self, rng, amount):
        for row in self.px:
            for p in row:
                n = rng.uniform(-amount, amount)
                for i in range(3):
                    p[i] += n

    def ppm(self) -> bytes:
        body = bytearray()
        for row in self.px:
            for p in row:
                body += bytes(max(4, min(255, round(c))) for c in p)
        return f"P6\n{SIZE} {SIZE}\n255\n".encode() + bytes(body)


def boards(rng):
    c = Canvas((88, 62, 42))
    for b in range(0, SIZE, 16):  # eight planks, each its own tone
        tone = rng.uniform(-10, 10)
        c.rect(0, b, SIZE, b + 16, (88 + tone, 62 + tone * 0.7, 42 + tone * 0.5))
        c.line(0, b, SIZE, b, (52, 36, 24))
        for g in range(5):  # grain lines run along the plank
            y = b + rng.uniform(2, 14)
            phase = rng.uniform(0, 6.28)
            for x in range(SIZE):
                c.put(x, y + math.sin(x / 9 + phase) * 1.2, (70, 48, 32), 0.5)
        c.disc(rng.uniform(10, 118), b + 8, 1.4, (60, 40, 26))  # nail
    c.grain(rng, 4)
    return c


def stone(rng):
    c = Canvas((116, 108, 96))
    for row in range(0, SIZE, 32):
        off = 0 if (row // 32) % 2 == 0 else 32
        for col in range(-1, 3):
            x0 = col * 64 + off
            tone = rng.uniform(-12, 12)
            c.rect(x0 + 2, row + 2, x0 + 62, row + 30, (116 + tone, 108 + tone, 96 + tone))
        c.line(0, row, SIZE, row, (78, 72, 64))
        for col in range(3):
            x = col * 64 + off
            c.line(x, row, x, row + 32, (78, 72, 64))
    c.grain(rng, 7)
    return c


def sea_chart(rng):
    c = Canvas((214, 204, 170))
    for k in range(9):  # contour lines of a sea that is now fields
        r0 = 18 + k * 12
        phase = rng.uniform(0, 6.28)
        pts = [(64 + (r0 + 6 * math.sin(a * 3 + phase)) * math.cos(a), 98 + (r0 + 6 * math.sin(a * 3 + phase)) * 0.55 * math.sin(a))
               for a in [i * math.pi / 60 for i in range(121)]]
        for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
            c.line(x0, y0, x1, y1, (110, 128, 150), 0.7)
    for _ in range(40):  # sounding figures, small crosses
        x, y = rng.uniform(8, 120), rng.uniform(40, 124)
        c.line(x - 1, y, x + 1, y, (90, 80, 70))
        c.line(x, y - 1, x, y + 1, (90, 80, 70))
    c.disc(40, 30, 3, (150, 40, 34))  # the tower: a star in red
    for a in range(8):
        c.line(40, 30, 40 + 7 * math.cos(a * math.pi / 4), 30 + 7 * math.sin(a * math.pi / 4), (150, 40, 34))
    c.grain(rng, 5)
    return c


def painting_tower(rng):
    c = Canvas((40, 52, 86))
    for y in range(64, SIZE):  # the sea, when there was one
        for x in range(SIZE):
            c.put(x, y, (30 + y * 0.2, 60 + y * 0.2, 96), 1.0)
    for _ in range(300):
        x, y = rng.uniform(0, 128), rng.uniform(66, 128)
        c.line(x, y, x + rng.uniform(3, 9), y, (90, 120, 150), 0.6)
    c.rect(78, 26, 90, 70, (206, 196, 176))  # the tower
    c.rect(76, 20, 92, 26, (60, 60, 64))
    for k in range(12):  # the lamp: every colour in a ring, a dark dot inside
        a = k * math.pi / 6
        hue = [(240, 90, 80), (240, 200, 90), (120, 220, 120), (100, 180, 240), (200, 120, 230), (250, 250, 230)][k % 6]
        c.disc(84 + 4 * math.cos(a), 17 + 4 * math.sin(a), 1.6, hue)
    c.disc(84, 17, 1.2, (24, 24, 30))
    c.line(14, 100, 30, 100, (70, 50, 30))  # lower left: the yellow sail
    c.line(22, 100, 22, 84, (70, 50, 30))
    for y in range(84, 99):
        c.line(23, y, 23 + (y - 84) * 0.6, y, (236, 200, 70))
    c.disc(18, 97, 1.2, (230, 220, 200))  # someone waving
    c.grain(rng, 5)
    return c


def portrait(rng):
    c = Canvas((56, 46, 40))
    c.disc(64, 50, 20, (196, 160, 134))  # face
    c.rect(34, 72, 94, 128, (40, 58, 92))  # keeper's coat
    for k in range(5):  # buttons, done up one off
        c.disc(64 + (3 if k else 0), 82 + k * 9, 2, (200, 160, 70))
    c.line(56, 46, 60, 46, (60, 40, 30))
    c.line(68, 46, 72, 46, (60, 40, 30))
    c.line(58, 60, 70, 60, (120, 70, 60))
    for _ in range(140):  # loose brushwork around her
        x, y = rng.uniform(0, 128), rng.uniform(0, 128)
        if (x - 64) ** 2 + (y - 50) ** 2 > 22 ** 2 and not (34 <= x <= 94 and y > 72):
            c.line(x, y, x + rng.uniform(-6, 6), y + rng.uniform(-6, 6), (90, 70, 56), 0.4)
    c.grain(rng, 4)
    return c


def photograph(rng):
    c = Canvas((176, 156, 120))
    c.rect(0, 70, SIZE, 72, (240, 236, 220))  # the sea, just: a thin bright line
    c.rect(0, 72, SIZE, SIZE, (150, 130, 98))
    c.rect(58, 52, 70, 100, (70, 60, 50))  # you, holding the keys
    c.disc(64, 46, 6, (200, 176, 144))
    c.disc(72, 74, 2, (230, 210, 120))
    for _ in range(30):  # gulls
        x, y = rng.uniform(4, 124), rng.uniform(6, 50)
        c.line(x - 2, y, x, y - 1, (110, 96, 76))
        c.line(x, y - 1, x + 2, y, (110, 96, 76))
    c.grain(rng, 8)
    return c


def letter(rng):
    c = Canvas((236, 230, 212))
    c.rect(10, 10, 60, 16, (60, 60, 70), 0.8)  # the Authority's heading
    for row in range(26, 120, 7):
        width = rng.uniform(70, 108)
        c.line(10, row, 10 + width, row, (90, 90, 100), 0.6)
    c.disc(100, 110, 8, (200, 150, 60), 0.5)  # marmalade
    c.grain(rng, 3)
    return c


ART = {
    "boards": boards,
    "stone": stone,
    "chart": sea_chart,
    "painting-tower": painting_tower,
    "portrait": portrait,
    "photograph": photograph,
    "letter": letter,
}


def render() -> dict[str, bytes]:
    return {name: draw(random.Random(f"keepers-hour/{name}")).ppm() for name, draw in ART.items()}


def main(argv: list[str]) -> int:
    images = render()
    if "--check" in argv:
        stale = [n for n, data in images.items() if not (OUT / f"{n}.ppm").is_file() or (OUT / f"{n}.ppm").read_bytes() != data]
        for n in stale:
            print(f"stale: data/art/{n}.ppm")
        return 1 if stale else 0
    OUT.mkdir(parents=True, exist_ok=True)
    for name, data in images.items():
        (OUT / f"{name}.ppm").write_bytes(data)
        print(f"wrote data/art/{name}.ppm")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
