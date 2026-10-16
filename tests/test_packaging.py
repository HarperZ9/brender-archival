"""The packaging manifests agree with each other, with the releases they name,
and with the AppImage build that CI runs."""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "packaging"
sys.path.insert(0, str(PACK))

import update_manifests as UM  # noqa: E402


def _winget_fields(text: str) -> dict:
    return dict(re.findall(r"^\s*-?\s*(\w+): (.+)$", text, re.M))


def test_scoop_and_winget_name_the_same_zip_and_hash():
    for product, p in UM.PRODUCTS.items():
        scoop = json.loads((PACK / "scoop" / f"{product}.json").read_text(encoding="utf-8"))
        version = scoop["version"]
        folder = PACK / "winget" / p["identifier"] / version
        installer = _winget_fields((folder / f"{p['identifier']}.installer.yaml").read_text(encoding="utf-8"))
        assert re.fullmatch(r"[0-9a-f]{64}", scoop["hash"])
        assert installer["InstallerSha256"] == scoop["hash"].upper()
        assert installer["InstallerUrl"] == scoop["url"] == UM.zip_url(product, version)
        assert f"{p['tag']}{version}/" in scoop["url"]
        assert scoop["extract_dir"] == product and scoop["bin"] == f"{product}.exe"


def test_every_winget_file_carries_one_identifier_and_version():
    for p in UM.PRODUCTS.values():
        for folder in (PACK / "winget" / p["identifier"]).iterdir():
            files = sorted(folder.glob("*.yaml"))
            assert len(files) == 3
            for f in files:
                fields = _winget_fields(f.read_text(encoding="utf-8"))
                assert fields["PackageIdentifier"] == p["identifier"], f
                assert fields["PackageVersion"] == folder.name, f
                assert fields["ManifestVersion"] == "1.6.0", f


def test_the_generator_reproduces_the_committed_manifests():
    """Without a network: rebuild from the committed hash and compare bytes."""
    for product, p in UM.PRODUCTS.items():
        scoop_path = PACK / "scoop" / f"{product}.json"
        committed = json.loads(scoop_path.read_text(encoding="utf-8"))
        version, digest = committed["version"], committed["hash"]
        assert json.dumps(UM.scoop(product, version, digest), indent=4) + "\n" == scoop_path.read_text(encoding="utf-8")
        for name, text in UM.winget(product, version, digest).items():
            assert (PACK / "winget" / p["identifier"] / version / name).read_text(encoding="utf-8") == text, name


def test_the_appimage_runtime_is_pinned_and_checked_before_use():
    script = (PACK / "appimage" / "build-appimage.sh").read_text(encoding="utf-8")
    assert "\r" not in script
    assert "/releases/download/20251108/runtime-x86_64" in script
    assert re.search(r"RUNTIME_SHA256=[0-9a-f]{64}\n", script)
    assert script.index("sha256sum -c") < script.index('cat "$work/runtime"')


def test_ci_and_releases_smoke_the_appimages_before_upload():
    workflows = ROOT / ".github" / "workflows"
    ci = (workflows / "ci.yml").read_text(encoding="utf-8")
    for image in ("keepers.AppImage", "brview.AppImage"):
        assert f'"$GITHUB_WORKSPACE/{image}" --appimage-extract-and-run' in ci, image
    for name in ("release-keepers.yml", "release-brview.yml"):
        text = (workflows / name).read_text(encoding="utf-8")
        smoke = text.index("--appimage-extract-and-run")
        assert smoke < text.index('gh release upload "$GITHUB_REF_NAME" "$img"'), name
        assert "-x86_64.AppImage" in text


def test_nothing_in_packaging_claims_a_submission():
    readme = (PACK / "README.md").read_text(encoding="utf-8")
    itch = (PACK / "itch" / "keepers-hour.md").read_text(encoding="utf-8")
    assert "Not submitted" in readme and "Nothing here is published" in itch
