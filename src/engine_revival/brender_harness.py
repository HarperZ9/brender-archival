from __future__ import annotations

import json
from pathlib import Path

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
    files = {
        "CMakeLists.txt": cmake_project_source(CORE_FLOAT_DEFINES),
        "README.md": readme_source(),
        "cmake/brender-core-sources.cmake": _source_manifest_cmake(source_lists),
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
        ],
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
