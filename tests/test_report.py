import json

from engine_revival.report import write_reports
from engine_revival.seed import seed_workspace


def test_write_reports_creates_public_index(tmp_path):
    seed_workspace(tmp_path)
    index = tmp_path / "docs" / "generated" / "index.md"
    assert index in write_reports(tmp_path)
    text = index.read_text(encoding="utf-8")
    assert (
        "| Priority | Target | Rights | Revival lane | Artifacts | Accessions | "
        "Tasks | Milestones |"
    ) in text
    assert "- [Attempts](attempts.md)" in text
    assert (
        "| 89 | [Argonaut BRender](targets/brender.md) | open | "
        "critical-edition | 0 | 0 | 1 | 1 |"
    ) in text


def test_write_reports_creates_artifact_summary(tmp_path):
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
  "evidence_quality": "public-source"
}""",
        encoding="utf-8",
    )
    artifacts = tmp_path / "docs" / "generated" / "artifacts.md"
    assert artifacts in write_reports(tmp_path)
    assert "BRender source release" in artifacts.read_text(encoding="utf-8")


def test_write_reports_creates_source_catalog(tmp_path):
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
    sources = tmp_path / "docs" / "generated" / "sources.md"
    assert sources in write_reports(tmp_path)
    text = sources.read_text(encoding="utf-8")
    assert "| Source | Type | Confidence | Uses | Scope | URL |" in text
    assert "Initial engine revival research reports" in text
    assert "| Initial engine revival research reports | local-research-summary | moderate | 45 |" in text
    assert "initial target selection" in text


def test_write_reports_creates_target_dossier(tmp_path):
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
  "capture_status": "planned",
  "storage_class": "external-url",
  "fixity_status": "not-started",
  "rights_review": "open-license",
  "public_notes": "Planned public source accession.",
  "source_ids": ["initial-research-reports"]
}""",
        encoding="utf-8",
    )
    dossier = tmp_path / "docs" / "generated" / "targets" / "brender.md"
    assert dossier in write_reports(tmp_path)
    text = dossier.read_text(encoding="utf-8")
    assert "# Argonaut BRender" in text
    assert "BRender source release" in text
    assert "brender-source-planned" in text
    assert "brender-triage" in text
    assert "brender-baseline" in text
    assert "Initial engine revival research reports" in text


def test_write_reports_creates_accession_summary(tmp_path):
    seed_workspace(tmp_path)
    (tmp_path / "artifacts").mkdir()
    (tmp_path / "accessions").mkdir()
    (tmp_path / "artifacts" / "brender-source.json").write_text(
        """{
  "id": "brender-source",
  "target_id": "brender",
  "artifact_type": "source-release",
  "title": "BRender source",
  "origin": "public",
  "redistribution_status": "open",
  "access_level": "public",
  "evidence_quality": "public-source"
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
  "public_notes": "Planned public source accession."
}""",
        encoding="utf-8",
    )
    accessions = tmp_path / "docs" / "generated" / "accessions.md"
    assert accessions in write_reports(tmp_path)
    assert "brender-source" in accessions.read_text(encoding="utf-8")


def test_write_reports_creates_task_board(tmp_path):
    seed_workspace(tmp_path)
    tasks = tmp_path / "docs" / "generated" / "tasks.md"
    assert tasks in write_reports(tmp_path)
    task_board = tasks.read_text(encoding="utf-8")
    assert "brender-triage" in task_board
    assert "triage-public-record" in task_board


def test_write_reports_creates_packet_pages(tmp_path):
    seed_workspace(tmp_path)
    packet_task = tmp_path / "tasks" / "brender-critical-edition-packet.json"
    packet_task.write_text(
        """{
  "id": "brender-critical-edition-packet",
  "target_id": "brender",
  "task_type": "build-archive-packet",
  "status": "planned",
  "public_notes": "Build the BRender critical-edition packet.",
  "inputs": ["public source branches", "BRender accessions"],
  "outputs": ["standalone archival packet", "version graph"],
  "blocked_by": ["brender-triage"],
  "source_ids": ["initial-research-reports"]
}""",
        encoding="utf-8",
    )
    reports = write_reports(tmp_path)
    packet_index = tmp_path / "docs" / "generated" / "packets.md"
    packet_page = tmp_path / "docs" / "generated" / "packets" / "brender-critical-edition-packet.md"
    assert packet_index in reports
    assert packet_page in reports
    index_text = packet_index.read_text(encoding="utf-8")
    assert "| brender | [brender-critical-edition-packet](packets/brender-critical-edition-packet.md) | planned |" in index_text
    page_text = packet_page.read_text(encoding="utf-8")
    assert "# brender-critical-edition-packet" in page_text
    assert "Build the BRender critical-edition packet." in page_text
    assert "- public source branches" in page_text
    assert "- standalone archival packet" in page_text
    assert "| Source | Type | Confidence | Scope | URL |" in page_text
    assert "Initial engine revival research reports" in page_text


def test_write_reports_creates_corpus_database_export(tmp_path):
    seed_workspace(tmp_path)
    database = tmp_path / "docs" / "generated" / "database.json"
    assert database in write_reports(tmp_path)
    payload = json.loads(database.read_text(encoding="utf-8"))
    assert payload["schema"] == "engine-revival-corpus-v1"
    assert payload["counts"]["targets"] == 22
    assert payload["counts"]["tasks"] == 22
    assert payload["targets"][0]["id"]
    assert payload["targets_by_id"]["brender"]["name"] == "Argonaut BRender"
    assert payload["tasks_by_target"]["brender"][0]["id"] == "brender-triage"
    assert payload["reproductions_by_target"] == {}
    assert payload["sources_by_id"]["initial-research-reports"]["confidence"] == "moderate"


def test_write_reports_creates_reproduction_pages(tmp_path):
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
    reports = write_reports(tmp_path)
    index = tmp_path / "docs" / "generated" / "reproductions.md"
    page = tmp_path / "docs" / "generated" / "reproductions" / "brender-source-build.md"
    assert index in reports
    assert page in reports
    assert "| brender | [brender-source-build](reproductions/brender-source-build.md) | source-build | planned |" in index.read_text(encoding="utf-8")
    page_text = page.read_text(encoding="utf-8")
    assert "# brender-source-build" in page_text
    assert "- period compiler or compatibility layer" in page_text
    assert "- clone the public source" in page_text
    assert "- sample executable" in page_text


def test_write_reports_creates_milestone_summary(tmp_path):
    seed_workspace(tmp_path)
    milestones = tmp_path / "docs" / "generated" / "milestones.md"
    assert milestones in write_reports(tmp_path)
    milestone_board = milestones.read_text(encoding="utf-8")
    assert "| Target | Milestone | Type | Status | Evidence |" in milestone_board
    assert "brender-baseline" in milestone_board
    assert "baseline-public-record" in milestone_board


def test_write_reports_creates_coverage_summary(tmp_path):
    seed_workspace(tmp_path)
    (tmp_path / "artifacts").mkdir()
    (tmp_path / "accessions").mkdir()
    (tmp_path / "artifacts" / "brender-source.json").write_text(
        """{
  "id": "brender-source",
  "target_id": "brender",
  "artifact_type": "source-release",
  "title": "BRender source",
  "origin": "public",
  "redistribution_status": "open",
  "access_level": "public",
  "evidence_quality": "public-source"
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
  "public_notes": "Planned public source accession."
}""",
        encoding="utf-8",
    )
    coverage = tmp_path / "docs" / "generated" / "coverage.md"
    assert coverage in write_reports(tmp_path)
    text = coverage.read_text(encoding="utf-8")
    assert "| Artifact accession coverage | 1 | 1 |" in text
    assert "No missing artifact accessions." in text


def test_write_reports_creates_source_usage_coverage(tmp_path):
    seed_workspace(tmp_path)
    coverage = tmp_path / "docs" / "generated" / "coverage.md"
    assert coverage in write_reports(tmp_path)
    text = coverage.read_text(encoding="utf-8")
    assert "| Source usage coverage | 1 | 1 |" in text
    assert "## Unused Sources" in text
    assert "No unused sources." in text


def test_write_reports_creates_target_task_coverage(tmp_path):
    seed_workspace(tmp_path)
    (tmp_path / "tasks" / "brender-triage.json").unlink()
    coverage = tmp_path / "docs" / "generated" / "coverage.md"
    assert coverage in write_reports(tmp_path)
    text = coverage.read_text(encoding="utf-8")
    assert "| Target task coverage | 21 | 22 |" in text
    assert "## Missing Target Tasks" in text
    assert "- `brender`" in text


def test_write_reports_creates_target_milestone_coverage(tmp_path):
    seed_workspace(tmp_path)
    (tmp_path / "milestones" / "brender-baseline.json").unlink()
    coverage = tmp_path / "docs" / "generated" / "coverage.md"
    assert coverage in write_reports(tmp_path)
    text = coverage.read_text(encoding="utf-8")
    assert "| Target milestone coverage | 21 | 22 |" in text
    assert "## Missing Target Milestones" in text
    assert "- `brender`" in text
