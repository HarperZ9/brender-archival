from engine_revival.report import write_reports
from engine_revival.seed import seed_workspace


def test_target_dossier_includes_reproductions_and_snapshots(tmp_path):
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
    dossier = tmp_path / "docs" / "generated" / "targets" / "brender.md"
    assert dossier in write_reports(tmp_path)
    text = dossier.read_text(encoding="utf-8")
    assert "## Reproductions" in text
    assert "| brender-source-build | source-build | planned |" in text
    assert "Build public BRender source into a repeatable critical-edition recipe." in text
    assert "## Snapshots" in text
    assert "| brender-source-main | brender-source | refs/heads/main |" in text
    assert "d88d0ed41122664b9781015b517db64353e16f19" in text
