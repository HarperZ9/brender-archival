# ADR 0002: a Vulkan backend for BRender, in three stages

**Status:** Accepted for stage A, which is built and measured here. Stages B
and C are proposed. **Date:** 2026-10-17.

## Context

Roadmap item 6 asks for modern GPU backends next to the software rasteriser,
under MIT, each held to the item 5 parity bounds. BRender 1.4
(BlazingRenderer) has two renderers today:

- **softrend + softprim**: geometry, lighting and clipping in softrend, then
  triangles in screen space handed to the primitive library softprim, which
  rasterises them. It is deterministic, and item 5 measures it against the
  1998 rasteriser.
- **glrend**: an OpenGL 3.3 renderer facility with its own transform and
  lighting in GLSL (about 9,200 lines). Item 5's OpenGL comparison shows it
  fills the same pixels as the software rasteriser to a coverage IoU of
  0.977 or better, and lights them differently (per pixel against per
  vertex).

Vulkan runs on Windows and Linux, and Mesa's lavapipe gives a CPU Vulkan
device that CI can run with no GPU. Vulkan is also verbose: a first triangle
takes several hundred lines, and a full renderer is a large job. The order of
work decides whether every step can be checked.

## Options

**A. Port glrend to Vulkan in one piece.** Rejected for now. It changes two
things at once, the API and the transform path, so a difference from the
software rasteriser could come from either.

**B. Run OpenGL on Vulkan (Zink).** Rejected. It gives a Vulkan driver
without writing one, but nothing here is owned, measured or new.

**C. Direct3D 11 or 12 first.** Rejected as a first step: Windows only, and
CI cannot run it without a GPU.

**D. Three stages, each measured against the software rasteriser.** Chosen.

## Decision

1. **Stage A: a headless Vulkan rasteriser.** Built here.
   `modern/vulkan/vk_offscreen.c` and `vk_pipeline.c` create an instance and
   a device with no window, draw flat-coloured screen-space triangles into an
   RGBA8 image and read it back. `vk_triangle.c` draws the same triangles
   through softrend + softprim, as one-face models under a parallel camera
   whose view volume is exactly the buffer. `vk_compare.py` compares the two
   frames. This settles the questions every later stage depends on: where
   pixel centres fall, which edges own their pixels, how colours quantise,
   how readback works, and whether lavapipe gives the same bytes every run.
2. **Stage B: vkprim, a primitive library on Vulkan.** Proposed. softrend
   keeps doing geometry, lighting and clipping, and hands its screen-space
   triangles to a Vulkan primitive library instead of softprim. Both sides
   then rasterise the same vertices, so a parity difference is a
   rasterisation difference and nothing else. It starts with flat and
   Gouraud untextured triangles into RGB_888 with 16-bit depth, then adds
   textures.
3. **Stage C: vkrend, a renderer facility like glrend.** Proposed. Transform
   and lighting move to the GPU. It shares glrend's GLSL, compiled to SPIR-V
   with glslang, which the OpenGL build already uses. It presents through an
   SDL3 Vulkan surface. It is held to the same bounds item 5 sets for OpenGL.

All of it is original code under MIT. An upstream offer to BlazingRenderer
waits until the author lifts the hold on upstream reports.

## Stage A: what was measured (17 October 2026)

Mesa lavapipe (llvmpipe, LLVM 20.1.2) on WSL Ubuntu 24.04 against BRender
1.4's software rasteriser, 320 x 240, four scenes:

| Scene | Coverage IoU | Pixels only Vulkan / only software | Colour within 1 level where both draw | MAD |
|---|---|---|---|---|
| triangle (no edge on a pixel boundary) | 0.9913 | 38 / 160 | 100% | 2.12 |
| quad (two triangles sharing a diagonal) | 1.0 | 0 / 0 | 99.75% | 0.71 |
| slivers (eight thin triangles) | 0.9137 | 188 / 233 | 100% | 13.95 |
| offset (the triangle moved half a pixel) | 0.9897 | 157 / 78 | 100% | 2.40 |

- **Same bytes every run:** two runs on lavapipe are identical, and so are
  two runs of the software rasteriser.
- **Coverage:** the two disagree only on edges. Vulkan follows its
  specification's top-left rule. The software rasteriser draws about 0.5%
  more of a general triangle, most of it along one long edge.
  `software-left-vulkan-middle-2026-10-17.png` maps every pixel that
  differs.
- **Shared edges:** neither leaves a gap or draws a pixel twice. On the
  shared diagonal, Vulkan splits the pixels evenly (16,000 and 16,000); the
  software rasteriser gives 80 more to the first triangle.
- **Colour:** the software rasteriser writes some flat colours one level
  low: 232, 180, 92 comes out 231, 179, 92, and 200 becomes 199. Channel
  values of 120 and below come through unchanged. This matches the colour
  scale softprim applies (offset 1, scale 254, in softprim `match.c`), but
  that link is not traced value by value. Vulkan writes the exact bytes.
- **Control:** Vulkan's triangle against the software quad gives coverage
  IoU 0.63, so the measure can tell scenes apart.

CI runs stage A on Linux with lavapipe forced (`VK_DRIVER_FILES`,
`VKO_DEVICE_TYPE=cpu`). It requires two identical runs and holds every scene
to coverage IoU 0.91, colour within one level on 99.7% of the pixels both
draw, and MAD 14.5. Those bounds come from the table above, so they are
calibrated, not predicted. Windows CI has no Vulkan SDK, so stage A is
Linux-only for now.

## Consequences

- Stage B must choose one edge rule. Following Vulkan's means accepting the
  edge differences measured above. Matching softprim's means writing it
  into the vertex positions or the fragment test. Stage A's numbers are the
  baseline for either choice.
- The colour quantisation lives on the software side, so a Vulkan stage
  will not match it exactly unless it copies the scale on purpose.
- The build gains an option, `BRENDER_VULKAN`, off by default. It needs the
  Vulkan headers and loader and `glslangValidator`; the usual builds and the
  releases do not change.
- Local runs use lavapipe only, so no GPU is touched while other work holds
  it.
