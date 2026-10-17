# SPDX-License-Identifier: MIT
# The Vulkan backend, stage A (docs/adr/0002-vulkan-backend.md): a headless
# rasteriser and its parity check against the software rasteriser. Built only
# with -DBRENDER_VULKAN=ON; needs the Vulkan headers and loader and
# glslangValidator. A measuring tool: never installed.
find_package(Vulkan REQUIRED)
find_program(GLSLANG_VALIDATOR glslangValidator REQUIRED)

set(vk_shader_headers)
foreach(stage vert frag)
  set(header "${CMAKE_CURRENT_BINARY_DIR}/tri_${stage}.h")
  add_custom_command(OUTPUT "${header}"
    COMMAND "${GLSLANG_VALIDATOR}" -V --vn tri_${stage} -o "${header}" "${CMAKE_CURRENT_SOURCE_DIR}/tri.${stage}"
    DEPENDS "${CMAKE_CURRENT_SOURCE_DIR}/tri.${stage}"
    COMMENT "SPIR-V for tri.${stage}")
  list(APPEND vk_shader_headers "${header}")
endforeach()

add_executable(vk-triangle vk_triangle.c vk_offscreen.c vk_pipeline.c vk_offscreen.h vk_offscreen_ip.h ${vk_shader_headers})
target_include_directories(vk-triangle PRIVATE "${CMAKE_CURRENT_BINARY_DIR}")
# Beside brview and parity-scene, so it finds the same SDL3 library.
set_target_properties(vk-triangle PROPERTIES RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}")
target_link_libraries(vk-triangle PRIVATE BRender::DDI BRender::Drivers::SoftRend BRender::Drivers::SoftPrim BRender::Drivers::SDL3Dev Vulkan::Vulkan)
if(MSVC)
  target_compile_definitions(vk-triangle PRIVATE _CRT_SECURE_NO_WARNINGS)
endif()
if(WIN32)
  add_custom_command(TARGET vk-triangle POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E copy_if_different $<TARGET_FILE:SDL3::SDL3> $<TARGET_FILE_DIR:vk-triangle>)
else()
  set_target_properties(vk-triangle PROPERTIES BUILD_WITH_INSTALL_RPATH ON INSTALL_RPATH "$ORIGIN")
  add_custom_command(TARGET vk-triangle POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E copy_if_different $<TARGET_FILE:SDL3::SDL3>
            $<TARGET_FILE_DIR:vk-triangle>/$<TARGET_SONAME_FILE_NAME:SDL3::SDL3>)
endif()
