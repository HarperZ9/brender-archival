from __future__ import annotations

import json
from pathlib import Path

from engine_revival.brender_asset_sources import (
    asset_audit_source,
    material_audit_source,
    material_file_audit_source,
    pixelmap_roundtrip_source,
)
REPO_ROOT = Path(__file__).resolve().parents[1]
from engine_revival.brender_compat_sources import (
    portable_core_stubs_source,
    startup_smoke_source,
    vector_smoke_source,
)
from engine_revival.brender_render_sources import render_smoke_source
from engine_revival.brender_scene_sources import scene_smoke_source
from engine_revival.brender_fill_sources import fill_smoke_source
from engine_revival.brender_depth_sources import depth_smoke_source
from engine_revival.brender_texture_sources import texture_smoke_source
from engine_revival.brender_model_sources import model_smoke_source
from engine_revival.brender_material_sources import material_smoke_source
from engine_revival.brender_multimodel_sources import multimodel_smoke_source
from engine_revival.brender_gouraud_sources import gouraud_smoke_source
from engine_revival.brender_material_resolve_sources import material_resolve_source
from engine_revival.brender_texture_sample_sources import texture_file_sample_source
from engine_revival.brender_game_shell_sources import game_shell_source
from engine_revival.brender_host_semantic_sources import host_semantic_source
from engine_revival.brender_softrend_sources import softrend_render_source
from engine_revival.brender_plotter_sources import plotter_smoke_source
from engine_revival.brender_host_sources import portable_host_stubs_source
from engine_revival.brender_harness_templates import cmake_project_source, readme_source


CORE_FLOAT_DIRS = ("fw", "host", "std", "pixelmap", "dosio", "v1db", "math", "fmt")
CORE_V1DB_DISABLED_DIRS = ("fw", "host", "std", "pixelmap", "dosio", "math")
CORE_FLOAT_DEFINES = (
    "BASED_FLOAT=1",
    "BASED_FIXED=0",
    "INLINE_FIXED=0",
    "__386__=1",
    "DEBUG=0",
    "PARANOID=0",
    "EVAL=0",
    "STATIC=static",
    "ADD_RCS_ID=0",
)
OUTPUT_FILES = (
    "CMakeLists.txt",
    "README.md",
    "cmake/brender-core-sources.cmake",
    "cmake/brender-softrend.cmake",
    "cmake/brender-pentprim.cmake",
    "compat/brender-softrend-float-fallbacks.c",
    "compat/brender-pentprim-c-port.c",
    "compat/brender-portable-core-stubs.c",
    "compat/brender-portable-host-stubs.c",
    "smoke/brender-core-smoke.c",
    "smoke/brender-core-startup-smoke.c",
    "smoke/brender-core-render-smoke.c",
    "smoke/brender-core-scene-smoke.c",
    "smoke/brender-core-fill-smoke.c",
    "smoke/brender-core-depth-smoke.c",
    "smoke/brender-core-texture-smoke.c",
    "smoke/brender-core-model-smoke.c",
    "smoke/brender-core-material-smoke.c",
    "smoke/brender-core-multimodel-smoke.c",
    "smoke/brender-core-gouraud-smoke.c",
    "smoke/brender-core-plotter-smoke.c",
    "smoke/brender-core-asset-audit.c",
    "smoke/brender-core-material-audit.c",
    "smoke/brender-core-material-file-audit.c",
    "smoke/brender-core-pixelmap-roundtrip.c",
    "smoke/brender-core-material-resolve.c",
    "smoke/brender-core-texture-file-sample.c",
    "smoke/brender-core-game-shell.c",
    "smoke/brender-core-host-semantic.c",
    "smoke/brender-core-softrend-render.c",
    "harness-manifest.json",
)


class HarnessMaterializationError(ValueError):
    pass


def materialize_brender_core_harness(source_root: Path, output_root: Path) -> list[Path]:
    source = source_root.resolve()
    output = output_root.resolve()
    _validate_source_tree(source)
    _validate_output_location(source, output)
    source_lists = _load_core_float_source_lists(source)
    softrend_sources = _load_softrend_source_list(source)
    pentprim_sources = _load_pentprim_source_lists(source)
    files = {
        "CMakeLists.txt": cmake_project_source(CORE_FLOAT_DEFINES),
        "README.md": readme_source(),
        "cmake/brender-core-sources.cmake": _source_manifest_cmake(source_lists),
        "cmake/brender-softrend.cmake": _softrend_cmake(softrend_sources),
        "cmake/brender-pentprim.cmake": _pentprim_cmake(pentprim_sources),
    "compat/brender-pentprim-c-port.c": (REPO_ROOT / ".." / "compat" / "brender-pentprim-c-port.c").resolve().read_text(encoding="utf-8"),
        "compat/brender-portable-core-stubs.c": portable_core_stubs_source(),
        "compat/brender-portable-host-stubs.c": portable_host_stubs_source(),
        "smoke/brender-core-smoke.c": vector_smoke_source(),
        "smoke/brender-core-startup-smoke.c": startup_smoke_source(),
        "smoke/brender-core-render-smoke.c": render_smoke_source(),
        "smoke/brender-core-scene-smoke.c": scene_smoke_source(),
        "smoke/brender-core-fill-smoke.c": fill_smoke_source(),
        "smoke/brender-core-depth-smoke.c": depth_smoke_source(),
        "smoke/brender-core-texture-smoke.c": texture_smoke_source(),
        "smoke/brender-core-model-smoke.c": model_smoke_source(),
        "smoke/brender-core-material-smoke.c": material_smoke_source(),
        "smoke/brender-core-multimodel-smoke.c": multimodel_smoke_source(),
        "smoke/brender-core-gouraud-smoke.c": gouraud_smoke_source(),
        "smoke/brender-core-plotter-smoke.c": plotter_smoke_source(),
    "smoke/brender-core-asset-audit.c": asset_audit_source(),
    "smoke/brender-core-material-audit.c": material_audit_source(),
    "smoke/brender-core-material-file-audit.c": material_file_audit_source(),
    "smoke/brender-core-pixelmap-roundtrip.c": pixelmap_roundtrip_source(),
    "smoke/brender-core-material-resolve.c": material_resolve_source(),
    "smoke/brender-core-texture-file-sample.c": texture_file_sample_source(),
    "smoke/brender-core-game-shell.c": game_shell_source(),
    "smoke/brender-core-host-semantic.c": host_semantic_source(),
    "smoke/brender-core-softrend-render.c": softrend_render_source(),
    "compat/brender-softrend-float-fallbacks.c": (REPO_ROOT / ".." / "compat" / "brender-softrend-float-fallbacks.c").resolve().read_text(encoding="utf-8"),
    "harness-manifest.json": _manifest_json(source_lists),
    }
    written: list[Path] = []
    for relative_name in OUTPUT_FILES:
        path = output / relative_name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(files[relative_name], encoding="utf-8")
        written.append(path)
    return written


def _validate_source_tree(source: Path) -> None:
    required = [source / "inc", source / "core" / "inc"]
    for directory in CORE_FLOAT_DIRS:
        module_dir = source / "core" / directory
        required.extend([module_dir, module_dir / "makefile"])
    missing = [path for path in required if not path.exists()]
    if missing:
        names = ", ".join(str(path) for path in missing)
        raise HarnessMaterializationError(f"BRender source checkout is missing: {names}")


def _validate_output_location(source: Path, output: Path) -> None:
    if output == source or source in output.parents:
        raise HarnessMaterializationError(
            "BRender harness output must be outside the source checkout"
        )


def _load_core_float_source_lists(source: Path) -> dict[str, list[str]]:
    source_lists: dict[str, list[str]] = {}
    for directory in CORE_FLOAT_DIRS:
        module_dir = source / "core" / directory
        makefile = module_dir / "makefile"
        object_names = _parse_objs_c(makefile.read_text(encoding="utf-8"))
        if not object_names:
            raise HarnessMaterializationError(
                f"{makefile} does not define OBJS_C entries"
            )
        filenames = [f"{name}.c" for name in object_names]
        missing = [
            module_dir / filename
            for filename in filenames
            if not (module_dir / filename).exists()
        ]
        if missing:
            names = ", ".join(str(path) for path in missing)
            raise HarnessMaterializationError(
                f"BRender makefile references missing C source: {names}"
            )
        source_lists[directory] = filenames
    return source_lists


def _load_softrend_source_list(source: Path) -> list[str]:
    """Parse the softrend makefile OBJS_C list into checkout-relative .c paths.

    The optional 386 assembly overlays (OBJS_ASM) are deliberately excluded:
    the period makefile treats them as a speed layer over these C objects.
    """
    module_dir = source / "drivers" / "softrend"
    makefile = module_dir / "makefile"
    object_names = _parse_objs_c(makefile.read_text(encoding="utf-8"))
    if not object_names:
        raise HarnessMaterializationError(
            f"{makefile} does not define OBJS_C entries"
        )
    filenames = [f"{name}.c" for name in object_names]
    missing = [
        module_dir / filename
        for filename in filenames
        if not (module_dir / filename).exists()
    ]
    if missing:
        names = ", ".join(str(path) for path in missing)
        raise HarnessMaterializationError(
            f"softrend makefile references missing C source: {names}"
        )
    return filenames



def _load_pentprim_source_lists(source):
    """Parse pentprim makefile OBJS_C + XOBJS_C into checkout-relative .c paths.

    XOBJS_C is the period makefile's own generic-C primitive path; the
    XOBJS_ASM overlays are excluded exactly as with softrend.
    """
    module_dir = source / "drivers" / "pentprim"
    makefile = module_dir / "makefile"
    text = makefile.read_text(encoding="utf-8")
    def parse(block_name):
        names = []
        in_block = False
        for raw_line in text.splitlines():
            line = raw_line.strip()
            if not in_block and not line.startswith(block_name):
                continue
            if not in_block:
                in_block = True
                line = line.split("=", 1)[1] if "=" in line else ""
            if not line or line.startswith("#"):
                if in_block and not raw_line.rstrip().endswith("\\"):
                    break
                continue
            name = _extract_object_name(line)
            if name:
                names.append(name)
            if not raw_line.rstrip().endswith("\\"):
                break
        return names
    filenames = [f"{n}.c" for n in parse("OBJS_C") + parse("XOBJS_C")]
    # The period makefile omitted the alternative-build C implementations
    # (awtmz.c generates every TrapezoidRenderPIZ2T* variant via awtmi.h);
    # include them explicitly.
    filenames += ["awtmz.c"]
    missing = [module_dir / f for f in filenames if not (module_dir / f).exists()]
    if missing:
        raise HarnessMaterializationError(
            "pentprim makefile references missing C source: "
            + ", ".join(str(p) for p in missing)
        )
    return filenames
def _parse_objs_c(text: str) -> list[str]:
    object_names: list[str] = []
    in_block = False
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not in_block and not line.startswith("OBJS_C"):
            continue
        if not in_block:
            in_block = True
            line = line.split("=", 1)[1] if "=" in line else ""
        if not line or line.startswith("#"):
            if in_block and not line.endswith("\\"):
                break
            continue
        object_name = _extract_object_name(line)
        if object_name:
            object_names.append(object_name)
        if not raw_line.rstrip().endswith("\\"):
            break
    return object_names


def _extract_object_name(line: str) -> str | None:
    item = line.split("#", 1)[0].strip().rstrip("\\").strip()
    if not item:
        return None
    stem = item.rsplit("/", 1)[-1].split("$(OBJ_EXT)", 1)[0]
    if "$(" in stem or ")" in stem or not stem:
        return None
    return stem


def _source_manifest_cmake(source_lists: dict[str, list[str]]) -> str:
    lines = [
        "# Explicit source lists generated from the period OBJS_C makefile rules.",
    ]
    aggregate_vars: list[str] = []
    for directory in CORE_FLOAT_DIRS:
        variable = _module_source_var(directory)
        aggregate_vars.append(variable)
        lines.extend([
            "",
            f"set({variable}",
            *_indented(_cmake_source_paths(directory, source_lists[directory])),
            ")",
        ])
    lines.extend(["", "set(BRENDER_CORE_FLOAT_SOURCES"])
    lines.extend(f"  ${{{variable}}}" for variable in aggregate_vars)
    lines.extend([
        ")",
        "",
        "foreach(source_file IN LISTS BRENDER_CORE_FLOAT_SOURCES)",
        "  if(NOT EXISTS \"${source_file}\")",
        "    message(FATAL_ERROR \"Missing BRender core source: ${source_file}\")",
        "  endif()",
        "endforeach()",
        "",
    ])
    return "\n".join(lines)


def _manifest_json(source_lists: dict[str, list[str]]) -> str:
    payload = {
        "id": "brender-v132-portable-core-plan",
        "target_id": "brender",
        "harness_type": "portable-cmake-core-scaffold",
        "cmake_platform": "Win32",
        "core_float_dirs": list(CORE_FLOAT_DIRS),
        "core_v1db_disabled_dirs": list(CORE_V1DB_DISABLED_DIRS),
        "compile_definitions": list(CORE_FLOAT_DEFINES),
        "portable_compat_source": "compat/brender-portable-core-stubs.c",
        "portable_compat_sources": [
            "compat/brender-portable-core-stubs.c",
            "compat/brender-portable-host-stubs.c",
        ],
        "smoke_target": "brender_core_smoke",
        "smoke_targets": [
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
        "brender_core_asset_audit",
        "brender_core_material_audit",
        "brender_core_material_file_audit",
        "brender_core_pixelmap_roundtrip",
        "brender_core_material_resolve",
        "brender_core_texture_file_sample",
        "brender_core_game_shell",
        "brender_core_host_semantic",
        "brender_core_softrend_render",
        ],
        "softrend_lane": {
            "library_target": "brender_softrend_float",
            "source_list_var": "BRENDER_SOFTREND_FLOAT_SOURCES",
            "asm_overlays_excluded": True,
            "entry_point": "BrDrv1SoftRendBegin",
            "note": "softrend OBJS_C only; the seven 386 assembly kernels are the period makefile's optional speed overlay over these C objects",
        },
        "source_lists": source_lists,
        "source_policy": "out-of-tree; explicit period OBJS_C lists; no vendored BRender source",
    }
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def _module_source_var(directory: str) -> str:
    return f"BRENDER_CORE_FLOAT_{directory.upper()}_SOURCES"


def _cmake_source_paths(directory: str, filenames: list[str]) -> list[str]:
    return [
        f'"${{BRENDER_SOURCE_DIR}}/core/{directory}/{filename}"'
        for filename in filenames
    ]


def _indented(items: tuple[str, ...] | list[str]) -> list[str]:
    return [f"  {item}" for item in items]


def _softrend_cmake(sources: list[str]) -> str:
    """CMake for the softrend lane: period OBJS_C only, no assembly overlays."""
    source_paths = [
        f'"${{BRENDER_SOURCE_DIR}}/drivers/softrend/{filename}"'
        for filename in sources
    ]
    lines = [
        "# Softrend driver lane generated from the period OBJS_C makefile rule.",
        "# The seven 386 assembly kernels are excluded: they are the makefile's",
        "# optional speed overlay over these C objects.",
        "",
        "set(BRENDER_SOFTREND_FLOAT_SOURCES",
        *_indented(source_paths),
        ")",
        "",
        "foreach(source_file IN LISTS BRENDER_SOFTREND_FLOAT_SOURCES)",
        "  if(NOT EXISTS \"${source_file}\")",
        "    message(FATAL_ERROR \"Missing softrend source: ${source_file}\")",
        "  endif()",
        "endforeach()",
        "",
        "add_library(brender_softrend_float STATIC ${BRENDER_SOFTREND_FLOAT_SOURCES} \"${CMAKE_CURRENT_LIST_DIR}/../compat/brender-softrend-float-fallbacks.c\")",
        "target_include_directories(brender_softrend_float PRIVATE",
        "  ${BRENDER_SOURCE_DIR}/drivers/softrend",
        "  ${BRENDER_SOURCE_DIR}/inc",
        "  ${BRENDER_SOURCE_DIR}/core/inc",
        "  ${BRENDER_SOURCE_DIR}/ddi_inc)",
        "target_compile_definitions(brender_softrend_float PRIVATE",
        "  BASED_FLOAT=1",
        "  BASED_FIXED=0",
        "  INLINE_FIXED=0",
        "  DEBUG=0",
        "  PARANOID=0",
        "  EVAL=0",
        "  STATIC=static",
        "  ADD_RCS_ID=0",
        "  BrDrv1Begin=BrDrv1SoftRendBegin",
        "  V1Face_CullOneSidedPerspective_P6=V1Face_CullOneSidedPerspective)",
        "target_link_libraries(brender_softrend_float PRIVATE brender_core_float)",
        "",
        "add_executable(brender_core_softrend_render smoke/brender-core-softrend-render.c)",
        "target_include_directories(brender_core_softrend_render PRIVATE",
        "  ${BRENDER_SOURCE_DIR}/inc",
        "  ${BRENDER_SOURCE_DIR}/core/inc",
        "  ${BRENDER_SOURCE_DIR}/ddi_inc)",
        "target_compile_definitions(brender_core_softrend_render PRIVATE",
        "  BASED_FLOAT=1",
        "  BASED_FIXED=0",
        "  INLINE_FIXED=0",
        "  __386__=1",
        "  DEBUG=0",
        "  PARANOID=0",
        "  EVAL=0",
        "  STATIC=static",
        "  ADD_RCS_ID=0)",
        "target_link_libraries(brender_core_softrend_render PRIVATE brender_core_float brender_softrend_float)",
        "add_test(NAME brender_core_softrend_render",
        "  COMMAND brender_core_softrend_render",
        "    \"${BRENDER_SOURCE_DIR}/dat/sph32.dat\"",
        "    \"${BRENDER_SOURCE_DIR}/dat/earth.pix\"",
        "    \"${BRENDER_SOURCE_DIR}/dat/std.pal\"",
        "    brender-core-softrend-render.ppm)",
        "set_tests_properties(brender_core_softrend_render PROPERTIES",
        "  TIMEOUT 120)",
        "# Integration note: awtmz.c now supplies real C kernels for every",
        "# TrapezoidRenderPIZ2T* variant (via awtmi.h), so the rung renders",
        "# through BRender's own primitive library. See readiness evidence.",
        "",
    ]
    return "\n".join(lines)


def _pentprim_cmake(sources: list[str]) -> str:
    """CMake for the pentprim lane: period OBJS_C + XOBJS_C, no asm overlays."""
    source_paths = [
        f'"${{BRENDER_SOURCE_DIR}}/drivers/pentprim/{filename}"'
        for filename in sources
    ]
    lines = [
        "# Pentprim primitive-library lane generated from period OBJS_C + XOBJS_C.",
        "# XOBJS_C is the makefile's own generic-C primitive path; XOBJS_ASM",
        "# overlays (the pentium rasterizer kernels) are excluded.",
        "",
        "set(BRENDER_PENTPRIM_FLOAT_SOURCES",
        *_indented(source_paths),
        "  \"${CMAKE_CURRENT_LIST_DIR}/../compat/brender-pentprim-c-port.c\")",
        "",
        "foreach(source_file IN LISTS BRENDER_PENTPRIM_FLOAT_SOURCES)",
        "  if(NOT EXISTS \"${source_file}\")",
        "    message(FATAL_ERROR \"Missing pentprim source: ${source_file}\")",
        "  endif()",
        "endforeach()",
        "",
        "add_library(brender_pentprim_float STATIC ${BRENDER_PENTPRIM_FLOAT_SOURCES})",
        "target_include_directories(brender_pentprim_float PRIVATE",
        "  ${BRENDER_SOURCE_DIR}/drivers/pentprim",
        "  ${BRENDER_SOURCE_DIR}/inc",
        "  ${BRENDER_SOURCE_DIR}/core/inc",
        "  ${BRENDER_SOURCE_DIR}/ddi_inc)",
        "target_compile_definitions(brender_pentprim_float PRIVATE",
        "  BASED_FLOAT=1",
        "  BASED_FIXED=0",
        "  INLINE_FIXED=0",
        "  DEBUG=0",
        "  PARANOID=0",
        "  EVAL=0",
        "  STATIC=static",
        "  ADD_RCS_ID=0",
        "  PARTS=0x03FF",
        "  BrDrv1Begin=BrDrv1PentPrimBegin)",
        "target_link_libraries(brender_pentprim_float PRIVATE brender_core_float brender_softrend_float)",
        "",
        "target_link_libraries(brender_core_softrend_render PRIVATE brender_pentprim_float)",
        "",
    ]
    return "\n".join(lines)
