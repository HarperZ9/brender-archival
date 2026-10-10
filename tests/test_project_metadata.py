from __future__ import annotations

from pathlib import Path
import tomllib

from packaging.requirements import Requirement


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_media_extra_declares_pillow_for_release_artifact_rendering():
    pyproject = tomllib.loads((PROJECT_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    optional_dependencies = pyproject["project"]["optional-dependencies"]

    assert "media" in optional_dependencies

    requirements = [Requirement(value) for value in optional_dependencies["media"]]
    assert any(requirement.name.lower() == "pillow" for requirement in requirements)


def test_engine_revival_is_a_pinned_dependency_not_a_vendored_copy():
    pyproject = tomllib.loads((PROJECT_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    requirements = [Requirement(value) for value in pyproject["project"]["dependencies"]]
    engine = [r for r in requirements if r.name == "engine-revival"]
    assert len(engine) == 1
    assert engine[0].url.endswith("@v0.3.0"), "pin engine-revival to a release tag"
    assert not (PROJECT_ROOT / "src" / "engine_revival").exists()
