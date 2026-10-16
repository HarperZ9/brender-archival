# Pixel parity: the 1998 rasteriser against the modern one

The question is whether BRender 1.4, the modern 64-bit engine the downloads
use, draws the same pixels as Argonaut's BRender 1.3.2 from 1998.

**Answer on 16 October 2026, for the untextured scenes measured here: almost.
Silhouettes match to a coverage IoU of 0.9993 or better, 90.7% to 100% of
pixels are identical, and the mean difference is under 0.2 levels. The 1998
build gives the same bytes on every run.** Texturing is not measured: the
period build's textured path is still open.

## The instrument

`parity-scene.c` draws seven untextured scenes at 320 x 240 into an RGB_888
buffer: a sphere, a torus and the teapot from the 1998 sample models, unlit,
lit flat and lit smooth (Gouraud), plus a control. Everything except the
rasteriser is shared: model, camera, transform, material, light and buffer.
Each side copies the renderer setup of its own ladder rung.

| Side | Engine | Built by |
|---|---|---|
| period | BRender 1.3.2: softrend + pentprim, 32-bit, from the public source | `period/CMakeLists.txt` over the harness from engine-revival 0.4.0 |
| modern | BRender 1.4 (BlazingRenderer): softrend + softprim, 64-bit | `modern/CMakeLists.txt` (target `parity-scene`) |

BRender's 1998 rasterisers are x86 assembly. The period build replaces the
ones these scenes use (`RawTriangle_PIZ2_RGB_888` and
`RawTriangle_PIZ2I_RGB_888` in `tt24_piz.asm`) with engine-revival 0.4.0's
line-by-line C port. The port keeps the assembly's fixed-point setup, its
edge stepping, its truncating divides and its depth test. So "period" means
the 1998 algorithm, run through a C port, not the 1998 binary.

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

| Comparison | Scenes identical | Lowest coverage IoU | Lowest identical | Highest MAD | Control |
|---|---|---|---|---|---|
| period 1.3.2, two runs (Win32) | 6 of 6 | 1.0 | 1.0 | 0 | fails, as required |
| modern 1.4, two runs (Linux) | 6 of 6 | 1.0 | 1.0 | 0 | fails, as required |
| modern Windows MSVC against modern Linux GCC | 3 of 6 | 1.0 | 0.9998 | 0.0 | fails, as required |
| modern (Linux) against period | 1 of 6 | 0.9993 | 0.907 | 0.174 | fails, as required (0.60) |
| modern (Windows) against period | 1 of 6 | 0.9993 | 0.907 | 0.174 | fails, as required |

| Scene, modern against period | Coverage IoU | Identical | MAD | Max |
|---|---|---|---|---|
| sphere-flat (unlit) | 0.9998 | 0.9998 | 0.032 | 199 |
| sphere-lit (flat lit) | 0.9998 | 0.9583 | 0.065 | 159 |
| sphere-smooth (Gouraud) | 0.9998 | 0.9070 | 0.072 | 153 |
| torus-flat | 1.0 | 1.0 | 0.0 | 0 |
| torus-smooth | 1.0 | 0.9348 | 0.035 | 15 |
| teapot-smooth | 0.9993 | 0.9215 | 0.174 | 91 |

The two engines draw the same silhouettes. The unlit torus is the same to the
byte. The 1998 edge rule draws a few pixels more along some edges (6 on the
sphere, 6 on the teapot). Pixels more than 20 levels apart number 6 on the
unlit and smooth spheres, all of them on those edges; 36 on the flat-lit
sphere and 20 on the teapot, 6 of each on edges and the rest inside. The
Gouraud scenes differ by small rounding over larger areas (MAD under 0.2
levels), which fits the 1998 16.16 fixed-point stepping against 1.4's own
arithmetic. These are measured differences, not a judgement that either side
is wrong.

Evidence: `evidence/*.json` and `evidence/period-left-modern-right-2026-10-16.png`
(period on the left, modern on the right).

### Before the port (same day, kept for the record)

The first measurement, before engine-revival 0.4.0, found the period build
unusable as a reference:

- the flat and unlit scenes drew nothing;
- the Gouraud scenes saturated to white with holes (coverage IoU 0.60 to
  0.76);
- runs differed on up to 0.25% of pixels.

The cause was in the C port, not in the 1998 engine. The port redefined
BRender's component slots (`C_SX` and the rest) as 0 to 8 with `#ifndef`,
which shadowed the real enum, so its kernels read the wrong vertex data. The
Gouraud kernel also interpolated the wrong slot, shifted colour by 8 bits
instead of 16, and inverted the depth test. Those records are in this
repository's history at commit `cb238d7`.

## CI

Every change:

- runs the period scenes twice (Win32) and the modern scenes twice on Windows
  and on Linux, and requires identical bytes each time;
- compares modern Windows against modern Linux within coverage IoU 1.0, at
  least 99.9% identical pixels and at most 1 level;
- compares modern against period within coverage IoU 0.999, at least 90%
  identical pixels and a MAD of at most 0.25.

All bounds were set from the measurements above, so they are calibrated, not
predicted.

## Not measured yet

- Textured scenes: the period build's textured path does not apply the
  texture yet.
- Palette (8-bit) and 15/16-bit targets: only RGB_888 is ported.
- OpenGL against software.
