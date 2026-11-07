#!/usr/bin/env python3
"""
bump_version.py — deteksi & naikkan versi semantic (semver) pada file-file
project yang umum dipakai (package.json, pyproject.toml, Cargo.toml,
composer.json, gradle.properties, VERSION/version.txt, setup.py/setup.cfg).

Usage:
  python bump_version.py detect [--path .]
      -> cetak JSON berisi file versi yang terdeteksi & versi saat ini

  python bump_version.py bump --type major|minor|patch [--path .]
  python bump_version.py bump --set 2.4.0 [--path .]
      -> update semua file versi yang terdeteksi, cetak JSON:
         {"old_version": "...", "new_version": "...", "files_updated": [...]}

Catatan:
- Jika ada lebih dari satu file versi dan versinya BERBEDA satu sama lain,
  script akan berhenti dan minta konfirmasi manual (kemungkinan monorepo /
  versi yang memang independen) — jangan menebak.
- Script ini tidak melakukan git add/commit/tag/push. Itu bagian dari alur
  di SKILL.md, dilakukan lewat perintah git biasa supaya tetap transparan
  dan bisa dikonfirmasi ke user.
"""
import argparse
import json
import re
import sys
from pathlib import Path

SEMVER_RE = re.compile(r"^(\d+)\.(\d+)\.(\d+)(?:-([0-9A-Za-z.-]+))?(?:\+([0-9A-Za-z.-]+))?$")

VERSION_FILE_SPECS = [
    # (filename, extractor_regex, replacer_template)
    ("package.json", r'"version"\s*:\s*"([^"]+)"', '"version": "{new}"'),
    ("package-lock.json", r'"version"\s*:\s*"([^"]+)"', '"version": "{new}"'),
    ("pyproject.toml", r'(?m)^version\s*=\s*"([^"]+)"', 'version = "{new}"'),
    ("Cargo.toml", r'(?m)^version\s*=\s*"([^"]+)"', 'version = "{new}"'),
    ("composer.json", r'"version"\s*:\s*"([^"]+)"', '"version": "{new}"'),
    ("gradle.properties", r'(?m)^version\s*=\s*(.+)$', 'version={new}'),
    ("VERSION", r'^(.+)$', '{new}'),
    ("version.txt", r'^(.+)$', '{new}'),
    ("setup.py", r'version\s*=\s*["\']([^"\']+)["\']', 'version="{new}"'),
    ("setup.cfg", r'(?m)^version\s*=\s*(.+)$', 'version = {new}'),
]


def find_version_files(root: Path):
    found = []
    for fname, extractor, _ in VERSION_FILE_SPECS:
        fpath = root / fname
        if fpath.exists():
            text = fpath.read_text(encoding="utf-8")
            m = re.search(extractor, text)
            if m:
                raw = m.group(1).strip().strip('"').strip("'")
                found.append({"file": fname, "raw_version": raw})
    return found


def parse_semver(raw: str):
    m = SEMVER_RE.match(raw.strip())
    if not m:
        return None
    major, minor, patch = int(m.group(1)), int(m.group(2)), int(m.group(3))
    return major, minor, patch


def bump(major, minor, patch, bump_type):
    if bump_type == "major":
        return major + 1, 0, 0
    if bump_type == "minor":
        return major, minor + 1, 0
    if bump_type == "patch":
        return major, minor, patch + 1
    raise ValueError(f"unknown bump type: {bump_type}")


def cmd_detect(args):
    root = Path(args.path)
    found = find_version_files(root)
    if not found:
        print(json.dumps({"error": "no_version_file_found", "checked": [s[0] for s in VERSION_FILE_SPECS]}))
        sys.exit(1)
    versions = {f["raw_version"] for f in found}
    print(json.dumps({
        "files": found,
        "current_version": found[0]["raw_version"] if len(versions) == 1 else None,
        "inconsistent": len(versions) > 1,
    }, indent=2))


def cmd_bump(args):
    root = Path(args.path)
    found = find_version_files(root)
    if not found:
        print(json.dumps({"error": "no_version_file_found", "checked": [s[0] for s in VERSION_FILE_SPECS]}))
        sys.exit(1)

    versions = {f["raw_version"] for f in found}
    if len(versions) > 1:
        print(json.dumps({
            "error": "inconsistent_versions",
            "files": found,
            "message": "File versi yang terdeteksi punya nilai berbeda-beda. Konfirmasi manual ke user diperlukan sebelum bump.",
        }, indent=2))
        sys.exit(1)

    current_raw = found[0]["raw_version"]
    parsed = parse_semver(current_raw)
    if not parsed:
        print(json.dumps({"error": "not_semver", "raw_version": current_raw}))
        sys.exit(1)

    if args.set:
        if not parse_semver(args.set):
            print(json.dumps({"error": "invalid_target_version", "value": args.set}))
            sys.exit(1)
        new_version = args.set
    else:
        if not args.type:
            print(json.dumps({"error": "missing_bump_type_or_set"}))
            sys.exit(1)
        major, minor, patch = bump(*parsed, args.type)
        new_version = f"{major}.{minor}.{patch}"

    updated_files = []
    spec_map = {s[0]: s for s in VERSION_FILE_SPECS}
    for f in found:
        fname = f["file"]
        _, extractor, template = spec_map[fname]
        fpath = root / fname
        text = fpath.read_text(encoding="utf-8")
        new_text, n = re.subn(
            extractor,
            lambda m, tpl=template: _render_replacement(m, tpl, new_version),
            text,
            count=1,
        )
        if n == 0:
            continue
        fpath.write_text(new_text, encoding="utf-8")
        updated_files.append(fname)

    print(json.dumps({
        "old_version": current_raw,
        "new_version": new_version,
        "files_updated": updated_files,
    }, indent=2))


def _render_replacement(match, template, new_version):
    # Ganti seluruh match (bukan hanya group version) supaya format sekitar
    # (indentasi, tanda kutip, dsb.) tetap terjaga per-jenis file.
    full = match.group(0)
    old_value = match.group(1)
    rendered = template.format(new=new_version)
    return full.replace(f'"{old_value}"', f'"{new_version}"') if f'"{old_value}"' in full else rendered


def main():
    parser = argparse.ArgumentParser(description="Deteksi & bump semantic version project")
    sub = parser.add_subparsers(dest="command", required=True)

    p_detect = sub.add_parser("detect")
    p_detect.add_argument("--path", default=".")
    p_detect.set_defaults(func=cmd_detect)

    p_bump = sub.add_parser("bump")
    p_bump.add_argument("--path", default=".")
    p_bump.add_argument("--type", choices=["major", "minor", "patch"])
    p_bump.add_argument("--set", help="Set versi eksplisit, mis. 2.4.0 (override --type)")
    p_bump.set_defaults(func=cmd_bump)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
