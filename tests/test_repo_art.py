"""The drawings in the README, held against the corpus and the code.

The art gate settles whether a drawing fits its columns and matches the spec it
was rendered from. Both sides of that check read the same JSON, so it cannot
settle whether a drawing is TRUE. That is the job of this file: every count the
three drawings put on the page is asserted here against the records or the
module that produces it, so a claim that stops holding fails the suite rather
than staying on the page.

One number here is self-referential. The card says how many test functions this
suite carries, and that count includes the functions below, so the assertion
reads the same directory the claim describes.
"""

from __future__ import annotations

import ast
import json
import sys
from collections import Counter
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import check_repo_art as GATE  # noqa: E402

SPEC = json.loads((ROOT / "docs" / "art" / "brender-archival.art.json")
                  .read_text(encoding="utf-8"))
CARD = {field["key"]: field for field in SPEC["cards"][0]["fields"]}
LADDER = next(f for f in SPEC["flows"] if f["file"] == "ladder-lane.svg")


@pytest.fixture(scope="module")
def records():
    from engine_revival.records import RECORD_DIRS, load_records

    return {kind: load_records(ROOT, kind) for kind in RECORD_DIRS}


def test_the_art_gate_passes_every_check():
    """The gate runs under pytest too, so the front page is covered by CI."""
    result = GATE.receipt()
    failed = [check for check in result["checks"] if not check["passed"]]
    assert failed == []
    assert result["passed"] is True


def test_the_corpus_holds_twelve_record_kinds():
    from engine_revival.records import RECORD_DIRS

    assert CARD["record kinds"]["value"] == "twelve of them"
    assert len(RECORD_DIRS) == 12
    named = CARD["record kinds"]["note"].split(":", 1)[1].rstrip(".")
    assert [word.strip() for word in named.split(",")] == list(RECORD_DIRS)


def test_three_hundred_and_forty_two_records_sit_on_disk(records):
    assert CARD["records on disk"]["value"] == "342 files"
    counts = {kind: len(found) for kind, found in records.items()}
    assert sum(counts.values()) == 342
    assert counts["source"] == 78
    assert counts["artifact"] == 60
    assert counts["accession"] == 60
    assert counts["task"] == 31
    assert max(counts, key=counts.get) == "source"


def test_twenty_three_engines_are_tracked_across_fifteen_categories(records):
    assert CARD["engines tracked"]["value"] == "23 targets"
    targets = records["target"]
    assert len(targets) == 23
    assert len({target.payload["category"] for target in targets}) == 15
    status = Counter(target.payload["public_status"] for target in targets)
    assert status["curated-public-sources"] == 8
    assert status["curated-public-metadata"] == 15


def test_seventy_eight_sources_carry_a_confidence_rating(records):
    assert CARD["sources cited"]["value"] == "78 of them"
    confidence = Counter(source.payload["confidence"] for source in records["source"])
    assert confidence["high"] == 62
    assert confidence["moderate"] == 16
    assert sum(confidence.values()) == 78
    assert all(artifact.payload["source_ids"] for artifact in records["artifact"])


def test_five_restricted_artifacts_and_none_of_them_publishable(records):
    """The one marked row: a wrong value here would publish restricted material."""
    from engine_revival.audit import PUBLISHABLE_LEVELS

    assert CARD["restricted holds"]["tone"] == "drift"
    assert CARD["restricted holds"]["value"] == "five artifacts"
    held = [artifact for artifact in records["artifact"]
            if artifact.payload["redistribution_status"] == "do-not-redistribute"]
    assert len(held) == 5
    access = Counter(artifact.payload["access_level"] for artifact in held)
    assert access == {"metadata-only": 4, "public-reference": 1}
    assert not [a for a in held if a.payload["access_level"] in PUBLISHABLE_LEVELS]


def test_the_accessions_for_those_five_record_no_holding(records):
    held = {artifact.payload["id"] for artifact in records["artifact"]
            if artifact.payload["redistribution_status"] == "do-not-redistribute"}
    matching = [accession for accession in records["accession"]
                if accession.payload["artifact_id"] in held]
    assert len(matching) == 5
    assert {a.payload["storage_class"] for a in matching} == {"not-held"}
    assert {a.payload["rights_review"] for a in matching} == {"do-not-redistribute"}


def test_the_audit_and_the_validator_return_no_messages():
    from engine_revival.audit import audit_public_workspace
    from engine_revival.validate import validate_workspace

    assert CARD["audit messages"]["value"] == "none"
    assert audit_public_workspace(ROOT) == []
    assert validate_workspace(ROOT) == []


def test_one_schema_file_per_record_kind():
    from engine_revival.records import RECORD_DIRS
    from engine_revival.schema import load_schema

    assert CARD["schemas"]["value"] == "twelve files"
    files = sorted((ROOT / "schemas").glob("*.schema.json"))
    assert len(files) == 12
    for kind in RECORD_DIRS:
        assert load_schema(ROOT, kind).required


def test_the_report_writes_two_hundred_and_fourteen_files(tmp_path):
    """Written into a copy, so the assertion never rewrites the real tree."""
    import shutil

    from engine_revival.records import RECORD_DIRS
    from engine_revival.report import write_reports

    for directory in RECORD_DIRS.values():
        shutil.copytree(ROOT / directory, tmp_path / directory)
    written = list(write_reports(tmp_path))
    assert CARD["generated pages"]["value"] == "214 written"
    assert len(written) == 214
    assert len([path for path in written if path.suffix == ".md"]) == 213
    assert len([path for path in written if path.suffix == ".json"]) == 1


def test_the_report_leaves_the_committed_pages_byte_identical(tmp_path):
    import shutil

    from engine_revival.records import RECORD_DIRS
    from engine_revival.report import write_reports

    for directory in RECORD_DIRS.values():
        shutil.copytree(ROOT / directory, tmp_path / directory)
    for path in write_reports(tmp_path):
        committed = ROOT / path.relative_to(tmp_path)
        assert committed.read_bytes() == path.read_bytes(), committed


def test_the_ladder_runs_twenty_one_targets_under_ctest():
    from engine_revival import brender_harness as harness
    from engine_revival import brender_harness_templates as templates

    assert CARD["ladder targets"]["value"] == "21 under CTest"
    project = templates.cmake_project_source(harness.CORE_FLOAT_DEFINES)
    in_project = project.count("add_test(NAME")
    module = Path(harness.__file__).read_text(encoding="utf-8")
    assert in_project == 20
    assert module.count("add_test(NAME") == 1
    assert in_project + 1 == 21


def test_the_transcript_reports_twenty_one_passed_and_none_failed():
    log = (ROOT / "builds" / "brender-v132-ctest-twentyone-targets.log").read_bytes()
    text = log.decode("utf-16", errors="ignore")
    assert "100% tests passed, 0 tests failed out of 21" in text
    assert "21/21 Test #21" in text


def test_the_materializer_generates_thirty_one_files():
    from engine_revival.brender_harness import OUTPUT_FILES

    assert CARD["harness files"]["value"] == "31 generated"
    assert len(OUTPUT_FILES) == 31
    assert len(set(OUTPUT_FILES)) == 31
    assert "CMakeLists.txt" in OUTPUT_FILES


def test_the_float_core_is_eight_directories_under_nine_defines():
    from engine_revival.brender_harness import CORE_FLOAT_DEFINES, CORE_FLOAT_DIRS

    assert CARD["build settings"]["value"] == "eight dirs"
    assert CORE_FLOAT_DIRS == ("fw", "host", "std", "pixelmap", "dosio",
                               "v1db", "math", "fmt")
    assert len(CORE_FLOAT_DEFINES) == 9
    assert CORE_FLOAT_DEFINES[0] == "BASED_FLOAT=1"
    stages = {stage["title"]: stage["note"] for stage in LADDER["stages"]}
    assert stages["Build"] == "Eight upstream directories, nine defines."


def test_the_suite_carries_the_number_of_tests_the_card_claims():
    """Self-referential on purpose: the count includes the functions here."""
    found = 0
    for path in sorted((ROOT / "tests").glob("test_*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        found += len([node for node in ast.walk(tree)
                      if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
                      and node.name.startswith("test_")])
    assert CARD["python tests"]["value"] == f"{found} passing"
