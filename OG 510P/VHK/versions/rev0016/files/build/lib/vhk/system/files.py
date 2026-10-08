from __future__ import annotations

import csv
import fnmatch
import json
from pathlib import Path
from typing import Any


def read_text(path: str | Path, *, encoding: str = "utf-8") -> str:
    p = Path(path).expanduser()
    return p.read_text(encoding=encoding)


def write_text(path: str | Path, text: str, *, encoding: str = "utf-8", create_parents: bool = True, append: bool = False) -> Path:
    p = Path(path).expanduser()
    if create_parents:
        p.parent.mkdir(parents=True, exist_ok=True)
    mode = "a" if append else "w"
    with p.open(mode, encoding=encoding) as f:
        f.write(text)
    return p


def read_csv(path: str | Path, *, encoding: str = "utf-8", delimiter: str = ",", has_header: bool = True) -> list[Any]:
    p = Path(path).expanduser()
    with p.open("r", encoding=encoding, newline="") as f:
        if has_header:
            reader = csv.DictReader(f, delimiter=delimiter)
            return [dict(row) for row in reader]
        reader = csv.reader(f, delimiter=delimiter)
        return [list(row) for row in reader]


def write_csv(
    path: str | Path,
    rows: list[Any],
    *,
    encoding: str = "utf-8",
    delimiter: str = ",",
    create_parents: bool = True,
    append: bool = False,
    include_header: bool = True,
    fieldnames: list[str] | None = None,
) -> Path:
    p = Path(path).expanduser()
    if create_parents:
        p.parent.mkdir(parents=True, exist_ok=True)

    rows_list = list(rows)
    if not rows_list:
        if not append and not p.exists():
            p.write_text("", encoding=encoding)
        return p

    first = rows_list[0]
    mode = "a" if append else "w"
    with p.open(mode, encoding=encoding, newline="") as f:
        if isinstance(first, dict):
            cols = list(fieldnames or first.keys())
            writer = csv.DictWriter(f, fieldnames=cols, delimiter=delimiter)
            should_write_header = bool(include_header) and (not append or p.stat().st_size == 0)
            if should_write_header:
                writer.writeheader()
            for row in rows_list:
                writer.writerow({k: row.get(k, "") for k in cols})
        else:
            writer = csv.writer(f, delimiter=delimiter)
            for row in rows_list:
                if isinstance(row, (list, tuple)):
                    writer.writerow(list(row))
                else:
                    writer.writerow([row])
    return p


def read_json(path: str | Path, *, encoding: str = "utf-8") -> Any:
    p = Path(path).expanduser()
    with p.open("r", encoding=encoding) as f:
        return json.load(f)


def write_json(path: str | Path, value: Any, *, encoding: str = "utf-8", indent: int = 2, create_parents: bool = True) -> Path:
    p = Path(path).expanduser()
    if create_parents:
        p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding=encoding) as f:
        json.dump(value, f, indent=indent, ensure_ascii=False)
        f.write("\n")
    return p


def list_directory(path: str | Path, *, pattern: str | None = None, recursive: bool = False, files_only: bool = False, dirs_only: bool = False, sort: str = "name") -> list[str]:
    root = Path(path).expanduser()
    iterator = root.rglob("*") if recursive else root.iterdir()
    items: list[Path] = []
    for entry in iterator:
        if files_only and not entry.is_file():
            continue
        if dirs_only and not entry.is_dir():
            continue
        rel = entry.relative_to(root)
        rel_str = rel.as_posix()
        if pattern and not fnmatch.fnmatch(rel_str, pattern):
            continue
        items.append(entry)

    if sort == "mtime":
        items.sort(key=lambda p: (p.stat().st_mtime_ns, p.name))
    else:
        items.sort(key=lambda p: p.as_posix())

    return [p.relative_to(root).as_posix() for p in items]
