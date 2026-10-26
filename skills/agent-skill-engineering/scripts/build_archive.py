#!/usr/bin/env python3
"""Rebuild the grounding archive reproducibly from a directory of source files."""

import argparse
import gzip
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import sys
import tarfile


def regular_file_inside(source_dir, name):
    parts = PurePosixPath(name).parts
    if not isinstance(name, str) or not parts or PurePosixPath(name).is_absolute() or ".." in parts:
        raise ValueError(f"unsafe manifest path: {name!r}")
    path = source_dir
    for part in parts:
        path = path / part
        if path.is_symlink():
            raise ValueError(f"symlink in source tree: {name}")
    if not path.is_file():
        raise ValueError(f"missing source file: {name}")
    return path


def build(manifest, source_dir, output):
    members = [entry["path"] for entry in manifest["files"] if entry.get("bundled", True)]
    if not members:
        raise ValueError("manifest lists no bundled source files")
    if len({str(name).casefold() for name in members}) != len(members):
        raise ValueError("duplicate or case-colliding source paths in manifest")
    if Path(output).resolve().is_relative_to(source_dir.resolve()):
        raise ValueError("output must be outside source_dir")
    payload = io.BytesIO()
    report = []
    with tarfile.open(fileobj=payload, mode="w", format=tarfile.PAX_FORMAT) as archive:
        for name in members:
            content = regular_file_inside(source_dir, name).read_bytes()
            info = tarfile.TarInfo(name)
            info.size, info.mode, info.mtime = len(content), 0o644, 0
            info.uid = info.gid = 0
            info.uname = info.gname = ""
            archive.addfile(info, io.BytesIO(content))
            report.append({"path": name, "bytes": len(content),
                           "sha256": hashlib.sha256(content).hexdigest()})
    with open(output, "wb") as raw, gzip.GzipFile(filename="", mode="wb", fileobj=raw,
                                                  compresslevel=9, mtime=0) as stream:
        stream.write(payload.getvalue())
    return {"archive_sha256": hashlib.sha256(Path(output).read_bytes()).hexdigest(),
            "files": report}


def main():
    parser = argparse.ArgumentParser(
        description="Write the bundled files listed in provenance/sources.json, in manifest order, "
                    "to a deterministic archive and print the hashes to record. Does not edit the manifest.",
        epilog="Exit codes: 0 written; 1 unsafe, missing, or unreadable input, or unwritable output; 2 usage error.",
    )
    parser.add_argument("source_dir", help="directory holding the files at their manifest paths")
    parser.add_argument("output", help="archive path to write; review before replacing the shipped archive")
    args = parser.parse_args()
    skill_root = Path(__file__).resolve().parents[1]
    try:
        manifest = json.loads((skill_root / "provenance/sources.json").read_text())
        result = build(manifest, Path(args.source_dir), args.output)
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f"Archive build failed: {error}", file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
