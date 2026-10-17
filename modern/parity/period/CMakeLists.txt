# The parity scenes on BRender 1.3.2 (Argonaut, 1998): softrend + pentprim,
# built 32-bit from the public source by the materialized harness.
#
#   engine-revival materialize-brender-harness --source-root <BRender-v1.3.2> --output-root <harness>
#   cmake -S modern/parity/period -B <build> -A Win32 -DBRENDER_HARNESS_DIR=<harness> -DBRENDER_SOURCE_DIR=<BRender-v1.3.2>
#   cmake --build <build> --config Debug --target parity_scene_period
#
# The flags are those of the harness's own renderer rung. Add
# -DBRENDER_PENTPRIM_MMX=ON (engine-revival 0.9.0) to build pentprim as a
# Pentium with MMX runs it: 15/16-bit triangles then go through its MMX table,
# the 1998 path BRender 1.4 reproduces.
cmake_minimum_required(VERSION 3.23)
project(brender_parity_period C)

set(BRENDER_HARNESS_DIR "" CACHE PATH "Materialized BRender v1.3.2 harness")
if(NOT BRENDER_HARNESS_DIR OR NOT BRENDER_SOURCE_DIR)
  message(FATAL_ERROR "Set -DBRENDER_HARNESS_DIR=<harness> and -DBRENDER_SOURCE_DIR=<BRender-v1.3.2 checkout>")
endif()
add_subdirectory("${BRENDER_HARNESS_DIR}" harness)

add_executable(parity_scene_period ../parity-scene.c)
target_include_directories(parity_scene_period PRIVATE
  ${BRENDER_SOURCE_DIR}/inc
  ${BRENDER_SOURCE_DIR}/core/inc
  ${BRENDER_SOURCE_DIR}/ddi_inc)
target_compile_definitions(parity_scene_period PRIVATE
  BASED_FLOAT=1 BASED_FIXED=0 INLINE_FIXED=0 __386__=1 DEBUG=0 PARANOID=0 EVAL=0
  STATIC=static ADD_RCS_ID=0 PARITY_PERIOD=1 _CRT_SECURE_NO_WARNINGS)
target_link_libraries(parity_scene_period PRIVATE brender_core_float brender_softrend_float brender_pentprim_float)
