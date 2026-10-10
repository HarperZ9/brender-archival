# The Keeper's Hour, built by modern/CMakeLists.txt beside brview.
# Code: MIT. Words and art in data/: CC BY 4.0.
add_executable(keepers-hour
  src/kh_main.c src/kh_script.c src/kh_script.h src/kh_talk.c src/kh_talk.h src/kh_world.c src/kh_world.h)
target_link_libraries(keepers-hour PRIVATE brdemo)
if(MSVC)
  target_compile_definitions(keepers-hour PRIVATE _CRT_SECURE_NO_WARNINGS)
endif()
add_custom_command(TARGET keepers-hour POST_BUILD
  COMMAND ${CMAKE_COMMAND} -E copy_if_different "${CMAKE_CURRENT_SOURCE_DIR}/data/night.txt" "$<TARGET_FILE_DIR:keepers-hour>/data/night.txt"
  COMMAND ${CMAKE_COMMAND} -E copy_if_different $<TARGET_FILE:SDL3::SDL3> $<TARGET_FILE_DIR:keepers-hour>)
