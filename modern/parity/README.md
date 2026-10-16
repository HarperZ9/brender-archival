# Pixel parity: the 1998 rasteriser against the modern one

The question is whether BRender 1.4, the modern 64-bit engine the downloads
use, draws the same pixels as Argonaut's BRender 1.3.2 from 1998.

**Answer on 16 October 2026: not measurable yet. The 1998 side, as this
repository builds it, does not draw these scenes correctly, so it cannot
serve as the reference.** The instrument is built, its controls work, and the
modern rasteriser is measured against itself across compilers. Those results
follow.

## The instrument

`parity-scene.c` draws seven untextured scenes at 320 x 240 into an RGB_888
buffer: a sphere, a torus and the teapot from the 1998 sample models, unlit,
lit flat and lit smooth (Gouraud), plus a control. Everything except the
rasteriser is shared: model, camera, transform, material, light and buffer.
Each side copies the renderer setup of its own ladder rung, which is known to
render.

| Side | Engine | Built by |
|---|---|---|
| period | BRender 1.3.2: softrend + pentprim, 32-bit, from the public source | `period/CMakeLists.txt` over the materialized harness |
| modern | BRender 1.4 (BlazingRenderer): softrend + softprim, 64-bit | `modern/CMakeLists.txt` (target `parity-scene`) |

`parity_compare.py` compares two runs scene by scene, over the pixels either
side drew:

- **coverage IoU**: pixels drawn in both, over pixels drawn in either;
- **identical**: the share of those pixels with the same three bytes;
- **MAD**: the mean absolute channel difference;
- **max**: the largest single channel difference.

The control compares the torus with the same torus turned 25 degrees, drawn
by the same side. It must come out unlike (coverage IoU under 0.9), or the
measure cannot tell scenes apart.

## Results, 16 October 2026

| Comparison | Scenes identical | Lowest coverage IoU | Worst channel difference | Control |
|---|---|---|---|---|
| modern, Linux GCC, two runs | 6 of 6 | 1.0 | 0 | fails, as required (0.60) |
| modern, Windows MSVC against Linux GCC | 3 of 6 | 1.0 | 1 level, on at most 0.02% of pixels | fails, as required |
| period 1.3.2 build, two runs | 3 of 6 (the three that draw nothing) | 0.9985 | 255 | cannot fail: the period build draws no flat scene |
| modern against period | 0 of 6 | 0.0 | 255 | fails, as required (modern side) |

Evidence: `evidence/*.json` and `evidence/period-left-modern-right-2026-10-16.png`
(period on the left, modern on the right).

What the period numbers show:

- **The flat and unlit paths draw nothing.** The sphere-flat, sphere-lit and
  torus-flat scenes are black.
- **The Gouraud path draws, but wrongly.** Shading saturates to white. There
  are holes where the depth test drops faces, and coverage IoU against the
  modern side is 0.60 to 0.76.
- **It is not deterministic.** Two runs differ on 0.04% to 0.25% of the
  drawn pixels.
- **The kernels are not Argonaut's.** The period build replaces BRender's
  x86 assembly kernels with C ports written in this project (in
  `engine-revival`'s harness, `compat/brender-pentprim-c-port.c`), and most of
  those ports are stubs. The port prints a record for every vertex it
  draws, and in the first run all 2,128 records had a screen x of zero.
  That fits the vertex layout mismatch already recorded for
  the textured path.

So the gap measures this project's unfinished C ports, not Argonaut's 1998
rasteriser. No parity claim is made in either direction.

What the modern numbers show: BRender 1.4's software rasteriser is
deterministic and draws the same coverage on Windows (MSVC) and on Linux
(GCC). Its Gouraud colours differ by one level on a handful of pixels, which
fits floating-point differences between the compilers.

## CI

- Every change runs the modern scenes twice on Windows and twice on Linux and
  requires identical bytes.
- It then compares Windows against Linux within the bounds measured above:
  coverage IoU 1.0, at least 99.9% identical pixels, at most 1 level. These
  bounds were set after measuring, so they are calibrated, not predicted.

The period comparison is not in CI. It becomes a CI gate when the period
build draws these scenes.

## Next

Fix the period C ports until the period side draws all seven scenes,
deterministically. Start with the vertex layout the rung prints. Then rerun
`modern against period`. The harness and its ports live in `engine-revival`,
so that work is a change there.
