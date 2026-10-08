#!/usr/bin/env python3
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import os
from pathlib import Path
import re
import stat
import subprocess
import tempfile
import zipfile


ROOT = Path(__file__).resolve().parents[1]
NAME_PATTERN = re.compile(
    r"GlassTTY-rev[0-9]{4}-[0-9]{4}\.[0-9]{2}\.[0-9]{2}\.[0-9]{2}\.[0-9]{2}-"
    r"[a-z0-9][a-z0-9-]*-sandclaude-browser\.zip"
)


def git(*args: str, text: bool = True) -> str | bytes:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=text)


def tracked_files() -> list[tuple[int, Path]]:
    raw = git("ls-files", "-s", "-z", text=False)
    assert isinstance(raw, bytes)
    entries: list[tuple[int, Path]] = []
    for record in raw.split(b"\0"):
        if not record:
            continue
        metadata, name = record.split(b"\t", 1)
        mode = int(metadata.split(b" ", 1)[0], 8)
        path = ROOT / os.fsdecode(name)
        if not path.is_file() or path.is_symlink():
            raise SystemExit(f"release input must be a regular tracked file: {path.relative_to(ROOT)}")
        entries.append((mode, path))
    return sorted(entries, key=lambda item: item[1].relative_to(ROOT).as_posix())


def zip_timestamp() -> tuple[int, int, int, int, int, int]:
    epoch = int(str(git("log", "-1", "--format=%ct")).strip())
    value = datetime.fromtimestamp(max(epoch, 315532800), timezone.utc)
    return value.year, value.month, value.day, value.hour, value.minute, value.second


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a clean GlassTTY Sandclaude browser handoff archive")
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    output = args.output.expanduser().resolve()
    if not NAME_PATTERN.fullmatch(output.name):
        raise SystemExit("output filename must end in a release codename and -sandclaude-browser.zip")
    status = str(git("status", "--porcelain=v1", "--untracked-files=all"))
    if status:
        raise SystemExit("refusing to package a dirty GlassTTY tree")
    subprocess.run(["python3", "scripts/verify-package.py"], cwd=ROOT, check=True)

    output.parent.mkdir(parents=True, exist_ok=True)
    root_name = output.stem
    timestamp = zip_timestamp()
    fd, temporary_name = tempfile.mkstemp(prefix=f".{output.name}.", dir=output.parent)
    os.close(fd)
    temporary = Path(temporary_name)
    try:
        with zipfile.ZipFile(temporary, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
            for git_mode, path in tracked_files():
                relative = path.relative_to(ROOT).as_posix()
                info = zipfile.ZipInfo(f"{root_name}/{relative}", date_time=timestamp)
                info.create_system = 3
                mode = stat.S_IFREG | (0o755 if git_mode & 0o111 else 0o644)
                info.external_attr = mode << 16
                info.compress_type = zipfile.ZIP_DEFLATED
                archive.writestr(info, path.read_bytes(), compresslevel=9)
        with zipfile.ZipFile(temporary) as archive:
            bad = archive.testzip()
            if bad is not None:
                raise SystemExit(f"release archive CRC failed for {bad}")
        os.replace(temporary, output)
    finally:
        temporary.unlink(missing_ok=True)

    digest = hashlib.sha256(output.read_bytes()).hexdigest()
    print(f"{digest}  {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
