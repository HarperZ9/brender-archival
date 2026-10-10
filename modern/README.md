# BRender on a modern PC

Run Argonaut's 1990s BRender engine on a 64-bit Windows PC, open its period
sample models in a viewer, and check that the restored engine still does what
the 1998 one did.

## Get the viewer

Download `brview-<version>-windows-x64.zip` from the
[releases page](https://github.com/HarperZ9/brender-archival/releases), unzip
it and double-click `brview.exe`. Nothing to install. The zip carries its
SHA-256 beside it.

| Input | Action |
|---|---|
| Mouse drag | orbit |
| Right or middle drag | pan |
| Wheel, Q and E | zoom |
| WASD or arrow keys | orbit |
| Tab or N, P | next, previous model |
| T | texture on or off |
| Space | spin on or off |
| R | reset the view |
| H or F1 | hide the help |
| Alt+Enter | fullscreen |
| Gamepad | left stick orbit, triggers zoom, A next, X previous, B spin, Y texture, Start reset |

```
brview.exe                    cycle through the bundled models
brview.exe my.dat my.pix      open your own model and texture
brview.exe --force-software   draw with BRender's software rasteriser
```

## What it is built on

The engine is **BRender 1.4 from [BlazingRenderer/BRender](https://github.com/BlazingRenderer/BRender)**,
the maintained modern fork by Zane van Iperen, erysdren and contributors
(MIT). It replaces the x86 assembly rasteriser with portable C, adds SDL2/SDL3
and OpenGL drivers, and builds 64-bit. This repository does not fork it: the
build pins one commit and fetches it, and the credit and licence travel with
every binary.

That choice can be reversed. If the archive later needs its own 64-bit
branch of the 1.3.2 source, `modern/` is the only place that names the
dependency, and the period build in the rest of this repository does not use it.

| Part | Source | Licence | Pin |
|---|---|---|---|
| Engine | BlazingRenderer/BRender | MIT | commit `ed5e7a91` |
| Window, input, gamepad | SDL3 | zlib | `release-3.4.16` |
| Sample models and textures | foone/BRender-v1.3.2 (Argonaut Software, 1998) | MIT | commit `d88d0ed4` |
| brview, ladder64 | this repository | MIT | |

## Build it yourself

Needs CMake 3.24 or newer and a C compiler (Visual Studio 2022 or newer on
Windows). The first configure fetches the three pinned sources.

```
cmake -S modern -B build -A x64
cmake --build build --config Release
build\Release\brview.exe
```

To build against a local BlazingRenderer checkout, add
`-DBLAZINGRENDERER_SOURCE_DIR=<checkout>`.

## The 21-step ladder, 64-bit

The period ladder (21 test programs, from vector maths to a textured model
drawn by the renderer) builds BRender 1.3.2 itself, Win32 only. `ladder64`
runs the same programs against BRender 1.4, 64-bit:

```
pip install -e .
engine-revival materialize-brender-harness --source-root BRender-v1.3.2 --output-root harness
python modern/ladder64/make_ladder64.py harness ladder64
cmake -S ladder64 -B ladder64-build -A x64 -DBLAZINGRENDERER_SOURCE_DIR=<checkout> -DBRENDER_SOURCE_DIR=BRender-v1.3.2
cmake --build ladder64-build --config Release
ctest --test-dir ladder64-build -C Release
```

Result on 10 October 2026: **21 of 21 pass** on x64 (Visual Studio 18 2026,
SDL3 3.4.16, BlazingRenderer `ed5e7a91`). CI runs it on every change.

Two documented differences between 1.3.2 and 1.4 are bridged, and nothing else:

- `BR_COLOUR_RGB` gains an opaque alpha byte in 1.4. The 20 period programs
  compare pixels against 1.3.2 colours, so a force-included header gives them
  the 1.3.2 macro. Their source is unchanged.
- 1.4 replaces pentprim with softprim and begins a renderer differently, so
  the renderer step is a 1.4 program (`ladder64/softrend-render-14.c`). It
  makes a stronger claim than the period one: more than 500 lit pixels and more
  than 500 coloured pixels, so a grey, untextured frame fails.
