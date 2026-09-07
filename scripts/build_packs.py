#!/usr/bin/env python3
"""Build Minecraft-ready ZIPs without changing the source pack folders."""

import argparse
import json
import os
from pathlib import Path
import re
import zipfile


ROOT = Path(__file__).resolve().parents[1]
PACKS = ("Generic", "Parks")


def build_pack(root, output, name, build_number):
    version = (root / f"{name.upper()}_VERSION").read_text(encoding="utf-8").strip()
    if not re.fullmatch(r"(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)", version):
        raise ValueError(f"{name}: version must use X.Y.Z, got {version!r}")

    source = root / f"{name} RP"
    metadata = json.loads((source / "pack.mcmeta").read_text(encoding="utf-8"))
    description = metadata["pack"]["description"]
    if not isinstance(description, str):
        raise ValueError(f"{name}: pack description must be a string")
    description, count = re.subn(
        r"Version \d+\.\d+\.\d+(?: · Build [\w.-]+)?",
        f"Version {version} · Build {build_number}",
        description,
    )
    if count != 1:
        raise ValueError(f"{name}: expected exactly one 'Version X.Y.Z' in pack.mcmeta")
    metadata["pack"]["description"] = description

    destination = output / f"MagicalDreams-{name}-Pack.zip"
    with zipfile.ZipFile(destination, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(source.rglob("*")):
            if not path.is_file() or path.name.endswith(".DS_Store"):
                continue
            relative = path.relative_to(source).as_posix()
            if relative == "pack.mcmeta":
                archive.writestr(relative, json.dumps(metadata, ensure_ascii=False, indent=2) + "\n")
            else:
                archive.write(path, relative)

    with zipfile.ZipFile(destination) as archive:
        bad_file = archive.testzip()
        if bad_file:
            raise ValueError(f"{name}: corrupt ZIP entry {bad_file}")
        if json.loads(archive.read("pack.mcmeta")) != metadata:
            raise ValueError(f"{name}: packaged metadata does not match")
    print(f"Built {destination.name}: version {version}, build {build_number}")
    return version


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build-number", default="local")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "dist")
    args = parser.parse_args()
    if args.build_number != "local" and not re.fullmatch(r"[1-9]\d*", args.build_number):
        parser.error("--build-number must be a positive integer or 'local'")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    versions = {
        name: build_pack(ROOT, args.output_dir, name, args.build_number)
        for name in PACKS
    }
    notes = f"Build {args.build_number}\n\n"
    notes += "\n".join(f"- {name}: {version}" for name, version in versions.items())
    notes += f"\n\nSource commit: `{os.environ.get('GITHUB_SHA', 'local working tree')}`\n\n"
    notes += "Place the desired ZIP directly in Minecraft's `resourcepacks` folder.\n\n"
    (args.output_dir / "release-notes.md").write_text(notes, encoding="utf-8")


if __name__ == "__main__":
    main()
