from engine_revival.report import write_reports
from engine_revival.seed import seed_workspace


def test_accession_report_creates_detail_page_with_fixity_and_sources(tmp_path):
    seed_workspace(tmp_path)
    (tmp_path / "artifacts").mkdir()
    (tmp_path / "accessions").mkdir()
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
  "capture_status": "metadata-only",
  "capture_uri": "https://example.invalid/brender",
  "captured_at": "2026-07-03",
  "storage_class": "external-url",
  "fixity_status": "recorded",
  "rights_review": "open-license",
  "hashes": {
    "brender-source.zip": {
      "sha256": "3f786850e387550fdab836ed7e6dc881de23001b"
    }
  },
  "public_notes": "Public source accession metadata.",
  "source_ids": ["initial-research-reports"]
}""",
        encoding="utf-8",
    )
    reports = write_reports(tmp_path)
    index = tmp_path / "docs" / "generated" / "accessions.md"
    page = tmp_path / "docs" / "generated" / "accessions" / "brender-source-planned.md"
    assert index in reports
    assert page in reports
    index_text = index.read_text(encoding="utf-8")
    assert "[brender-source-planned](accessions/brender-source-planned.md)" in index_text
    page_text = page.read_text(encoding="utf-8")
    assert "# brender-source-planned" in page_text
    assert "| Artifact | brender-source |" in page_text
    assert "| Capture URI | https://example.invalid/brender |" in page_text
    assert "| brender-source.zip | sha256 | 3f786850e387550fdab836ed7e6dc881de23001b |" in page_text
    assert "| Source | Type | Confidence | Scope | URL |" in page_text
    assert "Initial engine revival research reports" in page_text
