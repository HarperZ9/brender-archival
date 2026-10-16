"""Write the winget and Scoop manifests for one released product.

    python packaging/update_manifests.py keepers-hour 0.4.0
    python packaging/update_manifests.py brview 0.1.2

Reads the SHA-256 the release workflow published beside the Windows zip
(`<zip>.sha256` on the GitHub release), so a manifest can only name a hash
that CI produced after the packaged smoke run. Writes:

    packaging/winget/<Identifier>/<version>/*.yaml   (three files, schema 1.6.0)
    packaging/scoop/<product>.json

Nothing is submitted anywhere. Submitting to winget-pkgs or a Scoop bucket is
the author's decision. Standard library only.
"""
from __future__ import annotations

import json
import re
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = "https://github.com/HarperZ9/brender-archival"

PRODUCTS = {
    "keepers-hour": {
        "tag": "keepers-v",
        "identifier": "HarperZ9.TheKeepersHour",
        "name": "The Keeper's Hour",
        "short": "A short, talkative game about the last night of a lighthouse, built on Argonaut's 1990s BRender engine.",
        "description": (
            "The last night of a lighthouse on a coast the sea left years ago. Walk the tower, talk to what is in it, "
            "listen to the four voices in the keeper's head, and decide what happens to the light at dawn. About 25 "
            "minutes, three endings, keyboard, mouse and gamepad. Built on BRender 1.4 (BlazingRenderer, MIT), running "
            "64-bit. Code MIT; words and art CC BY 4.0."
        ),
        "license": "MIT,CC-BY-4.0",
        "license_note": "Code MIT; words and art CC BY 4.0",
        "tags": ["game", "adventure", "narrative", "brender", "retro"],
        "page": f"{REPO}/tree/main/games/keepers-hour",
    },
    "brview": {
        "tag": "brview-v",
        "identifier": "HarperZ9.brview",
        "name": "brview",
        "short": "A viewer for Argonaut's 1998 BRender sample models, on the modern 64-bit BRender.",
        "description": (
            "Opens the sample models that shipped with BRender 1.3.2 (Argonaut Software, 1998, MIT) and your own .dat "
            "models in a window, with mouse, keyboard and gamepad controls and OpenGL or BRender's software rasteriser."
        ),
        "license": "MIT",
        "license_note": "MIT",
        "tags": ["3d", "viewer", "brender", "retro"],
        "page": f"{REPO}/tree/main/modern",
    },
}


def zip_name(product: str, version: str) -> str:
    return f"{product}-{version}-windows-x64.zip"


def zip_url(product: str, version: str) -> str:
    return f"{REPO}/releases/download/{PRODUCTS[product]['tag']}{version}/{zip_name(product, version)}"


def released_sha256(product: str, version: str) -> str:
    with urllib.request.urlopen(zip_url(product, version) + ".sha256", timeout=60) as response:
        text = response.read().decode("ascii")
    digest, name = text.split()
    if name != zip_name(product, version) or not re.fullmatch(r"[0-9a-f]{64}", digest):
        raise SystemExit(f"unexpected checksum file: {text!r}")
    return digest


def winget(product: str, version: str, digest: str) -> dict[str, str]:
    p = PRODUCTS[product]
    ident = p["identifier"]
    head = f"# yaml-language-server: $schema=https://aka.ms/winget-manifest.{{kind}}.1.6.0.schema.json\n\n"
    common = f"PackageIdentifier: {ident}\nPackageVersion: {version}\n"
    tags = "".join(f"- {t}\n" for t in p["tags"])
    return {
        f"{ident}.yaml": head.format(kind="version") + common
        + "DefaultLocale: en-US\nManifestType: version\nManifestVersion: 1.6.0\n",
        f"{ident}.installer.yaml": head.format(kind="installer") + common
        + "InstallerType: zip\nNestedInstallerType: portable\nNestedInstallerFiles:\n"
        + f"- RelativeFilePath: {product}\\{product}.exe\n  PortableCommandAlias: {product}\n"
        + "Installers:\n- Architecture: x64\n"
        + f"  InstallerUrl: {zip_url(product, version)}\n  InstallerSha256: {digest.upper()}\n"
        + "ManifestType: installer\nManifestVersion: 1.6.0\n",
        f"{ident}.locale.en-US.yaml": head.format(kind="defaultLocale") + common
        + "PackageLocale: en-US\nPublisher: Zain Dana Harper\n"
        + f"PublisherUrl: https://github.com/HarperZ9\nPackageName: {p['name']}\nPackageUrl: {p['page']}\n"
        + f"License: {p['license_note']}\nLicenseUrl: {REPO}/blob/main/LICENSE\n"
        + f"ShortDescription: {json.dumps(p['short'])}\nDescription: {json.dumps(p['description'])}\n"
        + f"Tags:\n{tags}ManifestType: defaultLocale\nManifestVersion: 1.6.0\n",
    }


def scoop(product: str, version: str, digest: str) -> dict:
    p = PRODUCTS[product]
    return {
        "version": version,
        "description": p["short"],
        "homepage": p["page"],
        "license": p["license"],
        "url": zip_url(product, version),
        "hash": digest,
        "extract_dir": product,
        "bin": f"{product}.exe",
        "shortcuts": [[f"{product}.exe", p["name"]]],
        "checkver": {"github": REPO, "regex": f"{p['tag']}([\\d.]+)"},
        "autoupdate": {
            "url": f"{REPO}/releases/download/{p['tag']}$version/{product}-$version-windows-x64.zip",
            "hash": {"url": "$url.sha256"},
            "extract_dir": product,
        },
    }


def main(product: str, version: str) -> None:
    digest = released_sha256(product, version)
    out = ROOT / "packaging" / "winget" / PRODUCTS[product]["identifier"] / version
    out.mkdir(parents=True, exist_ok=True)
    for name, text in winget(product, version, digest).items():
        (out / name).write_text(text, encoding="utf-8", newline="\n")
    (ROOT / "packaging" / "scoop" / f"{product}.json").write_text(
        json.dumps(scoop(product, version, digest), indent=4) + "\n", encoding="utf-8", newline="\n")
    print(f"{product} {version}: sha256 {digest}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
