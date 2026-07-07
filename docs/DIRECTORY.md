# Lost Engine Directory

This archive does two things. It hosts archival restorations of the engines it
rebuilds itself, and it acts as a directory for finding other lost or dormant
rendering and game engine resources. When a project is actively maintained, the
archive does not fork or re-host it; it points to the maintainer.

## Restorations hosted here

Engines rebuilt in this repository, with a reproducible harness and a verified
build.

| Engine | State | Where |
|---|---|---|
| Argonaut BRender v1.3.2 | portable pure-C render path complete (loads and renders real `.dat` models) | [BRender packet](BRENDER-ARCHIVAL.md) |

## Actively maintained: go to the maintainer

These were assessed and found to be living projects. The archive indexes them as
lineage and interop references and does not attempt a revival. Use the upstream
repository.

| Project | Maintainer repository | License |
|---|---|---|
| Mesa 3D | https://gitlab.freedesktop.org/mesa/mesa | MIT (core; per-file SPDX exceptions) |
| OGRE | https://github.com/OGRECave/ogre | MIT (LGPL before v1.7) |
| Quesa (QuickDraw 3D API) | https://github.com/jwwalker/Quesa | BSD-3-Clause |
| Open Inventor | https://github.com/aumuell/open-inventor | maintained fork |
| PHIGS (CERN OpenPHIGS) | CERN OpenPHIGS | permissive (X Consortium / Sun) |
| PSn00bSDK (PS1 clean-room SDK) | https://github.com/Lameguy64/PSn00bSDK | MPL-2.0 (sub-tools GPL) |
| OpenGOAL (Jak/GOAL) | https://github.com/open-goal/jak-project | ISC |
| LithTech Jupiter (ltjs) | https://github.com/bibendovsky/ltjs | rights unresolved; see note |

Note on ltjs: the original Jupiter EX source carries an in-tree "all rights
reserved" LithTech copyright, and the widely-repeated GPLv2 release claim has no
primary-source corroboration. The archive treats its rights posture as
unresolved and links the maintained fork for reference only.

## Lost or reference-only: leads worth pursuing

Genuinely lost, dormant, or source-restricted engines. Some are buildable revival
candidates, others can only be dossiers. Confidence varies; entries are leads,
not claims.

### Buildable revival candidates (genuinely lost)

- Crystal Space 3D (github.com/crystalspace/CS, LGPL, dead since ~2011).
- RenderWare, via the `aap/librw` clean-room substrate (original Criterion/EA
  source is lost/restricted).
- Aqsis and Pixie (RenderMan-compliant renderers, dormant mirrors).

### Missing from the roster, worth adding

- Cosmo3D (SGI).
- N64 GBI / Fast3D microcode family.
- Sega Saturn SGL / SBL.
- Sony PS1 LIBGPU / LIBGTE / LIBGS (Psy-Q / Programmer's Tool).
- trueSpace / Caligari (Octree Software renderer).
- BMRT (Blue Moon Rendering Tools) and its Entropy / Gelato lineage.
- RealSpace Engine (Origin Systems, Wing / Strike Commander).
- Blade Runner Engine (Westwood Studios).
- Mercenary / Damocles (Novagen, Paul Woakes).
- MathEngine Karma.
- TDI Explore (Thomson Digital Image).

### Reference-only (dossier deliverables)

IRIS GL, OpenGL Performer core (SGI never released libpf/libpr), QuickDraw 3D
(Apple source never released), Reality Lab (RenderMorphics), the RenderMan
interface specification, Softimage/Alias pipeline history, the tri-Ace PS2
renderer (GDC 2005 slides only), Sony ProDG/EB for PS2, and studio-heritage
lineages such as Psygnosis Liverpool and Team Ico.

Restricted material is indexed as rights-posture metadata only. This directory
never links to redistribution of proprietary source, leaked SDKs, or assets.
