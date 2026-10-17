# Pixel parity: the 1998 rasteriser against the modern one

The question is whether BRender 1.4, the modern 64-bit engine the downloads
use, draws the same pixels as Argonaut's BRender 1.3.2 from 1998.

**Answer on 17 October 2026, for the sixty-one scenes measured here: yes,
with one 1998 defect.** Given the same angles, the 1998 rasteriser and
BRender 1.4 draw the same pixels.

- **56 of the 61 scenes are byte-identical** to BRender 1.4 on Windows:
  every 8-bit scene (unlit, flat, Gouraud, textured, lit textured,
  perspective-correct), every 24-bit flat and textured scene, and all 34
  15/16-bit scenes through the 1998 MMX table, textured and dithered
  included.
- **Three 24-bit Gouraud scenes** differ in 2 to 6 pixels, by one level. BRender 1.4's own
  Windows and Linux builds differ from each other on the same scenes by a
  similar amount.
- **24-bit lit textured:** the 1998 kernel reads its shade table at the wrong
  stride, so as shipped it draws garbage (see
  [A 1998 defect](#a-1998-defect-the-24-bit-lit-textured-kernel)). With the
  table laid at the stride it reads, one scene is identical and the other
  differs in 2 pixels.
- What made the difference: BRender 1.3.2's `BR_ANGLE_DEG` is 182 units a
  degree, truncated, where BRender 1.4's angle is exact (see
  [The same angle on both sides](#the-same-angle-on-both-sides)). Every
  section below that one was measured before the fix, with each version's own
  macro; it stays as the record of what each kernel port achieved then.

The earlier answer (16 and 17 October, each version's own angle macro): almost,
with the same defect.
- **24-bit untextured:** silhouettes match to a coverage IoU of 0.9993 or
  better, 90.7% to 100% of pixels are identical, and the mean difference is
  under 0.2 levels.
- **24-bit textured:** coverage IoU is 0.9992 or better, 95.7% to 99.7% of
  pixels are identical, and the mean difference is at most 1.09 levels.
- **8-bit, through the palette:** coverage IoU is 0.9983 or better, 96.4% to
  99.9% of pixels carry the same palette index, and the mean difference is at
  most 0.43 levels. This covers unlit, flat, Gouraud, textured and lit
  textured scenes.
- **8-bit, perspective-correct:** coverage IoU is 0.9983 or better, 92.6% to
  97.9% of pixels carry the same palette index, and the mean difference is
  at most 1.71 levels. The lowest is a steeply turned plane, which scores the
  same without perspective, so that difference comes before the rasteriser
  (see [Perspective-correct texturing](#perspective-correct-texturing)).
- **24-bit lit textured:** the 1998 kernel reads its shade table at the wrong
  stride, so as shipped it draws garbage (see
  [A 1998 defect](#a-1998-defect-the-24-bit-lit-textured-kernel)). With the
  table laid at the stride it reads, it matches: coverage IoU 0.9998 or
  better, 97.9% and 99.5% identical.
- **15 and 16-bit, through the 1998 MMX table:** coverage IoU 0.9970 or
  better, 96.6% to 99.9% of pixels identical, and the mean difference at
  most 0.48 levels, textured included. Fed BRender 1.4's own vertices, the
  1998 MMX kernels draw 1.4's frames byte for byte, so the rest is in the
  vertices (see
  [15 and 16-bit through the MMX table](#15-and-16-bit-through-the-mmx-table)).

The 1998 build gives the same bytes on every run.

## The same angle on both sides

Measured 17 October 2026, CI run 39067573521. The CI period frames (general
tables, MMX table and shade table at stride 4) are the same bytes as local
Win32 runs, and CI Windows modern the same as a local Windows run.

`parity-scene.c` turns its model, camera and light through degrees. The two
versions turn degrees into angles differently:

- BRender 1.3.2, `inc/angles.h:16`:
  `BR_ANGLE_DEG(deg) ((br_angle)(long)((deg)*182))`. A turn is 65536 units,
  so a degree is 182.04 units; 182 is 0.024% short, and the product is
  truncated. The 55-degree field of view becomes 54.987 degrees.
- BRender 1.4, `core/inc/angles.h:16`:
  `BR_ANGLE_DEG(deg) ((br_angle)((deg) / 360.0f))`, a float fraction of a turn.

So every period vertex sat up to a few hundredths of a pixel from 1.4's: the
geometry difference the perspective and 15/16-bit sections traced to the
vertices. The lead found the cause by dumping each version's model, clip and
screen coordinates (the model-to-clip matrices differed by 3.5e-4 relative).
`parity-scene.c` now gives both sides the same angle, `PARITY_ANGLE`: the
nearest 16-bit unit, in each version's own form. With it the clip
coordinates agree, and:

| Against BRender 1.4 (Linux, CI) | Scenes | Identical scenes | Rest |
|---|---|---|---|
| 24-bit and 8-bit, general tables | 27 | 22 | three Gouraud scenes, 2 to 6 pixels each, max 1 level; the two lit textured scenes (1998 stride defect) |
| 24-bit lit textured, table at stride 4 | 2 | 1 | 2 pixels |
| 15/16-bit, MMX table | 34 | 30 | four scenes, 2 pixels each, one level of the format |
| 15/16-bit, general tables | 34 | 0 | a different kernel family from 1.4's (above): IoU 0.9868, 63.7% identical |

Against BRender 1.4 on Windows the MMX row is 34 of 34. Apart from the torus with its table at stride 4 (2 pixels, not
traced), every scene left over
is one on which BRender 1.4's own Windows and Linux builds also disagree, by
a similar amount (7 scenes, 1 to 3 pixels each,
`evidence/modern-windows-vs-linux-angle-2026-10-17.json`). That looks like
the last-bit floating point variance between builds that BlazingRenderer's
softprim README describes; it was not traced further.

The gates are now tight: byte-identical where the measurement is, and one
level (one level of the format at 15/16 bits) on at most 0.1% of pixels
elsewhere. Run against the frames from before the fix, the tightened gates
fail, so they can tell the difference.

Evidence: `evidence/modern-vs-period-angle-2026-10-17.json` (24 and 8-bit),
`evidence/modern-vs-period-mmx-angle-2026-10-17.json` (15/16-bit, MMX),
`evidence/modern-vs-period-shade4-angle-2026-10-17.json`,
`evidence/modern-vs-period-hicolor-angle-2026-10-17.json` (15/16-bit,
general tables), `evidence/modern-windows-vs-linux-angle-2026-10-17.json` and
`evidence/shared-angle-differences-2026-10-17.png`. The sheet shows, for five
scenes, where period and 1.4 differ before the fix and after it. I looked at
it: hundreds of scattered pixels before, two after on the Gouraud sphere,
none on the others.

## The instrument

`parity-scene.c` draws sixty-one scenes and a control at 320 x 240, from
the 1998 sample models and one plane it builds itself. Eleven draw into an RGB_888 buffer:

- six untextured: a sphere, a torus and the teapot, unlit, lit flat and lit
  smooth (Gouraud);
- three textured and unlit: the sphere with `earth.pix` at two angles, and
  the torus with `rosewood.pix`, each expanded through `std.pal` into an
  RGB_888 map;
- two lit textured: the sphere and the torus with their 8-bit maps, lit
  through `shade.tab` expanded through `std.pal` into an RGB_888 shade table.

Nine draw into an INDEX_8 buffer through `std.pal`, BRender's 8-bit palette
path: five untextured (each on its own palette ramp), two textured unlit and
two textured lit through `shade.tab`. Seven more are 8-bit and textured
with `BR_MATF_PERSPECTIVE`: the sphere and the torus, unlit and lit, and a
plane of eight large triangles turned 60 degrees so it recedes, unlit and lit,
beside the same plane without perspective. Thirty-four more draw into
RGB_555 and RGB_565 buffers (the two 15/16-bit sections below). Each 8-bit
scene writes the indices
(`.pgm`) and the colours they map to (`.ppm`); the comparison counts a pixel
identical when the index is the same.

The control is described below. Everything except the
rasteriser is shared: model, camera, transform, material, light and buffer.
Each side copies the renderer setup of its own ladder rung.

| Side | Engine | Built by |
|---|---|---|
| period | BRender 1.3.2: softrend + pentprim, 32-bit, from the public source | `period/CMakeLists.txt` over the harness from engine-revival 0.9.0, built twice: with pentprim's general tables, and with `-DBRENDER_PENTPRIM_MMX=ON` as a Pentium with MMX runs it |
| modern | BRender 1.4 (BlazingRenderer): softrend + softprim, 64-bit | `modern/CMakeLists.txt` (target `parity-scene`) |

BRender's 1998 rasterisers are x86 assembly. The period build replaces the
ones these scenes use with engine-revival's line-by-line C ports:

- `RawTriangle_PIZ2_RGB_888` and `RawTriangle_PIZ2I_RGB_888` in
  `tt24_piz.asm` (0.4.0);
- the `TrapezoidRenderPIZ2TA24` and `TrapezoidRenderPIZ2TIA_RGB_888` loops
  in `t_piza.asm` (0.5.0), under Argonaut's own C setup in `awtmz.c`;
- `TriangleRender_Z_I8_D16` and `TriangleRender_ZTI_I8_D16_256` in `zb8.asm`,
  `TriangleRender_ZI_I8_D16` and `TriangleRender_ZT_I8_D16_256` in
  `fti8_piz.asm`, and the float setup they call in `fpsetup.asm` (0.6.0);
- `TriangleRender_ZPT_I8_D16_256` and `TriangleRender_ZPTI_I8_D16_256` in
  `fti8pizp.asm`, with the perspective setup in `pfpsetup.asm` (0.7.0).

The ports keep the assembly's fixed-point setup, its edge and texture
stepping, its truncating divides and its depth tests. So "period" means the
1998 algorithm, run through a C port, not the 1998 binary. For the 0.7.0
perspective kernels the port was also checked against the 1998 code itself
(see below).

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

## Perspective-correct texturing

Measured 17 October 2026, engine-revival 0.7.0 against BRender 1.4. The
modern frames come from Linux; Windows gives the same bytes for these
scenes, and the period frames from CI are the same bytes as a local Win32
run. The control fails as required (coverage IoU 0.60).
Recomputed from the artifacts of CI run 38988569106 (commit `487a262`).

| Scene, modern against period | Coverage IoU | Identical | MAD | Max | Triangles, perspective / linear |
|---|---|---|---|---|---|
| sphere-textured-persp-index8 | 0.9993 | 0.9793 | 0.427 | 246 | 0 / 326 |
| sphere-textured-lit-persp-index8 | 0.9993 | 0.9781 | 0.304 | 246 | 0 / 326 |
| torus-textured-persp-index8 | 0.9986 | 0.9665 | 0.393 | 158 | 28 / 84 |
| torus-textured-lit-persp-index8 | 0.9983 | 0.9634 | 0.386 | 158 | 28 / 84 |
| plane-textured-steep-persp-index8 | 0.9988 | 0.9259 | 1.616 | 252 | 8 / 0 |
| plane-textured-lit-steep-persp-index8 | 0.9988 | 0.9305 | 1.492 | 208 | 8 / 0 |
| plane-textured-steep-linear-index8 (no perspective) | 0.9988 | 0.9267 | 1.713 | 252 | linear material |

Before engine-revival 0.7.0 the two perspective kernels were stubs: the same
scenes drew nothing on the period side (0 pixels, 440 calls to each stub).

**Checked against the 1998 assembly.** `pfpsetup.asm` and `fti8pizp.asm`
were assembled with MASM (ml 14.44), against a `drv.inc` generated from the
harness's own structure offsets, and linked into the period build in place of
the port. Every scene came out byte for byte as the port draws it. A
differential test drew 62,000 random triangles both ways into separate
buffers with no mismatch, covering both scan directions, all five scanline
loops and the cheat path. Changing one instruction in the assembly (the v
step) changed exactly the two unlit scenes with perspective triangles, so the
check can fail. This was a local run; the reference build is not part of CI.

**Where the triangles go.** The 1998 setup draws a triangle linearly (its
"cheat") when w changes little across it: when the w range times the screen
range is below four times the smallest w. All 326 sphere triangles take that
path, on both sides, so the perspective sphere is the same bytes as the
linear one. The torus has 28 perspective triangles of 112 and the plane all
8, so those two exercise the perspective kernels.

**The plane's lower score is not in the perspective kernels.** The same plane
without perspective scores the same (IoU 0.9988, 92.7% identical, against
92.6% with perspective). Dumping the vertices each side hands its rasteriser
shows why: for the same triangles the screen x and y differ by up to 0.03
pixels and the depth by up to 3 units in 65536; w, u and v agree. BRender
1.4's screen points fit an exact projection of the scene (scale 230.52, which
is 120 / tan 27.5 degrees) within 0.01 pixels. The 1998 build's points scatter
around it, with scales between 230.48 and 230.71. So the 1998 geometry path,
as built here, places vertices up to 0.03 pixels off; a texel boundary then
lands one pixel away. Where in the period core or softrend that comes from is
not located yet.

Evidence: `evidence/modern-vs-period-persp-2026-10-17.json`,
`evidence/modern-vs-period-2026-10-17.json` (all 27 scenes),
`evidence/modern-windows-vs-linux-2026-10-17.json` (24 of 27 identical, the
other three off by one level on at most 0.02% of pixels) and
`evidence/period-left-modern-right-persp-2026-10-17.png` (the plane with and
without perspective, the lit plane, and the torus unlit and lit; period on
the left).

## 15 and 16-bit buffers (RGB_555, RGB_565)

Measured 17 October 2026, engine-revival 0.8.0 against BRender 1.4. The
frames come from CI run 39001220926 (commit `97154a4`). The CI period frames
are the same bytes as a local Win32 run, and modern Windows gives the same
bytes as modern Linux for all twenty scenes. The control fails as required.

There are twenty scenes, ten in each format. Five are untextured: the
sphere flat, flat lit and Gouraud, and the torus flat and Gouraud. Two use
256 x 256 maps, `earth.pix` and `rosewood.pix`, packed into the buffer's
format. One uses `gold8.pix`, which is 320 x 200 and so not a power of two.
Two light the 8-bit map through `shade.tab`, packed into the buffer's
format. For the PPMs both sides expand each field the same way: shift it to
the top of its byte and repeat its top bits below. Each class reaches its
own period kernel:

| Class | Period kernel (1998 source) |
|---|---|
| untextured, flat colour | `TriangleRenderPIZ2_RGB_555` / `_565` (`tt15_piz.asm`, `tt16_piz.asm`) |
| untextured, Gouraud | `TriangleRenderPIZ2I_RGB_555` / `_565` (same files) |
| 256 x 256 map | `TriangleRender_ZT_RGB565_D16_256` (`zb16p2ul.asm`; both tables use it) |
| 320 x 200 map | `TrapezoidRenderPIZ2TA15` (`t_piza.asm`, under `awtmz.c`) |
| lit 8-bit map | `TrapezoidRenderPIZ2TIA_RGB_555` (`t_piza.asm`; both tables use it) |

Before engine-revival 0.8.0 these were stubs, and the period side drew
nothing in all twenty scenes. Two period runs now give the same bytes, and
the 27 older scenes are unchanged.

**Checked against the 1998 assembly.** `tt15_piz.asm`, `tt16_piz.asm`,
`tt24_piz.asm`, `t_piza.asm`, `zb16p2ul.asm` and `fpsetup.asm` were assembled
with MASM against a `drv.inc` generated from the harness's own structure
offsets and linked into the period build in place of the ports. All 47 scenes
came out byte for byte as the ports draw them. A differential test drew
72,000 random triangles both ways over the fifteen kernels and found no
mismatch. Four one-instruction changes to the assembly changed exactly the 13
scenes that use those instructions, and made the random test fail. This was a
local run; the reference build is not part of CI.

**The DBPP 2 shade table stride is correct.** The 16-bit lit kernel reads
entry n at `[edx+ecx*2]`, a 2-byte entry, which matches its RGB_555 or
RGB_565 table. The 24-bit defect below has no 16-bit counterpart.

**BRender 1.4 draws a different 1998 path here.** On a processor with MMX,
the 1998 matcher replaces the whole 15/16-bit triangle table with the MMX
table (`drivers/pentprim/match.c:593`, selected by CPUID at
`plib.c:100`). BRender 1.4 reproduces that machine. Its softprim lists the
MMX tables first (`drivers/softprim/CMakeLists.txt:71`) and refuses the
z-buffered shapes that sample a 555 or 565 map (`infogen.pl:338`). The MMX
table's untextured rows take any map that is not 8-bit with a palette, so
BRender 1.4 draws every textured scene here untextured. Its untextured
kernels use the MMX setup, which walks four-pixel words (`raster.cpp:4631`).
The period harness builds without `USE_MMX`, so it uses pentprim's general
tables. For z-buffered 15/16-bit triangles the two sides share no kernel.
This is a difference in which 1998 path each side reproduces, not a defect
on either side. It is recorded here and not filed upstream (BlazingRenderer
`ed5e7a9`). engine-revival 0.9.0 ports the MMX path as well; the next
section compares like with like.

| Scene, modern against period | Coverage IoU | Identical | MAD | Max |
|---|---|---|---|---|
| sphere-flat-rgb555 / 565 | 0.9935 | 0.9935 | 1.03 / 1.023 | 198 |
| sphere-lit-rgb555 / 565 | 0.9935 | 0.9309 / 0.9226 | 1.008 | 181 |
| sphere-smooth-rgb555 / 565 | 0.9935 | 0.8574 / 0.8156 | 0.888 / 0.887 | 181 |
| torus-flat-rgb555 / 565 | 0.9869 | 0.9869 | 2.081 / 2.068 | 198 |
| torus-smooth-rgb555 / 565 | 0.9869 | 0.7166 / 0.632 | 1.875 / 1.879 | 165 |
| textured, all ten | 0.9642 to 0.9993 | 0 | 43.5 to 115.2 | 247 |

On the flat scenes every pixel both sides draw has the same colour: the
identical share equals the coverage IoU. BRender 1.4's 16-bit sphere covers
42 pixels fewer than its own 24-bit sphere (29,594 against 29,636), so its
MMX walk, not the colour, accounts for the coverage difference. On the
Gouraud scenes fewer pixels are identical. The likely cause, inferred from
`raster.cpp:4631` and not measured, is that the MMX path truncates the colour
step when it builds each four-pixel word. None of these numbers says
anything about the textured kernels: BRender 1.4 does not texture these
scenes. The assembly comparison above is the check on those kernels.

Evidence: `evidence/modern-vs-period-hicolor-2026-10-17.json` (twenty
scenes), `evidence/modern-windows-vs-linux-hicolor-2026-10-17.json` (all 47
scenes; the twenty new ones identical) and
`evidence/period-left-modern-right-hicolor-2026-10-17.png` (flat, Gouraud,
earth, gold and the lit torus; period on the left).

## 15 and 16-bit through the MMX table

Measured 17 October 2026, engine-revival 0.9.0 against BRender 1.4. The
frames come from CI run 39010833674 (commit `cbb58ce`). The CI period frames
are the same bytes as a local Win32 run, and the CI Windows modern frames are
the same as a local Windows run. The control fails as required.

engine-revival 0.9.0 ports pentprim's MMX family line by line:
`gsetuptf.asm`'s setup, `rastbuff.asm`'s rasterise buffer (parameter blocks
drawn newest first when the buffer fills or the renderer flushes) and the
kernels `xzrgb.inc`, `xzuv1.inc`, `xzuvc.inc` and `xzuvrgb.inc`. Its harness
option `BRENDER_PENTPRIM_MMX` builds pentprim with `USE_MMX=1` and a host that
reports MMX, so the 1998 matcher uses its MMX table for 15/16-bit triangles,
as on a Pentium with MMX. CI builds the period scene a second time with that
option. The 27 scenes that are not 15/16-bit come out byte for byte as the
general build draws them.

The MMX table textures only an 8-bit map with a palette, a power of two on
each side. The textured scenes of the previous section use 16-bit maps, or an
8-bit map with no palette, so on both sides they take the table's untextured
rows. Fourteen new scenes, seven in each format, use `earth.pix` and
`rosewood.pix` with `std.pal` attached:

| Scene | MMX kernel (1998 source) |
|---|---|
| `*-textured-pal-*`, white unlit material | `RasteriseMMX5x5_Z_UV` (`xzuv1.inc`) |
| `sphere-textured-pal-tint-*`, the usual material colour | `Z_UV_C` (`xzuvc.inc`): softrend modulates by any colour that is not white |
| `*-textured-pal-lit-*`, lit smooth | `Z_UV_RGB` (`xzuvrgb.inc`) |
| `sphere-textured-pal-dither-*`, `BR_MATF_DITHER` | `Z_UV_D` |
| `sphere-smooth-dither-*`, `BR_MATF_DITHER` | `Z_RGB_D` (`xzrgb.inc`) |

The untextured scenes take `Z_RGB`.

**Checked against the 1998 assembly.** `gsetuptf.asm`, `rastbuff.asm`,
`rastrise.asm`, `setupdat.asm` and the eight `xz*.asm` files were assembled
with MASM and linked into the period build in place of the port. MASM used a
`drv.inc` generated from the harness's structure offsets, plus 26 operand-size
annotations that MASM 14 asks for and that leave every encoding unchanged.
All 61 scenes came out byte for byte as the port draws them. A differential
test drew 240,866 random triangles both ways, in batches of 1 to 24 so that
the buffer's order and its flush are exercised, over all 32 kernels in both
formats: no difference. One-instruction changes to the assembly (one per
kernel file, one in the setup) made it fail in exactly the kernels they
touch. This was a local run; the reference build is not part of CI.

| Class, modern against period (MMX) | Scenes | Coverage IoU | Identical | MAD, at most |
|---|---|---|---|---|
| untextured | 10 | 0.9986 to 0.9993 | 0.9701 to 0.9993 | 0.230 |
| 16-bit maps (untextured on both sides) | 10 | 0.9986 to 0.9993 | 0.9701 to 0.9993 | 0.230 |
| 8-bit palette maps, textured | 10 | 0.9970 to 0.9993 | 0.9659 to 0.9809 | 0.432 |
| dithered | 4 | 0.9993 | 0.9781 to 0.9872 | 0.476 |

Against the general tables (previous section) the untextured scenes were 63%
to 99% identical. Through the MMX table they are 97% to 99.9%, and the
textured scenes, 0% before, are 96.6% to 98.1%.

**Where the rest comes from.** A local, instrumented copy of BRender 1.4's
softprim wrote out the vertices each of its MMX triangles receives
(`MmxTriangle`, `drivers/softprim/raster.cpp:5265`). Replayed in the same
order through engine-revival's port of the 1998 setup and kernels, they give
BRender 1.4's own frames byte for byte, on all 34 scenes. The port draws as
the 1998 assembly does, so the 1998 MMX kernels and BRender 1.4's draw the
same pixels from the same input. The period frames differ because the two
softrend versions hand the rasteriser different vertices: the 0.03-pixel
geometry difference found with the perspective scenes. It is also why the
period sphere covers 22 more pixels than 1.4's in every 15/16-bit scene. The
replay was local; it is not part of CI.

**A 1998 defect, kept as found.** In a span of two or more words, the 16-bit
dithered textured kernel does not mask green: `xzuv1.inc` tests
`COLOUR_TYPE_15` twice where the second test should be `COLOUR_TYPE_16`, so
green's low bits land in the blue field. The one-word span masks it. On the
sheet, the dithered 565 earth shows it as cyan in the green land, on both
sides. BlazingRenderer recorded this first, in BRender 1.4's
`drivers/softprim/raster.cpp:4823` (`MmxPackDirectDither`), and 1.4
reproduces it.

Evidence: `evidence/modern-vs-period-mmx-2026-10-17.json` (34 scenes),
`evidence/modern-windows-vs-linux-mmx-2026-10-17.json` (all 61 scenes; the
fourteen new ones identical) and
`evidence/period-mmx-left-modern-right-hicolor-2026-10-17.png` (the four
textured kernels, the dithered earth and the Gouraud torus; period on the
left).

## A 1998 defect: the 24-bit lit textured kernel

BRender 1.3.2 cannot draw a lit, textured triangle into a 24-bit buffer
correctly. The defect is in the 1998 source, not in the port. BlazingRenderer
found it first: their `drivers/softprim/README.md` (at the pinned commit
`ed5e7a9`) records that pentprim read the 256 x 256 RGB_888 table at a
four-byte stride while its matcher required three-byte entries, and that
softprim implements the family with the read corrected. We found it again on
16 October 2026 from the period side, by measurement, and missed their note
at the time; what this repository adds is the measurement below.

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

- runs the period scenes twice (Win32), checks the perspective and the
  15/16-bit scenes on their own as well, and runs them twice more with the shade table at stride
  4, then twice through the MMX table (checking that only the 15/16-bit
  scenes change), and the modern scenes twice on Windows and on Linux, and
  requires identical bytes each time;
- compares modern Windows against modern Linux within coverage IoU 1.0, at
  least 99.9% identical pixels and at most 1 level;
- compares modern against period, each class within its own bounds (table
  below);
- reports the 24-bit lit textured scenes as shipped, and the textured
  15/16-bit scenes against the general tables, without bounds.

| Class | Coverage IoU | Identical | MAD |
|---|---|---|---|
| 24-bit untextured | 0.999 | 90% | 0.25 |
| 24-bit textured, unlit | 0.999 | 95% | 1.2 |
| 8-bit untextured | 0.998 | 98% | 0.3 |
| 8-bit textured, unlit and lit | 0.998 | 96% | 0.5 |
| 24-bit lit textured, table at stride 4 | 0.999 | 97% | 0.3 |
| 8-bit perspective-correct, with the linear plane | 0.998 | 92% | 1.8 |
| 15/16-bit untextured, general tables (against 1.4's MMX path) | 0.986 | 63% | 2.1 |
| 15/16-bit untextured, through the MMX table | 0.998 | 97% | 0.25 |
| 15/16-bit, 16-bit maps, through the MMX table | 0.998 | 97% | 0.25 |
| 15/16-bit, 8-bit palette maps, through the MMX table | 0.997 | 96% | 0.45 |
| 15/16-bit dithered, through the MMX table | 0.999 | 97% | 0.5 |

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
| lit | 8 | 0.9774 to 0.9957 | 0.1139 to 0.6763 | up to 13.8 |

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
  unlit kernel. Since 17 October 2026 brview gives its lit textured models
  on the software renderer their 8-bit map and a 24-bit shade table built
  from `std.pal` (`viewer/brview_shade.c`). Before that change the earth and
  torus drew flat: identical pixels 0.9% and 2.5%, MAD 35.2 and 19.1 against
  OpenGL. After it: 11.4% and 35.6%, MAD 13.8 and 10.4. The rest is
  per-pixel against per-vertex lighting and OpenGL's specular highlight.
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

- The z-sorted 15/16-bit kernels and the `TIP256` perspective mappers are
  not ported. The MMX table's subdivided-perspective rows reuse the ported
  kernels, but no scene asks for subdivision.
