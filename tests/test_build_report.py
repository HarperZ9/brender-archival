import json

from engine_revival.report import write_reports
from engine_revival.seed import seed_workspace


def _write_build(root):
    (root / "builds").mkdir()
    (root / "builds" / "brender-v132-build-environment.json").write_text(
        """{
  "id": "brender-v132-build-environment",
  "target_id": "brender",
  "reproduction_id": "brender-critical-edition-source-build",
  "status": "source-inspected",
  "host_platform": "Windows local probe",
  "source_checkout": "out-of-tree public checkout",
  "snapshot_ids": ["brender-v132-main-head"],
  "toolchain_probe": {
    "available": ["cmake"],
    "missing": ["make", "nmake", "cl", "gcc"]
  },
  "build_system": "period makefiles with BR_* environment imports",
  "required_variables": ["BR_SOURCE_DIR", "BR_MAKEFILE", "BR_TARGET_DIR", "BR_MAKE_DIR"],
  "observed_layout": {
    "c_files": 332,
    "headers": 350,
    "makefiles": 68
  },
  "make_rule_map": {
    "root_imports": ["BR_SOURCE_DIR", "BR_MAKEFILE", "BR_TARGET_DIR", "BR_MAKE_DIR"],
    "root_active_subdirs": ["core", "drivers"],
    "root_disabled_subdirs": ["tools", "samples"],
    "core_variants": ["BR_BASE_TYPE=FLOAT", "BR_BASE_TYPE=FIXED"],
    "drivers_target_types": ["DRIVER"]
  },
  "blockers": ["period make environment needs reconstruction"],
  "next_actions": ["port or emulate the period make rules"],
  "public_notes": "BRender source checkout inspected, but no build output claimed.",
  "source_ids": ["foone-brender-v132"]
}""",
        encoding="utf-8",
    )


def test_build_report_creates_index_detail_page_and_database_entries(tmp_path):
    seed_workspace(tmp_path)
    _write_build(tmp_path)
    index = tmp_path / "docs" / "generated" / "builds.md"
    page = tmp_path / "docs" / "generated" / "builds" / "brender-v132-build-environment.md"
    database = tmp_path / "docs" / "generated" / "database.json"

    reports = write_reports(tmp_path)

    assert index in reports
    assert page in reports
    index_text = index.read_text(encoding="utf-8")
    assert "| Target | Build | Status | Reproduction | Snapshots | Host | Build System |" in index_text
    assert (
        "| brender | [brender-v132-build-environment](builds/brender-v132-build-environment.md) | "
        "source-inspected | brender-critical-edition-source-build | brender-v132-main-head | "
        "Windows local probe | period makefiles with BR_* environment imports |"
    ) in index_text
    page_text = page.read_text(encoding="utf-8")
    assert "# brender-v132-build-environment" in page_text
    assert "| Status | source-inspected |" in page_text
    assert "- BR_SOURCE_DIR" in page_text
    assert "| available | cmake |" in page_text
    assert "| missing | make; nmake; cl; gcc |" in page_text
    assert "| c_files | 332 |" in page_text
    assert "## Make Rule Map" in page_text
    assert "| root_active_subdirs | core; drivers |" in page_text
    assert "| root_disabled_subdirs | tools; samples |" in page_text
    assert "| core_variants | BR_BASE_TYPE=FLOAT; BR_BASE_TYPE=FIXED |" in page_text
    assert "| drivers_target_types | DRIVER |" in page_text
    payload = json.loads(database.read_text(encoding="utf-8"))
    assert payload["counts"]["builds"] == 1
    assert payload["builds_by_target"]["brender"][0]["id"] == "brender-v132-build-environment"


def test_target_dossier_includes_build_environment_section(tmp_path):
    seed_workspace(tmp_path)
    _write_build(tmp_path)
    dossier = tmp_path / "docs" / "generated" / "targets" / "brender.md"

    assert dossier in write_reports(tmp_path)

    text = dossier.read_text(encoding="utf-8")
    assert "## Build Environments" in text
    assert "| brender-v132-build-environment | source-inspected | Windows local probe |" in text
