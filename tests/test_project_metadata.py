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
