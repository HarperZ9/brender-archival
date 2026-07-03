from engine_revival.report import write_reports
from engine_revival.seed import seed_workspace


def test_reproduction_page_resolves_evidence_source_details(tmp_path):
    seed_workspace(tmp_path)
    (tmp_path / "artifacts").mkdir()
    (tmp_path / "artifacts" / "brender-source.json").write_text(
        """{
  "id": "brender-source",
  "target_id": "brender",
  "artifact_type": "source-release",
  "title": "BRender source release",
  "origin": "public repository",
  "redistribution_status": "open",
  "access_level": "public",
  "evidence_quality": "public-source",
  "source_ids": ["initial-research-reports"]
}""",
        encoding="utf-8",
    )
    (tmp_path / "reproductions").mkdir()
    (tmp_path / "reproductions" / "brender-source-build.json").write_text(
        """{
  "id": "brender-source-build",
  "target_id": "brender",
  "reproduction_type": "source-build",
  "status": "planned",
  "environment": ["period compiler or compatibility layer"],
  "steps": ["clone the public source", "record build dependencies"],
  "expected_outputs": ["build log", "sample executable"],
  "artifact_ids": ["brender-source"],
  "public_notes": "Build public BRender source into a repeatable critical-edition recipe.",
  "source_ids": ["initial-research-reports"]
}""",
        encoding="utf-8",
    )
    page = tmp_path / "docs" / "generated" / "reproductions" / "brender-source-build.md"
    assert page in write_reports(tmp_path)
    text = page.read_text(encoding="utf-8")
    assert "| Source | Type | Confidence | Scope | URL |" in text
    assert (
        "| Initial engine revival research reports | local-research-summary | "
        "moderate | initial target selection |  |"
    ) in text
