cmake_minimum_required(VERSION 3.24)
project(brender_modern C CXX)

# BRender 1.4 from BlazingRenderer/BRender (MIT), pinned by commit. Pass
# -DBLAZINGRENDERER_SOURCE_DIR=<checkout> to build against a local tree.
set(BLAZINGRENDERER_COMMIT ed5e7a911e394b58803dca681a34f1864431f9d7)
# SDL3 (zlib) for the window, input and gamepad layer, pinned by release tag.
set(SDL3_TAG release-3.4.16)
# The period sample models (MIT, Argonaut Software 1998), pinned by commit.
set(BRENDER132_COMMIT d88d0ed41122664b9781015b517db64353e16f19)

include(FetchContent)

find_package(SDL3 CONFIG QUIET COMPONENTS SDL3)
if(NOT TARGET SDL3::SDL3)
  set(SDL_SHARED ON CACHE BOOL "" FORCE)
  set(SDL_STATIC OFF CACHE BOOL "" FORCE)
  set(SDL_TEST_LIBRARY OFF CACHE BOOL "" FORCE)
  FetchContent_Declare(sdl3 GIT_REPOSITORY https://github.com/libsdl-org/SDL.git GIT_TAG ${SDL3_TAG} GIT_SHALLOW TRUE)
  FetchContent_MakeAvailable(sdl3)
endif()

set(BRENDER_USE_SDL3 ON CACHE BOOL "" FORCE)
# SDL3::SDL3 already exists in this scope, from either route above.
set(BRENDER_DISABLE_FINDSDL ON CACHE BOOL "" FORCE)
set(BRENDER_BUILD_EXAMPLES OFF CACHE BOOL "" FORCE)
set(BRENDER_BUILD_TOOLS OFF CACHE BOOL "" FORCE)
set(BRENDER_DISABLE_INSTALL ON CACHE BOOL "" FORCE)
set(BUILD_TESTING OFF CACHE BOOL "" FORCE)
if(BLAZINGRENDERER_SOURCE_DIR)
  add_subdirectory("${BLAZINGRENDERER_SOURCE_DIR}" blazingrenderer EXCLUDE_FROM_ALL)
  set(BRDEMO_DIR "${BLAZINGRENDERER_SOURCE_DIR}/examples/brdemo")
else()
  FetchContent_Declare(blazingrenderer GIT_REPOSITORY https://github.com/BlazingRenderer/BRender.git GIT_TAG ${BLAZINGRENDERER_COMMIT})
  FetchContent_MakeAvailable(blazingrenderer)
  set(BRDEMO_DIR "${blazingrenderer_SOURCE_DIR}/examples/brdemo")
endif()
# brdemo is BlazingRenderer's window layer (MIT); brview builds on it.
add_subdirectory("${BRDEMO_DIR}" brdemo EXCLUDE_FROM_ALL)

if(NOT BRENDER132_SOURCE_DIR)
  FetchContent_Declare(brender132 GIT_REPOSITORY https://github.com/foone/BRender-v1.3.2.git GIT_TAG ${BRENDER132_COMMIT})
  FetchContent_GetProperties(brender132)
  if(NOT brender132_POPULATED)
    FetchContent_Populate(brender132)
  endif()
  set(BRENDER132_SOURCE_DIR "${brender132_SOURCE_DIR}")
endif()

add_executable(brview viewer/brview.c viewer/brview_scenes.c viewer/brview_scenes.h)
target_link_libraries(brview PRIVATE brdemo)
if(MSVC)
  target_compile_definitions(brview PRIVATE _CRT_SECURE_NO_WARNINGS)
endif()

set(BRVIEW_DAT
  sph32.dat earth.pix teapot.dat skull.dat argo.dat ship.dat duck.dat
  torus.dat rosewood.pix terrain.dat std.pal)
foreach(f IN LISTS BRVIEW_DAT)
  add_custom_command(TARGET brview POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E copy_if_different "${BRENDER132_SOURCE_DIR}/dat/${f}" "$<TARGET_FILE_DIR:brview>/dat/${f}")
endforeach()
add_custom_command(TARGET brview POST_BUILD
  COMMAND ${CMAKE_COMMAND} -E copy_if_different $<TARGET_FILE:SDL3::SDL3> $<TARGET_FILE_DIR:brview>)

install(TARGETS brview RUNTIME DESTINATION .)
install(FILES $<TARGET_FILE:SDL3::SDL3> DESTINATION .)
foreach(f IN LISTS BRVIEW_DAT)
  install(FILES "${BRENDER132_SOURCE_DIR}/dat/${f}" DESTINATION dat)
endforeach()

# The showcase game's first playable slice.
add_subdirectory("${CMAKE_CURRENT_LIST_DIR}/../games/keepers-hour" keepers-hour)
