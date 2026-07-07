from __future__ import annotations


def cmake_project_source(core_float_defines: tuple[str, ...]) -> str:
    compile_definitions = "\n".join(f"  {definition}" for definition in core_float_defines)
    return f"""cmake_minimum_required(VERSION 3.20)
project(brender_v132_portable_core C)
enable_testing()

if(NOT CMAKE_SIZEOF_VOID_P EQUAL 4)
  message(FATAL_ERROR
    "BRender v1.3.2 harness currently requires a 32-bit C target; "
    "use -A Win32 with Visual Studio.")
endif()

set(BRENDER_SOURCE_DIR "" CACHE PATH "Path to the public BRender v1.3.2 checkout")
if(NOT BRENDER_SOURCE_DIR)
  message(FATAL_ERROR "Set -DBRENDER_SOURCE_DIR=<public BRender checkout>")
endif()
get_filename_component(BRENDER_SOURCE_DIR "${{BRENDER_SOURCE_DIR}}" ABSOLUTE)

include(${{CMAKE_CURRENT_LIST_DIR}}/cmake/brender-core-sources.cmake)

set(BRENDER_PORTABLE_COMPAT_SOURCES
  "${{CMAKE_CURRENT_LIST_DIR}}/compat/brender-portable-core-stubs.c"
  "${{CMAKE_CURRENT_LIST_DIR}}/compat/brender-portable-host-stubs.c"
)

set(BRENDER_CORE_INCLUDE_DIRS
  "${{BRENDER_SOURCE_DIR}}/inc"
  "${{BRENDER_SOURCE_DIR}}/core/inc"
  "${{BRENDER_SOURCE_DIR}}/core/fw"
  "${{BRENDER_SOURCE_DIR}}/core/host"
  "${{BRENDER_SOURCE_DIR}}/core/std"
  "${{BRENDER_SOURCE_DIR}}/core/pixelmap"
  "${{BRENDER_SOURCE_DIR}}/core/dosio"
  "${{BRENDER_SOURCE_DIR}}/core/v1db"
  "${{BRENDER_SOURCE_DIR}}/core/math"
  "${{BRENDER_SOURCE_DIR}}/core/fmt"
)

set(BRENDER_CORE_V1DB_DISABLED_SOURCES
  ${{BRENDER_CORE_FLOAT_FW_SOURCES}}
  ${{BRENDER_CORE_FLOAT_HOST_SOURCES}}
  ${{BRENDER_CORE_FLOAT_STD_SOURCES}}
  ${{BRENDER_CORE_FLOAT_PIXELMAP_SOURCES}}
  ${{BRENDER_CORE_FLOAT_DOSIO_SOURCES}}
  ${{BRENDER_CORE_FLOAT_MATH_SOURCES}}
)

foreach(source_file IN LISTS BRENDER_CORE_V1DB_DISABLED_SOURCES)
  set_property(SOURCE "${{source_file}}" APPEND PROPERTY COMPILE_DEFINITIONS __BR_V1DB__=0)
endforeach()

foreach(source_file IN LISTS BRENDER_CORE_FLOAT_HOST_SOURCES)
  set_property(SOURCE "${{source_file}}" APPEND PROPERTY COMPILE_DEFINITIONS __WIN_32__=1)
endforeach()

add_library(brender_core_float STATIC
  ${{BRENDER_CORE_FLOAT_SOURCES}}
  ${{BRENDER_PORTABLE_COMPAT_SOURCES}}
)
target_include_directories(brender_core_float PRIVATE ${{BRENDER_CORE_INCLUDE_DIRS}})
target_compile_definitions(brender_core_float PRIVATE
{compile_definitions}
)

add_executable(brender_core_smoke smoke/brender-core-smoke.c)
target_include_directories(brender_core_smoke PRIVATE ${{BRENDER_CORE_INCLUDE_DIRS}})
target_compile_definitions(brender_core_smoke PRIVATE
{compile_definitions}
)
target_link_libraries(brender_core_smoke PRIVATE brender_core_float)
add_test(NAME brender_core_smoke COMMAND brender_core_smoke)

add_executable(brender_core_startup_smoke smoke/brender-core-startup-smoke.c)
target_include_directories(brender_core_startup_smoke PRIVATE ${{BRENDER_CORE_INCLUDE_DIRS}})
target_compile_definitions(brender_core_startup_smoke PRIVATE
{compile_definitions}
)
target_link_libraries(brender_core_startup_smoke PRIVATE brender_core_float)
add_test(NAME brender_core_startup_smoke COMMAND brender_core_startup_smoke)

add_executable(brender_core_render_smoke smoke/brender-core-render-smoke.c)
target_include_directories(brender_core_render_smoke PRIVATE ${{BRENDER_CORE_INCLUDE_DIRS}})
target_compile_definitions(brender_core_render_smoke PRIVATE
{compile_definitions}
)
target_link_libraries(brender_core_render_smoke PRIVATE brender_core_float)
add_test(NAME brender_core_render_smoke
  COMMAND brender_core_render_smoke brender-core-render-smoke.ppm)

add_executable(brender_core_scene_smoke smoke/brender-core-scene-smoke.c)
target_include_directories(brender_core_scene_smoke PRIVATE ${{BRENDER_CORE_INCLUDE_DIRS}})
target_compile_definitions(brender_core_scene_smoke PRIVATE
{compile_definitions}
)
target_link_libraries(brender_core_scene_smoke PRIVATE brender_core_float)
add_test(NAME brender_core_scene_smoke
  COMMAND brender_core_scene_smoke brender-core-scene-smoke.ppm)

add_executable(brender_core_fill_smoke smoke/brender-core-fill-smoke.c)
target_include_directories(brender_core_fill_smoke PRIVATE ${{BRENDER_CORE_INCLUDE_DIRS}})
target_compile_definitions(brender_core_fill_smoke PRIVATE
{compile_definitions}
)
target_link_libraries(brender_core_fill_smoke PRIVATE brender_core_float)
add_test(NAME brender_core_fill_smoke
  COMMAND brender_core_fill_smoke brender-core-fill-smoke.ppm)

add_executable(brender_core_depth_smoke smoke/brender-core-depth-smoke.c)
target_include_directories(brender_core_depth_smoke PRIVATE ${{BRENDER_CORE_INCLUDE_DIRS}})
target_compile_definitions(brender_core_depth_smoke PRIVATE
{compile_definitions}
)
target_link_libraries(brender_core_depth_smoke PRIVATE brender_core_float)
add_test(NAME brender_core_depth_smoke
  COMMAND brender_core_depth_smoke brender-core-depth-smoke.ppm)

add_executable(brender_core_texture_smoke smoke/brender-core-texture-smoke.c)
target_include_directories(brender_core_texture_smoke PRIVATE ${{BRENDER_CORE_INCLUDE_DIRS}})
target_compile_definitions(brender_core_texture_smoke PRIVATE
{compile_definitions}
)
target_link_libraries(brender_core_texture_smoke PRIVATE brender_core_float)
add_test(NAME brender_core_texture_smoke
  COMMAND brender_core_texture_smoke brender-core-texture-smoke.ppm)

add_executable(brender_core_model_smoke smoke/brender-core-model-smoke.c)
target_include_directories(brender_core_model_smoke PRIVATE ${{BRENDER_CORE_INCLUDE_DIRS}})
target_compile_definitions(brender_core_model_smoke PRIVATE
{compile_definitions}
)
target_link_libraries(brender_core_model_smoke PRIVATE brender_core_float)
add_test(NAME brender_core_model_smoke
  COMMAND brender_core_model_smoke
    "${{BRENDER_SOURCE_DIR}}/dat/duck.dat" brender-core-model-smoke.ppm)

add_executable(brender_core_material_smoke smoke/brender-core-material-smoke.c)
target_include_directories(brender_core_material_smoke PRIVATE ${{BRENDER_CORE_INCLUDE_DIRS}})
target_compile_definitions(brender_core_material_smoke PRIVATE
{compile_definitions}
)
target_link_libraries(brender_core_material_smoke PRIVATE brender_core_float)
add_test(NAME brender_core_material_smoke
  COMMAND brender_core_material_smoke
    "${{BRENDER_SOURCE_DIR}}/dat/sph32.dat" brender-core-material-smoke.ppm)

add_executable(brender_core_multimodel_smoke smoke/brender-core-multimodel-smoke.c)
target_include_directories(brender_core_multimodel_smoke PRIVATE ${{BRENDER_CORE_INCLUDE_DIRS}})
target_compile_definitions(brender_core_multimodel_smoke PRIVATE
{compile_definitions}
)
target_link_libraries(brender_core_multimodel_smoke PRIVATE brender_core_float)
add_test(NAME brender_core_multimodel_smoke
  COMMAND brender_core_multimodel_smoke
    "${{BRENDER_SOURCE_DIR}}/dat/coupe.dat" brender-core-multimodel-smoke.ppm)

add_executable(brender_core_gouraud_smoke smoke/brender-core-gouraud-smoke.c)
target_include_directories(brender_core_gouraud_smoke PRIVATE ${{BRENDER_CORE_INCLUDE_DIRS}})
target_compile_definitions(brender_core_gouraud_smoke PRIVATE
{compile_definitions}
)
target_link_libraries(brender_core_gouraud_smoke PRIVATE brender_core_float)
add_test(NAME brender_core_gouraud_smoke
  COMMAND brender_core_gouraud_smoke
    "${{BRENDER_SOURCE_DIR}}/dat/sph32.dat" brender-core-gouraud-smoke.ppm)

add_executable(brender_core_plotter_smoke smoke/brender-core-plotter-smoke.c)
target_include_directories(brender_core_plotter_smoke PRIVATE ${{BRENDER_CORE_INCLUDE_DIRS}})
target_compile_definitions(brender_core_plotter_smoke PRIVATE
{compile_definitions}
)
target_link_libraries(brender_core_plotter_smoke PRIVATE brender_core_float)
add_test(NAME brender_core_plotter_smoke
  COMMAND brender_core_plotter_smoke
    "${{BRENDER_SOURCE_DIR}}/dat/teapot.dat"
    brender-core-plotter-smoke.svg brender-core-plotter-smoke.ppm)
"""


def readme_source() -> str:
    return """# BRender v1.3.2 Portable Core Harness

This harness materializes an out-of-tree CMake scaffold for the public BRender
v1.3.2 source checkout. It does not vendor BRender source, generated binaries,
private assets, or restricted SDK material.

```powershell
cmake -S . -B build -A Win32 "-DBRENDER_SOURCE_DIR=<path-to-public-brender-checkout>"
cmake --build build --config Debug --target brender_core_float
cmake --build build --config Debug --target brender_core_smoke
cmake --build build --config Debug --target brender_core_startup_smoke
cmake --build build --config Debug --target brender_core_render_smoke
cmake --build build --config Debug --target brender_core_scene_smoke
cmake --build build --config Debug --target brender_core_fill_smoke
cmake --build build --config Debug --target brender_core_depth_smoke
cmake --build build --config Debug --target brender_core_texture_smoke
cmake --build build --config Debug --target brender_core_model_smoke
ctest --test-dir build -C Debug --output-on-failure
```

The `brender_core_model_smoke` target loads a real period model from the public
checkout's `dat/` directory with `BrModelLoad` and renders it solid, flat-shaded
and depth-buffered. It reads the model file directly from `BRENDER_SOURCE_DIR`;
no BRender asset is copied into the harness.

The `brender_core_render_smoke` target renders a projected 3D wireframe cube
into an in-memory pixelmap through the pure-C memory dispatch path (no assembly
software driver) and writes a PPM image next to the executable. The
`brender_core_scene_smoke` target goes further: it starts BRender's v1db scene
database, builds a world/camera/model actor tree, and uses the engine's own
`BrActorToScreenMatrix4` to project a registered `br_model` cube before drawing
its faces. The `brender_core_fill_smoke` target goes one step further and
produces a solid, flat-shaded image: it reuses the scene projection, then
rasterizes each triangle face with a C scanline fill, shaded from the world-space
face normal and composited back-to-front. Keep the generated images out of git
unless they are intentionally reviewed as public release artifacts.

The first compiler run is expected to produce portability findings. Record the
transcript before advancing production-readiness status.
"""
