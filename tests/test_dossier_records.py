import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _json_records(directory):
    return [
        json.loads(path.read_text(encoding="utf-8"))
        for path in sorted((ROOT / directory).glob("*.json"))
    ]


def test_first_dossier_artifacts_are_recorded():
    expected = {
        "artifacts/brender-v132-source.json",
        "artifacts/brender-3dmm-source.json",
        "artifacts/renderware-ps2-gold-release-notes.json",
        "artifacts/renderware-sdk-310-ps2-archive-item.json",
        "artifacts/net-yaroze-documentation-set.json",
        "artifacts/ps1-psnoobsdk-open-source-sdk.json",
        "artifacts/ps1-runtime-library-33-redump-entry.json",
        "artifacts/ps1-sdevtc-development-environment-manual.json",
        "artifacts/ps2-linux-pal-installation-discs-archive-item.json",
        "artifacts/ps2-linux-release-10-official.json",
        "artifacts/ps2-ps2sdk-open-source-sdk.json",
        "artifacts/ps2-sn-systems-prodg-lineage.json",
        "artifacts/gool-andy-gavin-developer-article.json",
        "artifacts/opengoal-jak-project-source.json",
        "artifacts/opengoal-project-overview-docs.json",
        "artifacts/tri-ace-pbr-implementation-course-notes.json",
        "artifacts/tri-ace-ps2-sh-lighting-hdr-gdc2005.json",
        "artifacts/aqsis-renderer-source.json",
        "artifacts/aqsis-renderer-tooling-metadata.json",
        "artifacts/pixie-renderer-source-mirror.json",
        "artifacts/pixie-sourceforge-project-record.json",
        "artifacts/renderman-interface-spec-31-public-pdf.json",
        "artifacts/direct3d-directx2-release-record.json",
        "artifacts/directx-sdk-legacy-samples-archive.json",
        "artifacts/opengl-performer-getting-started-guide-30.json",
        "artifacts/opengl-performer-product-brochure.json",
        "artifacts/opengl-performer-programmers-guide-32.json",
        "artifacts/quesa-16d13-release-report.json",
        "artifacts/quesa-source-reimplementation.json",
        "artifacts/quickdraw-3d-documentation-qa.json",
        "artifacts/quickdraw-3d-manual-154-public-pdf.json",
        "artifacts/reality-lab-release-2-public-report.json",
        "artifacts/reality-lab-rendermorphics-acquisition-record.json",
        "artifacts/coin3d-open-inventor-api-compatibility.json",
        "artifacts/crystal-space-github-source-repository.json",
        "artifacts/crystal-space-sourceforge-project-record.json",
        "artifacts/mesa-license-and-api-summary.json",
        "artifacts/mesa-source-repository.json",
        "artifacts/ogre-licensing-record.json",
        "artifacts/ogre-source-repository.json",
        "artifacts/open-inventor-readme-first-build-notes.json",
        "artifacts/open-inventor-source-release.json",
        "artifacts/alias-autodesk-acquisition-record.json",
        "artifacts/iris-gl-opengl-history-record.json",
        "artifacts/japan-studio-restructure-public-report.json",
        "artifacts/opengl-registry-spec-anchor.json",
        "artifacts/openphigs-source-reimplementation.json",
        "artifacts/phigs-standard-public-metadata.json",
        "artifacts/psygnosis-studio-liverpool-closure-report.json",
        "artifacts/psygnosis-studio-liverpool-public-history.json",
        "artifacts/phigs-nist-validation-tests.json",
        "artifacts/softimage-autodesk-acquisition-record.json",
        "artifacts/softimage-last-release-transition-faq.json",
        "artifacts/softimage-microsoft-acquisition-record.json",
        "artifacts/team-ico-playstation-official-pages.json",
        "artifacts/team-ico-ueda-playstation-blog-interview.json",
    }
    missing = [path for path in expected if not (ROOT / path).exists()]
    assert missing == []


def test_first_accession_batch_is_recorded():
    expected = {
        "accessions/aqsis-renderer-source-planned.json",
        "accessions/brender-3dmm-source-planned.json",
        "accessions/brender-v132-source-planned.json",
        "accessions/crystal-space-github-source-repository-planned.json",
        "accessions/mesa-source-repository-planned.json",
        "accessions/ogre-source-repository-planned.json",
        "accessions/open-inventor-source-release-planned.json",
        "accessions/openphigs-source-reimplementation-planned.json",
        "accessions/pixie-renderer-source-mirror-planned.json",
        "accessions/quesa-source-reimplementation-planned.json",
    }
    missing = [path for path in expected if not (ROOT / path).exists()]
    assert missing == []


def test_rights_constrained_accession_batch_is_recorded():
    expected = {
        "accessions/net-yaroze-documentation-set-public-reference.json",
        "accessions/ps1-runtime-library-33-redump-entry-metadata-only.json",
        "accessions/ps1-sdevtc-development-environment-manual-public-reference.json",
        "accessions/ps2-linux-pal-installation-discs-archive-item-metadata-only.json",
        "accessions/ps2-linux-release-10-official-public-reference.json",
        "accessions/ps2-sn-systems-prodg-lineage-public-reference.json",
        "accessions/renderware-ps2-gold-release-notes-public-reference.json",
        "accessions/renderware-sdk-310-ps2-archive-item-metadata-only.json",
    }
    missing = [path for path in expected if not (ROOT / path).exists()]
    assert missing == []


def test_open_project_accession_batch_is_recorded():
    expected = {
        "accessions/aqsis-renderer-tooling-metadata-public-reference.json",
        "accessions/crystal-space-sourceforge-project-record-public-reference.json",
        "accessions/directx-sdk-legacy-samples-archive-planned.json",
        "accessions/mesa-license-and-api-summary-public-reference.json",
        "accessions/ogre-licensing-record-public-reference.json",
        "accessions/opengoal-jak-project-source-planned.json",
        "accessions/open-inventor-readme-first-build-notes-public-reference.json",
        "accessions/pixie-sourceforge-project-record-public-reference.json",
        "accessions/ps1-psnoobsdk-open-source-sdk-planned.json",
        "accessions/ps2-ps2sdk-open-source-sdk-planned.json",
    }
    missing = [path for path in expected if not (ROOT / path).exists()]
    assert missing == []


def test_lineage_history_accession_batch_is_recorded():
    expected = {
        "accessions/alias-autodesk-acquisition-record-public-reference.json",
        "accessions/coin3d-open-inventor-api-compatibility-public-reference.json",
        "accessions/direct3d-directx2-release-record-public-reference.json",
        "accessions/iris-gl-opengl-history-record-public-reference.json",
        "accessions/opengl-registry-spec-anchor-public-reference.json",
        "accessions/reality-lab-release-2-public-report-public-reference.json",
        "accessions/reality-lab-rendermorphics-acquisition-record-public-reference.json",
        "accessions/softimage-autodesk-acquisition-record-public-reference.json",
        "accessions/softimage-last-release-transition-faq-public-reference.json",
        "accessions/softimage-microsoft-acquisition-record-public-reference.json",
    }
    missing = [path for path in expected if not (ROOT / path).exists()]
    assert missing == []


def test_documentation_spec_accession_batch_is_recorded():
    expected = {
        "accessions/brender-preservation-index-public-reference.json",
        "accessions/gool-andy-gavin-developer-article-public-reference.json",
        "accessions/opengl-performer-getting-started-guide-30-public-reference.json",
        "accessions/opengl-performer-programmers-guide-32-public-reference.json",
        "accessions/opengoal-project-overview-docs-public-reference.json",
        "accessions/phigs-nist-validation-tests-public-reference.json",
        "accessions/phigs-standard-public-metadata-public-reference.json",
        "accessions/quickdraw-3d-documentation-qa-public-reference.json",
        "accessions/quickdraw-3d-manual-154-public-pdf-public-reference.json",
        "accessions/renderman-interface-spec-31-public-pdf-public-reference.json",
    }
    missing = [path for path in expected if not (ROOT / path).exists()]
    assert missing == []


def test_studio_course_accession_batch_is_recorded():
    expected = {
        "accessions/japan-studio-restructure-public-report-public-reference.json",
        "accessions/opengl-performer-product-brochure-public-reference.json",
        "accessions/psygnosis-studio-liverpool-closure-report-public-reference.json",
        "accessions/psygnosis-studio-liverpool-public-history-public-reference.json",
        "accessions/quesa-16d13-release-report-public-reference.json",
        "accessions/team-ico-playstation-official-pages-public-reference.json",
        "accessions/team-ico-ueda-playstation-blog-interview-public-reference.json",
        "accessions/tri-ace-pbr-implementation-course-notes-public-reference.json",
        "accessions/tri-ace-ps2-sh-lighting-hdr-gdc2005-public-reference.json",
    }
    missing = [path for path in expected if not (ROOT / path).exists()]
    assert missing == []


def test_live_sources_are_cited_by_archive_records():
    source_ids = {record["id"] for record in _json_records("sources")}
    used_source_ids = set()
    for directory in (
        "artifacts",
        "accessions",
        "tasks",
        "milestones",
        "reproductions",
        "snapshots",
        "readiness",
        "builds",
        "harnesses",
        "attempts",
    ):
        for record in _json_records(directory):
            used_source_ids.update(str(source_id) for source_id in record.get("source_ids", []))
    assert sorted(source_ids - used_source_ids) == []


def test_first_archival_packet_tasks_are_recorded():
    expected = {
        "tasks/brender-critical-edition-packet.json",
        "tasks/gool-goal-archive-packet.json",
        "tasks/japan-studio-team-ico-archive-packet.json",
        "tasks/ps1-programmer-tool-archive-packet.json",
        "tasks/ps2-prodg-eb-linux-archive-packet.json",
        "tasks/psygnosis-studio-liverpool-archive-packet.json",
        "tasks/renderware-ps2-archive-packet.json",
        "tasks/tri-ace-ps2-renderer-archive-packet.json",
    }
    missing = [path for path in expected if not (ROOT / path).exists()]
    assert missing == []


def test_first_reproduction_recipe_is_recorded():
    expected = {
        "reproductions/brender-critical-edition-source-build.json",
    }
    missing = [path for path in expected if not (ROOT / path).exists()]
    assert missing == []


def test_first_brender_source_snapshots_are_recorded():
    expected = {
        "snapshots/brender-3dmm-main-head.json",
        "snapshots/brender-v132-main-head.json",
    }
    missing = [path for path in expected if not (ROOT / path).exists()]
    assert missing == []


def test_first_harness_plan_is_recorded():
    expected = {
        "harnesses/brender-v132-portable-core-plan.json",
    }
    missing = [path for path in expected if not (ROOT / path).exists()]
    assert missing == []


def test_first_build_attempts_are_recorded():
    expected = {
        "attempts/brender-v132-harness-materializer-smoke.json",
        "attempts/brender-v132-cmake-configure.json",
        "attempts/brender-v132-core-build-attempt.json",
    }
    missing = [path for path in expected if not (ROOT / path).exists()]
    assert missing == []


def test_lithtech_jupiter_packet_is_recorded():
    expected = {
        "targets/lithtech-jupiter.json",
        "sources/internet-archive-lithtech-jupiter.json",
        "sources/internet-archive-lithtech-jupiter-dev-guide.json",
        "artifacts/lithtech-jupiter-build51-archive-item.json",
        "artifacts/lithtech-jupiter-development-guide.json",
        "accessions/lithtech-jupiter-build51-archive-item-metadata-only.json",
        "accessions/lithtech-jupiter-development-guide-public-reference.json",
        "tasks/lithtech-jupiter-archive-packet.json",
        "milestones/lithtech-jupiter-baseline.json",
        "reproductions/lithtech-jupiter-user-supplied-build.json",
    }
    missing = [path for path in expected if not (ROOT / path).exists()]
    assert missing == []


def test_open_source_remote_head_snapshots_are_recorded():
    expected = {
        "snapshots/aqsis-master-head.json",
        "snapshots/crystal-space-master-head.json",
        "snapshots/mesa-main-head.json",
        "snapshots/ogre-master-head.json",
        "snapshots/open-inventor-master-head.json",
        "snapshots/quesa-master-head.json",
        "snapshots/pixie-master-head.json",
        "snapshots/openphigs-main-head.json",
        "snapshots/opengoal-jak-project-master-head.json",
        "snapshots/psnoobsdk-master-head.json",
        "snapshots/ps2sdk-master-head.json",
    }
    missing = [path for path in expected if not (ROOT / path).exists()]
    assert missing == []


def test_open_source_snapshot_targets_have_reproduction_recipes():
    artifacts = {record["id"]: record for record in _json_records("artifacts")}
    reproduction_targets = {
        record["target_id"] for record in _json_records("reproductions")
    }
    snapshot_targets = set()
    for snapshot in _json_records("snapshots"):
        artifact = artifacts[snapshot["artifact_id"]]
        if (
            str(artifact["redistribution_status"]).startswith("open")
            and artifact["access_level"] == "public"
        ):
            snapshot_targets.add(artifact["target_id"])
    assert sorted(snapshot_targets - reproduction_targets) == []


def test_mesa_reproduction_recipe_is_recorded():
    expected = {
        "sources/mesa-build-docs.json",
        "reproductions/mesa-meson-local-build.json",
    }
    missing = [path for path in expected if not (ROOT / path).exists()]
    assert missing == []
