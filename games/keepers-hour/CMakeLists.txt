# The Keeper's Hour, built by modern/CMakeLists.txt beside brview.
# Code: MIT. Words and art in data/: CC BY 4.0.
add_executable(keepers-hour WIN32
  src/kh_main.c src/kh_script.c src/kh_script.h src/kh_talk.c src/kh_talk.h src/kh_world.c src/kh_world.h
  src/kh_shapes.c src/kh_shapes.h src/kh_rooms.c src/kh_rooms.h
  src/kh_save.c src/kh_save.h src/kh_boot.c src/kh_boot.h src/kh_tex.c src/kh_tex.h
  src/kh_audio.c src/kh_audio.h src/kh_options.c src/kh_options.h src/kh_input.c src/kh_game.h
  src/kh_capture.c src/kh_capture.h)
target_link_libraries(keepers-hour PRIVATE brdemo)
if(MSVC)
  target_compile_definitions(keepers-hour PRIVATE _CRT_SECURE_NO_WARNINGS)
endif()
add_custom_command(TARGET keepers-hour POST_BUILD
  COMMAND ${CMAKE_COMMAND} -E copy_if_different "${CMAKE_CURRENT_SOURCE_DIR}/data/night.txt" "$<TARGET_FILE_DIR:keepers-hour>/data/night.txt"
  COMMAND ${CMAKE_COMMAND} -E copy_directory "${CMAKE_CURRENT_SOURCE_DIR}/data/art" "$<TARGET_FILE_DIR:keepers-hour>/data/art"
  COMMAND ${CMAKE_COMMAND} -E copy_if_different $<TARGET_FILE:SDL3::SDL3> $<TARGET_FILE_DIR:keepers-hour>)

# The packaged game: the program, SDL3, the script, and nothing else.
install(TARGETS keepers-hour RUNTIME DESTINATION keepers-hour COMPONENT keepers)
install(FILES $<TARGET_FILE:SDL3::SDL3> DESTINATION keepers-hour COMPONENT keepers)
install(FILES "${CMAKE_CURRENT_SOURCE_DIR}/data/night.txt" DESTINATION keepers-hour/data COMPONENT keepers)
install(DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}/data/art" DESTINATION keepers-hour/data COMPONENT keepers)
