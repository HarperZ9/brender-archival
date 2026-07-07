import json

import pytest

from engine_revival.brender_harness import (
    HarnessMaterializationError,
    materialize_brender_core_harness,
)
from engine_revival.cli import main


CORE_DIRS = ("fw", "host", "std", "pixelmap", "dosio", "v1db", "math", "fmt")


def _write_source_fixture(root):
    (root / "inc").mkdir(parents=True)
    (root / "inc" / "brender.h").write_text("/* public header fixture */\n", encoding="utf-8")
    (root / "core" / "inc").mkdir(parents=True)
    for name in CORE_DIRS:
        directory = root / "core" / name
        directory.mkdir(parents=True)
        (directory / f"{name}_listed.c").write_text("void fixture(void) {}\n", encoding="utf-8")
        (directory / f"{name}_unlisted.c").write_text("void skip_me(void) {}\n", encoding="utf-8")
        (directory / f"{name}_commented.c").write_text("void skip_comment(void) {}\n", encoding="utf-8")
        (directory / "makefile").write_text(
            "\n".join([
                "OBJS_C=\\",
                f"    $(BLD_DIR)/{name}_listed$(OBJ_EXT)\\",
                f"#   $(BLD_DIR)/{name}_commented$(OBJ_EXT)\\",
                "",
                "OBJS_ASM=\\",
                "",
            ]),
            encoding="utf-8",
        )


def test_materialize_brender_core_harness_writes_out_of_tree_files(tmp_path):
    source = tmp_path / "source"
    output = tmp_path / "harness"
    _write_source_fixture(source)

    written = materialize_brender_core_harness(source, output)

    assert written == [
        output / "CMakeLists.txt",
        output / "README.md",
        output / "cmake" / "brender-core-sources.cmake",
        output / "compat" / "brender-portable-core-stubs.c",
        output / "compat" / "brender-portable-host-stubs.c",
        output / "smoke" / "brender-core-smoke.c",
        output / "smoke" / "brender-core-startup-smoke.c",
        output / "smoke" / "brender-core-render-smoke.c",
        output / "smoke" / "brender-core-scene-smoke.c",
        output / "smoke" / "brender-core-fill-smoke.c",
        output / "smoke" / "brender-core-depth-smoke.c",
        output / "smoke" / "brender-core-texture-smoke.c",
        output / "smoke" / "brender-core-model-smoke.c",
        output / "smoke" / "brender-core-material-smoke.c",
        output / "smoke" / "brender-core-multimodel-smoke.c",
        output / "smoke" / "brender-core-gouraud-smoke.c",
        output / "smoke" / "brender-core-plotter-smoke.c",
        output / "harness-manifest.json",
    ]
    cmake = (output / "CMakeLists.txt").read_text(encoding="utf-8")
    assert "project(brender_v132_portable_core C)" in cmake
    assert "add_library(brender_core_float STATIC" in cmake
    assert "add_executable(brender_core_smoke" in cmake
    assert "add_executable(brender_core_startup_smoke" in cmake
    assert "target_link_libraries(brender_core_smoke PRIVATE brender_core_float)" in cmake
    assert "target_link_libraries(brender_core_startup_smoke PRIVATE brender_core_float)" in cmake
    assert "add_test(NAME brender_core_smoke COMMAND brender_core_smoke)" in cmake
    assert "add_test(NAME brender_core_startup_smoke COMMAND brender_core_startup_smoke)" in cmake
    assert "add_executable(brender_core_render_smoke" in cmake
    assert "target_link_libraries(brender_core_render_smoke PRIVATE brender_core_float)" in cmake
    assert "add_test(NAME brender_core_render_smoke" in cmake
    assert "add_executable(brender_core_scene_smoke" in cmake
    assert "target_link_libraries(brender_core_scene_smoke PRIVATE brender_core_float)" in cmake
    assert "add_test(NAME brender_core_scene_smoke" in cmake
    assert "add_executable(brender_core_fill_smoke" in cmake
    assert "target_link_libraries(brender_core_fill_smoke PRIVATE brender_core_float)" in cmake
    assert "add_test(NAME brender_core_fill_smoke" in cmake
    assert "add_executable(brender_core_depth_smoke" in cmake
    assert "target_link_libraries(brender_core_depth_smoke PRIVATE brender_core_float)" in cmake
    assert "add_test(NAME brender_core_depth_smoke" in cmake
    assert "add_executable(brender_core_texture_smoke" in cmake
    assert "target_link_libraries(brender_core_texture_smoke PRIVATE brender_core_float)" in cmake
    assert "add_test(NAME brender_core_texture_smoke" in cmake
    assert "add_executable(brender_core_model_smoke" in cmake
    assert "target_link_libraries(brender_core_model_smoke PRIVATE brender_core_float)" in cmake
    assert "add_test(NAME brender_core_model_smoke" in cmake
    assert "${BRENDER_SOURCE_DIR}/dat/duck.dat" in cmake
    assert "add_executable(brender_core_material_smoke" in cmake
    assert "add_test(NAME brender_core_material_smoke" in cmake
    assert "${BRENDER_SOURCE_DIR}/dat/sph32.dat" in cmake
    assert "add_executable(brender_core_multimodel_smoke" in cmake
    assert "${BRENDER_SOURCE_DIR}/dat/coupe.dat" in cmake
    assert "add_executable(brender_core_gouraud_smoke" in cmake
    assert "add_executable(brender_core_plotter_smoke" in cmake
    assert "${BRENDER_SOURCE_DIR}/dat/teapot.dat" in cmake
    assert "compat/brender-portable-core-stubs.c" in cmake
    assert "compat/brender-portable-host-stubs.c" in cmake
    assert "CMAKE_SIZEOF_VOID_P" in cmake
    assert "use -A Win32 with Visual Studio" in cmake
    assert "__BR_V1DB__=0" in cmake
    assert "__WIN_32__=1" in cmake
    assert "target_compile_definitions(brender_core_float PRIVATE" in cmake
    for definition in [
        "BASED_FLOAT=1",
        "BASED_FIXED=0",
        "INLINE_FIXED=0",
        "__386__=1",
        "DEBUG=0",
        "PARANOID=0",
        "EVAL=0",
        "STATIC=static",
        "ADD_RCS_ID=0",
    ]:
        assert f"  {definition}" in cmake
    assert "BRENDER_SOURCE_DIR" in cmake
    source_manifest = (output / "cmake" / "brender-core-sources.cmake").read_text(
        encoding="utf-8"
    )
    assert "file(GLOB" not in source_manifest
    assert '"${BRENDER_SOURCE_DIR}/core/fw/fw_listed.c"' in source_manifest
    assert "fw_unlisted.c" not in source_manifest
    assert "fw_commented.c" not in source_manifest
    smoke = (output / "smoke" / "brender-core-smoke.c").read_text(encoding="utf-8")
    assert '#include "brender.h"' in smoke
    assert "#define _NO_VECTOR_MACROS 1" in smoke
    assert "BrVector3SetFloat(&vector, 1.0f, 2.0f, 3.0f)" in smoke
    assert "BrScalarToFloat(vector.v[2])" in smoke
    assert "BrBegin()" not in smoke
    startup_smoke = (output / "smoke" / "brender-core-startup-smoke.c").read_text(
        encoding="utf-8"
    )
    assert "#define __BR_V1DB__ 0" in startup_smoke
    assert "BrBegin()" in startup_smoke
    assert "BrEnd()" in startup_smoke
    render_smoke = (output / "smoke" / "brender-core-render-smoke.c").read_text(
        encoding="utf-8"
    )
    assert "BrPixelmapAllocate(BR_PMT_RGB_888" in render_smoke
    assert "BrMatrix4Perspective(" in render_smoke
    assert "BrMatrix4ApplyP(" in render_smoke
    assert "BrPixelmapLine(" in render_smoke
    assert "BrPixelmapPixelGet(" in render_smoke
    assert 'fprintf(f, "P6\\n%d %d\\n255\\n"' in render_smoke
    scene_smoke = (output / "smoke" / "brender-core-scene-smoke.c").read_text(
        encoding="utf-8"
    )
    assert "BrActorAllocate(BR_ACTOR_CAMERA" in scene_smoke
    assert "BrModelAllocate(" in scene_smoke
    assert "BrModelUpdate(model, BR_MODU_ALL)" in scene_smoke
    assert "BrActorToScreenMatrix4(" in scene_smoke
    assert "BrPixelmapLine(" in scene_smoke
    fill_smoke = (output / "smoke" / "brender-core-fill-smoke.c").read_text(
        encoding="utf-8"
    )
    assert "fill_triangle(" in fill_smoke
    assert "BrActorToScreenMatrix4(" in fill_smoke
    assert "BrMatrix34ApplyP(" in fill_smoke
    depth_smoke = (output / "smoke" / "brender-core-depth-smoke.c").read_text(
        encoding="utf-8"
    )
    assert "fill_triangle_z(" in depth_smoke
    assert "g_zbuf" in depth_smoke
    assert "g_rejections" in depth_smoke
    texture_smoke = (output / "smoke" / "brender-core-texture-smoke.c").read_text(
        encoding="utf-8"
    )
    assert "fill_triangle_tex(" in texture_smoke
    assert "BrPixelmapPixelGet(tex" in texture_smoke
    assert "uow" in texture_smoke and "vow" in texture_smoke
    model_smoke = (output / "smoke" / "brender-core-model-smoke.c").read_text(
        encoding="utf-8"
    )
    assert "BrModelLoad(" in model_smoke
    assert "BrActorToScreenMatrix4(" in model_smoke
    assert "fill_triangle_z(" in model_smoke
    material_smoke = (output / "smoke" / "brender-core-material-smoke.c").read_text(
        encoding="utf-8"
    )
    assert "BrModelLoad(" in material_smoke
    assert "fill_triangle_tex(" in material_smoke
    assert "model->vertices[i].map" in material_smoke
    multimodel_smoke = (output / "smoke" / "brender-core-multimodel-smoke.c").read_text(encoding="utf-8")
    assert "BrModelLoadMany(" in multimodel_smoke
    gouraud_smoke = (output / "smoke" / "brender-core-gouraud-smoke.c").read_text(encoding="utf-8")
    assert "fill_triangle_gouraud(" in gouraud_smoke
    plotter_smoke = (output / "smoke" / "brender-core-plotter-smoke.c").read_text(encoding="utf-8")
    assert "raster_depth(" in plotter_smoke
    assert "<svg xmlns=" in plotter_smoke
    compat = (output / "compat" / "brender-portable-core-stubs.c").read_text(
        encoding="utf-8"
    )
    assert "void BR_RESIDENT_ENTRY _PRO(void)" in compat
    assert "br_uint_16 BR_ASM_CALL _GetSysQual(void)" in compat
    assert "struct br_font BR_ASM_DATA _FontFixed3x5" in compat
    assert "static void copy_source_colour_key0(" in compat
    host_compat = (output / "compat" / "brender-portable-host-stubs.c").read_text(
        encoding="utf-8"
    )
    assert "br_uint_16 _RealSelector = 0;" in host_compat
    assert "br_error BR_RESIDENT_ENTRY HostRealAllocate(" in host_compat
    assert "void BR_ASM_CALL CPUInfo(" in host_compat
    assert "br_error BR_RESIDENT_ENTRY HostInterruptGet(" in host_compat
    assert "void BR_RESIDENT_ENTRY HostFarBlockWrite(" in host_compat
    readme = (output / "README.md").read_text(encoding="utf-8")
    assert "does not vendor BRender source" in readme
    assert "cmake -S . -B build -A Win32" in readme
    assert '"-DBRENDER_SOURCE_DIR=<path-to-public-brender-checkout>"' in readme
    assert "ctest --test-dir build -C Debug --output-on-failure" in readme
    manifest = json.loads((output / "harness-manifest.json").read_text(encoding="utf-8"))
    assert manifest["target_id"] == "brender"
    assert manifest["cmake_platform"] == "Win32"
    assert manifest["core_float_dirs"] == list(CORE_DIRS)
    assert manifest["smoke_target"] == "brender_core_smoke"
    assert manifest["smoke_targets"] == [
        "brender_core_smoke",
        "brender_core_startup_smoke",
        "brender_core_render_smoke",
        "brender_core_scene_smoke",
        "brender_core_fill_smoke",
        "brender_core_depth_smoke",
        "brender_core_texture_smoke",
        "brender_core_model_smoke",
        "brender_core_material_smoke",
        "brender_core_multimodel_smoke",
        "brender_core_gouraud_smoke",
        "brender_core_plotter_smoke",
    ]
    assert manifest["portable_compat_source"] == "compat/brender-portable-core-stubs.c"
    assert manifest["portable_compat_sources"] == [
        "compat/brender-portable-core-stubs.c",
        "compat/brender-portable-host-stubs.c",
    ]
    assert manifest["source_lists"]["fw"] == ["fw_listed.c"]
    assert manifest["compile_definitions"] == [
        "BASED_FLOAT=1",
        "BASED_FIXED=0",
        "INLINE_FIXED=0",
        "__386__=1",
        "DEBUG=0",
        "PARANOID=0",
        "EVAL=0",
        "STATIC=static",
        "ADD_RCS_ID=0",
    ]


def test_materializer_refuses_output_inside_source_checkout(tmp_path):
    source = tmp_path / "source"
    _write_source_fixture(source)

    with pytest.raises(HarnessMaterializationError, match="outside the source checkout"):
        materialize_brender_core_harness(source, source / "generated-harness")


def test_cli_materializes_brender_harness(tmp_path, capsys):
    source = tmp_path / "source"
    output = tmp_path / "harness"
    _write_source_fixture(source)

    exit_code = main([
        "materialize-brender-harness",
        "--source-root",
        str(source),
        "--output-root",
        str(output),
    ])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert str(output / "CMakeLists.txt") in captured.out
    assert (output / "cmake" / "brender-core-sources.cmake").exists()
    assert (output / "smoke" / "brender-core-smoke.c").exists()
    assert (output / "smoke" / "brender-core-startup-smoke.c").exists()
    assert (output / "smoke" / "brender-core-render-smoke.c").exists()
    assert (output / "smoke" / "brender-core-scene-smoke.c").exists()
    assert (output / "smoke" / "brender-core-fill-smoke.c").exists()
