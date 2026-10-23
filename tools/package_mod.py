"""Build and verify a deterministic, portable TFR Estonia development ZIP.

Only packages the local submod; never modifies or publishes the parent mod.
Run from any directory: python tools/package_mod.py [--output PATH] [--check]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INSTALL_FOLDER = "tfr-estonia"
LAUNCHER_PATH = "mod/tfr-estonia"
PACKAGE_MANIFEST = "tfr-estonia/PACKAGE-MANIFEST.json"
CONTENT_DIRS = {"common", "docs", "events", "gfx", "history", "interface", "localisation", "tests", "tools"}
ROOT_FILES = {"README.md", "CHANGELOG.md", "thumbnail.png", ".gitattributes", ".gitignore"}
EXCLUDED_DIRS = {".git", ".cache", "__pycache__", ".pytest_cache", "test-output", "dist", "logs"}
# Source photos and parent-mod style sheets are local research inputs. Ship the
# generated artwork and attribution registers without the reference originals.
RESEARCH_ONLY_PREFIXES = (
    "docs/artwork/ministers/references/",
    "docs/artwork/ideology/references/",
)
FIXED_ZIP_DATE = (2020, 1, 1, 0, 0, 0)
ABSOLUTE_PATH = re.compile(r'(?:[A-Za-z]:[\\/]|(?<!:)//|\\\\|"\s*/(?:Users|home|tmp|mnt|var)/)')


def metadata_value(descriptor: str, key: str) -> str:
    match = re.search(rf'^\s*{re.escape(key)}\s*=\s*"([^"\n]+)"\s*$', descriptor, re.M)
    if not match:
        raise ValueError(f"Missing descriptor field: {key}")
    return match[1]


def portable_descriptors(source: str) -> tuple[bytes, bytes, str]:
    version = metadata_value(source, "version")
    # Local launcher paths, Workshop IDs and package archives belong to the
    # installation that created them; never ship them as portable metadata.
    descriptor = re.sub(r'^\s*(?:path|archive|remote_file_id|picture)\s*=.*\r?\n?', "", source, flags=re.M)
    descriptor = re.sub(r'^\s*version\s*=.*$', f'version="{version}-development"', descriptor, flags=re.M)
    descriptor = re.sub(r'^\s*name\s*=.*$', 'name="TFR Estonia (Development)"', descriptor, flags=re.M)
    descriptor = descriptor.replace("\r\n", "\n").strip() + '\npicture="thumbnail.png"\n'
    if ABSOLUTE_PATH.search(descriptor):
        raise ValueError("A host-specific absolute path remains in the portable descriptor.")
    if not re.search(r'dependencies\s*=\s*\{\s*"The Fire Rises"\s*\}', descriptor):
        raise ValueError('The descriptor must declare dependency "The Fire Rises".')
    launcher = descriptor + f'path="{LAUNCHER_PATH}"\n'
    return descriptor.encode("utf-8"), launcher.encode("utf-8"), version


def package_entries(root: Path) -> tuple[dict[str, bytes], str]:
    root = root.resolve()
    source = (root / "descriptor.mod").read_text(encoding="utf-8-sig")
    descriptor, launcher, version = portable_descriptors(source)
    entries = {
        f"{INSTALL_FOLDER}/descriptor.mod": descriptor,
        f"{INSTALL_FOLDER}.mod": launcher,
    }
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root)
        if relative.as_posix().startswith(RESEARCH_ONLY_PREFIXES):
            continue
        if any(part in EXCLUDED_DIRS for part in relative.parts):
            continue
        if path.is_symlink():
            raise ValueError(f"Package input may not contain symlinks: {relative.as_posix()}")
        if not path.is_file() or path.suffix.lower() in {".pyc", ".pyo", ".zip"}:
            continue
        if relative.parts[0] not in CONTENT_DIRS and relative.as_posix() not in ROOT_FILES:
            continue
        entries[f"{INSTALL_FOLDER}/{relative.as_posix()}"] = path.read_bytes()
    for required in ("README.md", "thumbnail.png"):
        if f"{INSTALL_FOLDER}/{required}" not in entries:
            raise ValueError(f"Missing required package file: {required}")
    compatibility = root / "docs/compatibility.json"
    parent_version = json.loads(compatibility.read_text(encoding="utf-8"))["version"] if compatibility.exists() else "unspecified"
    manifest = {
        "format": 1,
        "name": "TFR Estonia",
        "build_status": "development",
        "source_version": version,
        "package_version": version + "-development",
        "parent": "The Fire Rises",
        "parent_version": parent_version,
        "supported_game_version": metadata_value(source, "supported_version"),
        "install_directory": INSTALL_FOLDER,
        "launcher_path": LAUNCHER_PATH,
        "workshop_published": False,
        "files": [
            {"path": name, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}
            for name, data in sorted(entries.items())
        ],
    }
    manifest_bytes = (json.dumps(manifest, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    if ABSOLUTE_PATH.search(manifest_bytes.decode("utf-8")):
        raise ValueError("A host-specific absolute path remains in the package manifest.")
    entries[PACKAGE_MANIFEST] = manifest_bytes
    return entries, version


def write_zip(destination: Path, entries: dict[str, bytes]) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(destination, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name, data in sorted(entries.items()):
            info = zipfile.ZipInfo(name, date_time=FIXED_ZIP_DATE)
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, data, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)


def verify_zip(destination: Path, expected: dict[str, bytes]) -> None:
    with zipfile.ZipFile(destination) as archive:
        names = archive.namelist()
        if len(names) != len(set(names)) or set(names) != set(expected):
            raise ValueError("ZIP contents differ from the current portable package inputs.")
        bad = archive.testzip()
        if bad:
            raise ValueError(f"ZIP CRC error: {bad}")
        for name in names:
            if archive.read(name) != expected[name]:
                raise ValueError(f"ZIP content mismatch: {name}")
            if any(part in EXCLUDED_DIRS for part in Path(name).parts) or name.startswith(("/", "\\")) or ".." in Path(name).parts:
                raise ValueError(f"Unsafe or excluded package entry: {name}")
        launcher = archive.read(f"{INSTALL_FOLDER}.mod").decode("utf-8")
        if metadata_value(launcher, "path") != LAUNCHER_PATH or ABSOLUTE_PATH.search(launcher):
            raise ValueError("The launcher descriptor is not portable.")
        if re.search(r'^\s*(?:path|archive|remote_file_id)\s*=', archive.read(f"{INSTALL_FOLDER}/descriptor.mod").decode("utf-8"), re.M):
            raise ValueError("The internal descriptor contains installation-specific metadata.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="ZIP destination; default: dist/tfr-estonia-VERSION-development.zip")
    parser.add_argument("--check", action="store_true", help="Verify an existing ZIP against the current sources without writing.")
    args = parser.parse_args()
    entries, version = package_entries(ROOT)
    destination = args.output or ROOT / "dist" / f"tfr-estonia-{version}-development.zip"
    if not args.check:
        write_zip(destination, entries)
    verify_zip(destination, entries)
    digest = hashlib.sha256(destination.read_bytes()).hexdigest()
    print(f"Development package {'verified' if args.check else 'created'}: {destination.resolve()}")
    print(f"Files: {len(entries)}; bytes: {destination.stat().st_size}; SHA-256: {digest}")


if __name__ == "__main__":
    main()
