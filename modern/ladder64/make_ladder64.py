"""Turn the period BRender ladder into one that links a modern 64-bit BRender.

    python make_ladder64.py <materialized-harness> <output-dir>

The materialized harness (from `engine-revival materialize-brender-harness`)
builds BRender v1.3.2 itself, Win32 only. This writes a CMake project that
keeps the same 21 test programs and the same CTest commands, but links them
against BlazingRenderer/BRender (MIT), built as a subproject, which builds
64-bit. The period data files still come from BRENDER_SOURCE_DIR.

Two documented differences between 1.3.2 and 1.4 are bridged:
- BR_COLOUR_RGB gains an opaque alpha byte in 1.4; the programs compare
  against 1.3.2 colours, so a force-included header restores the 1.3.2 macro.
- pentprim is replaced by softprim in 1.4, and a renderer is begun through
  BrRendererBegin and framed by BrRendererFrameBegin/End. The renderer rung
  is therefore the 1.4 program softrend-render-14.c, which makes the same
  claim (eight orbit frames of a textured .dat model, over 500 lit pixels).
  The other 20 programs are unchanged.
"""
from __future__ import annotations

import re
import shutil
import sys
from pathlib import Path

HEADER = """cmake_minimum_required(VERSION 3.23)
project(brender_ladder64 C CXX)

# The modern BRender these rungs link against: a checkout of
# BlazingRenderer/BRender (MIT), built here as a subproject.
set(BLAZINGRENDERER_SOURCE_DIR "" CACHE PATH "Path to a BlazingRenderer/BRender checkout")
if(NOT BLAZINGRENDERER_SOURCE_DIR)
  message(FATAL_ERROR "Set -DBLAZINGRENDERER_SOURCE_DIR=<BlazingRenderer/BRender checkout>")
endif()
set(BRENDER_BUILD_EXAMPLES OFF CACHE BOOL "" FORCE)
set(BRENDER_BUILD_TOOLS OFF CACHE BOOL "" FORCE)
set(BRENDER_DISABLE_INSTALL ON CACHE BOOL "" FORCE)
set(BRENDER_USE_SDL3 ON CACHE BOOL "" FORCE)
set(BRENDER_DISABLE_FINDSDL ON CACHE BOOL "" FORCE)
set(BUILD_TESTING OFF CACHE BOOL "" FORCE)
# SDL3 (zlib) drives the headless device the renderer rung draws through.
find_package(SDL3 CONFIG QUIET COMPONENTS SDL3)
if(NOT TARGET SDL3::SDL3)
  include(FetchContent)
  set(SDL_SHARED ON CACHE BOOL "" FORCE)
  set(SDL_STATIC OFF CACHE BOOL "" FORCE)
  set(SDL_TEST_LIBRARY OFF CACHE BOOL "" FORCE)
  FetchContent_Declare(sdl3 GIT_REPOSITORY https://github.com/libsdl-org/SDL.git GIT_TAG release-3.4.16 GIT_SHALLOW TRUE)
  FetchContent_MakeAvailable(sdl3)
endif()
add_subdirectory("${BLAZINGRENDERER_SOURCE_DIR}" blazingrenderer EXCLUDE_FROM_ALL)
set(BUILD_TESTING ON CACHE BOOL "" FORCE)
enable_testing()

set(BRENDER_SOURCE_DIR "" CACHE PATH "Path to the public BRender v1.3.2 checkout (period data files)")
if(NOT BRENDER_SOURCE_DIR)
  message(FATAL_ERROR "Set -DBRENDER_SOURCE_DIR=<public BRender v1.3.2 checkout>")
endif()
get_filename_component(BRENDER_SOURCE_DIR "${BRENDER_SOURCE_DIR}" ABSOLUTE)

if(MSVC)
  add_compile_definitions(_CRT_SECURE_NO_WARNINGS)
endif()

set(LADDER64_COMPAT "${CMAKE_CURRENT_LIST_DIR}/ladder64-compat.h")
"""

COMPAT_HEADER = r"""/* Seen before every ladder program: the 1.3.2 meaning of BR_COLOUR_RGB.
 * BRender 1.4 adds an opaque alpha byte to BR_COLOUR_RGB (see its MIGRATION.md);
 * the ladder programs compare pixels against 1.3.2 colours. */
#ifndef LADDER64_COMPAT_H
#define LADDER64_COMPAT_H
#include "brender.h"
#undef BR_COLOUR_RGB
#define BR_COLOUR_RGB(r, g, b) \
    ((((br_colour)(r)) << 16) | (((br_colour)(g)) << 8) | ((br_colour)(b)))
#endif
"""

RENDERER_RUNG = "brender_core_softrend_render"
RENDERER_LIBS = "BRender::DDI BRender::Drivers::SoftRend BRender::Drivers::SoftPrim sdl3dev"
CMAKE_FILES = ("CMakeLists.txt", "cmake/brender-softrend.cmake")
EXE_RE = re.compile(r"add_executable\((\w+) (smoke/[\w.-]+\.c)\)")
TEST_RE = re.compile(r"add_test\(NAME (\w+)\b.*?\)\n", re.S)
FORCE_INCLUDE = '"$<IF:$<C_COMPILER_ID:MSVC>,/FI${LADDER64_COMPAT},-include;${LADDER64_COMPAT}>"'
NEWLINE = "\n"


def _rung_block(name: str, source: str, test: str) -> str:
    libs = "BRender::Core" + (f" {RENDERER_LIBS}" if name == RENDERER_RUNG else "")
    return (
        f"add_executable({name} {source})\n"
        f"target_link_libraries({name} PRIVATE {libs})\n"
        f"target_compile_options({name} PRIVATE {FORCE_INCLUDE})\n"
        f"{test}"
        + (RENDERER_EXTRA.format(name=name) if name == RENDERER_RUNG else "")
    )


RENDERER_EXTRA = """set_tests_properties({name} PROPERTIES ENVIRONMENT SDL_VIDEODRIVER=offscreen)
if(WIN32)
  add_custom_command(TARGET {name} POST_BUILD
    COMMAND ${{CMAKE_COMMAND}} -E copy_if_different $<TARGET_FILE:SDL3::SDL3> $<TARGET_FILE_DIR:{name}>)
endif()
"""


def convert(harness: Path, out: Path) -> int:
    text = NEWLINE.join((harness / name).read_text(encoding="utf-8") for name in CMAKE_FILES)
    exes = EXE_RE.findall(text)
    tests = {match.group(1): match.group(0) for match in TEST_RE.finditer(text)}
    if out.exists():
        shutil.rmtree(out)
    (out / "smoke").mkdir(parents=True)
    blocks = [HEADER]
    for name, source in exes:
        code = (harness / source).read_text(encoding="utf-8")
        if name == RENDERER_RUNG:
            code = (Path(__file__).parent / "softrend-render-14.c").read_text(encoding="utf-8")
        (out / source).write_text(code, encoding="utf-8", newline=NEWLINE)
        blocks.append(_rung_block(name, source, tests[name]))
    (out / "ladder64-compat.h").write_text(COMPAT_HEADER, encoding="utf-8", newline=NEWLINE)
    (out / "CMakeLists.txt").write_text(NEWLINE.join(blocks), encoding="utf-8", newline=NEWLINE)
    return len(exes)


if __name__ == "__main__":
    count = convert(Path(sys.argv[1]), Path(sys.argv[2]))
    print(f"wrote {count} rungs to {sys.argv[2]}")
