from engine_revival.report import write_reports
from engine_revival.seed import seed_workspace


def test_artifact_report_links_related_records_and_sources(tmp_path):
    seed_workspace(tmp_path)
    (tmp_path / "artifacts").mkdir()
    (tmp_path / "accessions").mkdir()
    (tmp_path / "snapshots").mkdir()
    (tmp_path / "reproductions").mkdir()
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
    (tmp_path / "accessions" / "brender-source-planned.json").write_text(
        """{
  "id": "brender-source-planned",
  "artifact_id": "brender-source",
  "package_type": "source-snapshot",
  "capture_status": "planned",
  "storage_class": "external-url",
  "fixity_status": "not-started",
  "rights_review": "open-license",
  "public_notes": "Planned public source accession.",
  "source_ids": ["initial-research-reports"]
}""",
        encoding="utf-8",
    )
    (tmp_path / "snapshots" / "brender-source-main.json").write_text(
        """{
  "id": "brender-source-main",
  "artifact_id": "brender-source",
  "snapshot_type": "git-remote-head",
  "source_url": "https://github.com/example/brender.git",
  "ref": "refs/heads/main",
  "commit": "d88d0ed41122664b9781015b517db64353e16f19",
  "retrieved_at": "2026-07-03",
  "capture_command": "git ls-remote --symref https://github.com/example/brender.git HEAD",
  "public_notes": "Exact upstream source snapshot.",
  "source_ids": ["initial-research-reports"]
}""",
        encoding="utf-8",
    )
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
  "public_notes": "Build public BRender source into a repeatable recipe.",
  "source_ids": ["initial-research-reports"]
}""",
        encoding="utf-8",
    )

    reports = write_reports(tmp_path)

    index = tmp_path / "docs" / "generated" / "artifacts.md"
    page = tmp_path / "docs" / "generated" / "artifacts" / "brender-source.md"
    assert index in reports
    assert page in reports
    assert "[brender-source](artifacts/brender-source.md)" in index.read_text(
        encoding="utf-8",
    )
    page_text = page.read_text(encoding="utf-8")
    assert "# brender-source" in page_text
    assert "| Target | brender |" in page_text
    assert "| Title | BRender source release |" in page_text
    assert "## Accessions" in page_text
    assert "[brender-source-planned](../accessions/brender-source-planned.md)" in page_text
    assert "## Snapshots" in page_text
    assert "[brender-source-main](../snapshots/brender-source-main.md)" in page_text
    assert "## Reproductions" in page_text
    assert "[brender-source-build](../reproductions/brender-source-build.md)" in page_text
    assert "| Source | Type | Confidence | Scope | URL |" in page_text
    assert "Initial engine revival research reports" in page_text
