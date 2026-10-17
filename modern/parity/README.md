# Pixel parity: the 1998 rasteriser against the modern one

The question is whether BRender 1.4, the modern 64-bit engine the downloads
use, draws the same pixels as Argonaut's BRender 1.3.2 from 1998.

**Answer on 16 October 2026, for the twenty scenes measured here: almost,
with one 1998 defect.**
- **24-bit untextured:** silhouettes match to a coverage IoU of 0.9993 or
  better, 90.7% to 100% of pixels are identical, and the mean difference is
  under 0.2 levels.
- **24-bit textured:** coverage IoU is 0.9992 or better, 95.7% to 99.7% of
  pixels are identical, and the mean difference is at most 1.09 levels.
- **8-bit, through the palette:** coverage IoU is 0.9983 or better, 96.4% to
  99.9% of pixels carry the same palette index, and the mean difference is at
  most 0.43 levels. This covers unlit, flat, Gouraud, textured and lit
  textured scenes.
- **24-bit lit textured:** the 1998 kernel reads its shade table at the wrong
  stride, so as shipped it draws garbage (see
  [A 1998 defect](#a-1998-defect-the-24-bit-lit-textured-kernel)). With the
  table laid at the stride it reads, it matches: coverage IoU 0.9998 or
  better, 97.9% and 99.5% identical.

The 1998 build gives the same bytes on every run.

## The instrument

`parity-scene.c` draws twenty scenes and a control at 320 x 240, from the
1998 sample models. Eleven draw into an RGB_888 buffer:

- six untextured: a sphere, a torus and the teapot, unlit, lit flat and lit
  smooth (Gouraud);
- three textured and unlit: the sphere with `earth.pix` at two angles, and
  the torus with `rosewood.pix`, each expanded through `std.pal` into an
  RGB_888 map;
- two lit textured: the sphere and the torus with their 8-bit maps, lit
  through `shade.tab` expanded through `std.pal` into an RGB_888 shade table.

Nine draw into an INDEX_8 buffer through `std.pal`, BRender's 8-bit palette
path: five untextured (each on its own palette ramp), two textured unlit and
two textured lit through `shade.tab`. Each 8-bit scene writes the indices
(`.pgm`) and the colours they map to (`.ppm`); the comparison counts a pixel
identical when the index is the same.

The control is described below. Everything except the
rasteriser is shared: model, camera, transform, material, light and buffer.
Each side copies the renderer setup of its own ladder rung.

| Side | Engine | Built by |
|---|---|---|
| period | BRender 1.3.2: softrend + pentprim, 32-bit, from the public source | `period/CMakeLists.txt` over the harness from engine-revival 0.6.0 |
| modern | BRender 1.4 (BlazingRenderer): softrend + softprim, 64-bit | `modern/CMakeLists.txt` (target `parity-scene`) |

BRender's 1998 rasterisers are x86 assembly. The period build replaces the
ones these scenes use with engine-revival's line-by-line C ports:

- `RawTriangle_PIZ2_RGB_888` and `RawTriangle_PIZ2I_RGB_888` in
  `tt24_piz.asm` (0.4.0);
- the `TrapezoidRenderPIZ2TA24` and `TrapezoidRenderPIZ2TIA_RGB_888` loops
  in `t_piza.asm` (0.5.0), under Argonaut's own C setup in `awtmz.c`;
- `TriangleRender_Z_I8_D16` and `TriangleRender_ZTI_I8_D16_256` in `zb8.asm`,
  `TriangleRender_ZI_I8_D16` and `TriangleRender_ZT_I8_D16_256` in
  `fti8_piz.asm`, and the float setup they call in `fpsetup.asm` (0.6.0). The ports keep the assembly's fixed-point setup, its
edge and texture stepping, its truncating divides and its depth tests. So "period" means
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

Recomputed from the artifacts of CI run 38979266555 (commit `6934dc7`).

| Comparison | Scenes identical | Lowest coverage IoU | Lowest identical | Highest MAD | Control |
|---|---|---|---|---|---|
| period 1.3.2, two runs (Win32) | 20 of 20 | 1.0 | 1.0 | 0 | fails, as required |
| modern 1.4, two runs (Windows and Linux) | 20 of 20 | 1.0 | 1.0 | 0 | fails, as required |
| modern Windows MSVC against modern Linux GCC | 17 of 20 | 1.0 | 0.9998 | 0.0 | fails, as required |
| modern against period, 24-bit, without lit textured | 1 of 9 | 0.9992 | 0.907 | 1.085 | fails, as required (0.60) |
| modern against period, 8-bit | 0 of 9 | 0.9983 | 0.9642 | 0.427 | fails, as required |
| modern against period, 24-bit lit textured | 0 of 2 | 0.4771 | 0.0 | 132.6 | fails, as required |
| the same, shade table at stride 4 | 0 of 2 | 0.9998 | 0.9789 | 0.272 | fails, as required |

The two-run rows come from CI's determinism steps, which require identical
bytes on every change. The two-run records in `evidence/` predate the 8-bit
scenes and cover the first nine.

| Scene, modern against period | Coverage IoU | Identical | MAD | Max |
|---|---|---|---|---|
| sphere-flat (unlit) | 0.9998 | 0.9998 | 0.032 | 199 |
| sphere-lit (flat lit) | 0.9998 | 0.9583 | 0.065 | 159 |
| sphere-smooth (Gouraud) | 0.9998 | 0.9070 | 0.072 | 153 |
| torus-flat | 1.0 | 1.0 | 0.0 | 0 |
| torus-smooth | 1.0 | 0.9348 | 0.035 | 15 |
| teapot-smooth | 0.9993 | 0.9215 | 0.174 | 91 |
| sphere-textured (earth) | 0.9998 | 0.9824 | 0.332 | 240 |
| sphere-textured-turned | 0.9992 | 0.9565 | 1.085 | 246 |
| torus-textured (rosewood) | 1.0 | 0.9969 | 0.041 | 89 |
| sphere-textured-lit, as shipped | 0.4771 | 0.0005 | 132.634 | 252 |
| torus-textured-lit, as shipped | 0.6562 | 0.0 | 89.017 | 248 |
| sphere-textured-lit, table at stride 4 | 0.9998 | 0.9789 | 0.272 | 240 |
| torus-textured-lit, table at stride 4 | 1.0 | 0.9950 | 0.037 | 35 |
| sphere-flat-index8 | 0.9993 | 0.9993 | 0.059 | 158 |
| sphere-lit-index8 | 0.9993 | 0.9975 | 0.106 | 246 |
| sphere-smooth-index8 | 0.9993 | 0.9932 | 0.107 | 244 |
| torus-smooth-index8 | 0.9986 | 0.9893 | 0.256 | 242 |
| teapot-smooth-index8 | 0.9990 | 0.9835 | 0.224 | 228 |
| sphere-textured-index8 | 0.9993 | 0.9793 | 0.427 | 246 |
| torus-textured-index8 | 0.9986 | 0.9665 | 0.394 | 158 |
| sphere-textured-lit-index8 | 0.9993 | 0.9781 | 0.304 | 246 |
| torus-textured-lit-index8 | 0.9983 | 0.9642 | 0.392 | 158 |

In the 8-bit scenes "identical" means the same palette index, and MAD and max
are measured on the colours those indices map to. A neighbouring index on a
ramp can be a large colour step, so max is high where MAD is low.

The two engines draw the same silhouettes. The unlit torus is the same to the
byte. The 1998 edge rule draws a few pixels more along some edges (6 on the
sphere, 6 on the teapot). Pixels more than 20 levels apart number 6 on the
unlit and smooth spheres, all of them on those edges; 36 on the flat-lit
sphere and 20 on the teapot, 6 of each on edges and the rest inside. The
Gouraud scenes differ by small rounding over larger areas (MAD under 0.2
levels), which fits the 1998 16.16 fixed-point stepping against 1.4's own
arithmetic. These are measured differences, not a judgement that either side
is wrong.

The textured differences are not traced pixel by pixel yet. The likely
cause (inferred, not measured) is texture stepping: the 1998 kernel steps u
and v in 16.16 fixed point from Argonaut's setup, so a texel boundary can
land one pixel away from where BRender 1.4 puts it. The turned sphere
differs most.

Evidence: `evidence/*.json`, `evidence/period-left-modern-right-2026-10-16.png`
(untextured), `evidence/period-left-modern-right-textured-2026-10-16.png`
(textured) and `evidence/period-left-modern-right-index8-2026-10-16.png`
(8-bit), period on the left and modern on the right.

## A 1998 defect: the 24-bit lit textured kernel

BRender 1.3.2 cannot draw a lit, textured triangle into a 24-bit buffer
correctly. The defect is in the 1998 source, not in the port:

- `prim_t24.c` declares the primitive "RGB 888, Z Buffered, Constant
  Intensity, Textured, Perspective Correct"
  (`TriangleRenderPIZ2TIA_RGB_888`) with a shade table of type
  `BR_PMT_RGB_888`, whose entries are 3 bytes.
- `t_piza.asm`, in the 3-byte branch of `TrapezoidRenderPIZ2TIA_RGB_888`,
  reads entry n at `[edx+ecx*4]`: byte 4n, the stride of a 4-byte entry. It
  then writes 3 bytes.

So the kernel reads the wrong entry for every pixel past the first, and from
the 48th row of a 64-row table on it reads past the end of the table. The
engine-revival port keeps the 4-byte stride, as it keeps everything else in
the assembly.

`parity-scene.c` pads the RGB_888 shade table with zeroed rows below it, so
the over-read stays in memory the program owns and the result is the same on
every run. The table both sides see still has its 64 rows.

As shipped, the 1998 build draws the two 24-bit lit textured scenes as
stripes and fragments (coverage IoU 0.48 and 0.66, almost no identical
pixels). `PARITY_SHADE4=1`, read on the period side only, lays entry n at byte
4n instead, the stride the kernel reads. With that one change the same
scenes match BRender 1.4: coverage IoU 0.9998 and 1.0, 97.9% and 99.5% of
pixels identical, MAD at most 0.272. The stride is the whole difference; the
rest of the kernel (texture stepping, lighting index, depth) agrees.

`PARITY_SHADE4` is a measurement, not a fix to BRender 1.3.2: the period
build stays as the 1998 source wrote it. The 8-bit lit textured kernel
(`TriangleRender_ZTI_I8_D16_256`) reads its 8-bit table at the right stride
and matches without any change.

`evidence/lit-textured-24bit-stride-2026-10-16.png` shows the period build
with the table as declared, the period build with the table at stride 4, and
BRender 1.4. `evidence/modern-vs-period-shade4-2026-10-16.json` holds the
stride 4 numbers.

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

- runs the period scenes twice (Win32), and twice more with the shade table
  at stride 4, and the modern scenes twice on Windows and on Linux, and
  requires identical bytes each time;
- compares modern Windows against modern Linux within coverage IoU 1.0, at
  least 99.9% identical pixels and at most 1 level;
- compares modern against period, each class within its own bounds (table
  below);
- reports the 24-bit lit textured scenes as shipped, without bounds.

| Class | Coverage IoU | Identical | MAD |
|---|---|---|---|
| 24-bit untextured | 0.999 | 90% | 0.25 |
| 24-bit textured, unlit | 0.999 | 95% | 1.2 |
| 8-bit untextured | 0.998 | 98% | 0.3 |
| 8-bit textured, unlit and lit | 0.998 | 96% | 0.5 |
| 24-bit lit textured, table at stride 4 | 0.999 | 97% | 0.3 |

All bounds were set from the measurements above, so they are calibrated, not
predicted.

## OpenGL against software (BRender 1.4)

The downloads draw with BRender 1.4's OpenGL driver unless asked for the
software rasteriser, so the two should draw the same picture.
`gl_vs_software.py` draws every brview model both ways at 640 x 480, from
brview's still mode (`BRVIEW_SHOT`, `BRVIEW_SCENE`, `BRVIEW_TEXTURE`,
`BRVIEW_UNLIT`), in three classes:

- **unlit:** one flat colour per model, which isolates coverage;
- **textured:** unlit, with the texture (the earth and the torus);
- **lit:** brview's normal look.

Measured 16 October 2026 with Mesa llvmpipe (WSL, Ubuntu 24.04), recomputed
in CI on every change:

| Class | Stills | Coverage IoU | Identical (within 2 levels) | MAD |
|---|---|---|---|---|
| unlit | 8 | 0.9774 to 0.9957 | 0.9774 to 0.9957 | at most 4.21 |
| textured | 2 | 0.9929 and 0.9957 | 0.7829 and 0.7925 | at most 4.32 |
| lit | 8 | 0.9774 to 0.9957 | 0.0093 to 0.6763 | up to 35.2 |

- **Coverage:** every pixel both renderers fill has the same colour (the
  unlit "identical" share equals the IoU). The difference is at the edges:
  93 to 293 pixels per model drawn only by OpenGL and 82 to 289 only by
  software, about as many each way. The two follow different edge rules; no
  shift or offset.
- **Textures:** about 79% of textured pixels agree within 2 levels; texel
  selection differs between the two samplers. Not traced further.
- **Lighting:** OpenGL lights per pixel and the software rasteriser per
  vertex, so the lit stills differ, as intended. One difference is larger: a
  lit, textured 24-bit material is not lit at all by the software rasteriser
  (its lit and unlit stills are the same bytes), while OpenGL lights it. This
  follows 1998: the 24-bit textured kernels light only through a shade table
  (`TrapezoidRenderPIZ2TIA_RGB_888`), and with none given BRender picks the
  unlit kernel. So brview's earth and torus look flat on the software
  renderer.
- **Determinism:** two OpenGL runs give the same bytes (the readback waits
  for OpenGL to finish, `brd_frame_write_ppm`).
- **Control:** OpenGL's unlit earth against the software's unlit teapot must
  fail (coverage IoU 0.31).

CI gates unlit and textured at the measured values, rounded down: coverage
IoU 0.975 and 0.99, identical 0.975 and 0.77, MAD 4.5. It keeps the stills
and the JSON as the `gl-vs-software` artifact. Evidence:
`evidence/gl-vs-software-2026-10-16.json` and
`evidence/opengl-left-software-right-2026-10-16.png` (earth unlit, textured
and lit, teapot lit, torus textured, logo unlit; OpenGL left).

Windows CI has no OpenGL, so this runs on Linux only.

## Not measured yet

- Perspective-correct texturing: the materials here do not set
  `BR_MATF_PERSPECTIVE`, so both sides run their linear texture kernels.
- 15/16-bit targets: not ported.
