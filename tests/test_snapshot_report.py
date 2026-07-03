from engine_revival.report import write_reports
from engine_revival.seed import seed_workspace


def test_write_reports_creates_snapshot_pages(tmp_path):
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
    (tmp_path / "snapshots").mkdir()
    (tmp_path / "snapshots" / "brender-source-main.json").write_text(
        """{
  "id": "brender-source-main",
  "artifact_id": "brender-source",
  "snapshot_type": "git-remote-head",
  "source_url": "https://github.com/example/brender.git",
  "ref": "refs/heads/main",
  "commit": "d88d0ed41122664b9781015b517db64353e16f19",
  "retrieved_at": "2026-07-03",
  "capture_command": "git ls-remote --symref https://github.com/example/brender.git HEAD refs/heads/*",
  "public_notes": "Exact upstream source snapshot.",
  "source_ids": ["initial-research-reports"]
}""",
        encoding="utf-8",
    )
    reports = write_reports(tmp_path)
    index = tmp_path / "docs" / "generated" / "snapshots.md"
    page = tmp_path / "docs" / "generated" / "snapshots" / "brender-source-main.md"
    assert index in reports
    assert page in reports
    assert (
        "| brender-source | [brender-source-main](snapshots/brender-source-main.md) | "
        "git-remote-head |"
    ) in index.read_text(encoding="utf-8")
    page_text = page.read_text(encoding="utf-8")
    assert "# brender-source-main" in page_text
    assert "d88d0ed41122664b9781015b517db64353e16f19" in page_text
    assert "git ls-remote --symref" in page_text
    assert "| Source | Type | Confidence | Scope | URL |" in page_text
    assert (
        "| Initial engine revival research reports | local-research-summary | "
        "moderate | initial target selection |  |"
    ) in page_text
