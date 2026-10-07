#!/usr/bin/env python3
"""Validate source-path and source-hash bindings for every active queue note.

Release-readiness already checks Candidate and Published-ready entries. This
archive-wide queue binding audit also covers Hold notes, so review debt cannot
silently drift away from the current source bytes.
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import pathlib
import re
import sys
from typing import Any

CHECKED_STATES = ["candidate", "published_ready", "hold"]
STATE_DIR = {
    "candidate": "release_queue/candidates",
    "published_ready": "release_queue/published_ready",
    "hold": "release_queue/hold",
}
SOURCE_LINE_RE = re.compile(r"^- Source paper: `([^`]+)`$", re.MULTILINE)
HASH_LINE_RE = re.compile(r"^- Queue-bound source SHA-256: `sha256:([0-9a-f]{64})`$", re.MULTILINE)


def load_json(path: pathlib.Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def note_files(root: pathlib.Path, state: str) -> list[str]:
    directory = root / STATE_DIR[state]
    if not directory.exists():
        return []
    return sorted(p.relative_to(root).as_posix() for p in directory.glob("*.md") if p.name != "README.md")


def audit_item(root: pathlib.Path, item: dict[str, Any], state: str) -> dict[str, Any]:
    note_rel = str(item.get("path", ""))
    source_rel = str(item.get("source_tex", ""))
    row: dict[str, Any] = {
        "item_id": str(item.get("item_id", "")),
        "queue_state": state,
        "note_path": note_rel,
        "source_tex": source_rel,
        "status": "pass",
        "failures": [],
    }
    failures: list[dict[str, Any]] = []
    note_path = root / note_rel if note_rel else root / "__missing_note__"
    source_path = root / source_rel if source_rel else root / "__missing_source__"

    if not note_rel:
        failures.append({"category": "missing_note_path", "detail": "queue item has no path"})
    elif not note_path.exists():
        failures.append({"category": "missing_note_file", "detail": note_rel})
    elif state not in STATE_DIR or not note_rel.startswith(STATE_DIR[state] + "/"):
        failures.append({"category": "note_state_directory_mismatch", "detail": {"state": state, "note_path": note_rel}})

    if not source_rel:
        failures.append({"category": "missing_source_tex", "detail": note_rel})
    elif not source_path.exists():
        failures.append({"category": "missing_source_file", "detail": source_rel})
    elif source_path.suffix != ".tex":
        failures.append({"category": "source_not_tex", "detail": source_rel})

    current_hash = ""
    if source_path.exists() and source_path.is_file():
        current_hash = sha256_file(source_path)
        row["source_sha256"] = current_hash
        row["source_bytes"] = source_path.stat().st_size

    if note_path.exists() and note_path.is_file():
        text = note_path.read_text(encoding="utf-8", errors="replace")
        note_sources = SOURCE_LINE_RE.findall(text)
        note_hashes = HASH_LINE_RE.findall(text)
        row["note_source_lines"] = note_sources
        row["note_source_sha256_values"] = note_hashes
        if len(note_sources) != 1:
            failures.append({"category": "note_source_line_count", "detail": {"count": len(note_sources), "values": note_sources[:5]}})
        elif note_sources[0] != source_rel:
            failures.append({"category": "note_source_line_mismatch", "detail": {"queue_index": source_rel, "note": note_sources[0]}})
        if len(note_hashes) != 1:
            failures.append({"category": "note_source_sha256_line_count", "detail": {"count": len(note_hashes), "values": ["sha256:" + h for h in note_hashes[:5]]}})
        elif current_hash and note_hashes[0] != current_hash:
            failures.append({"category": "note_source_sha256_mismatch", "detail": {"current": "sha256:" + current_hash, "note": "sha256:" + note_hashes[0]}})

    row["status"] = "fail" if failures else "pass"
    row["failures"] = failures
    return row


def check(root: pathlib.Path) -> dict[str, Any]:
    release = load_json(root / "RELEASE_MANIFEST.json")
    queue = load_json(root / "release_queue" / "QUEUE_INDEX.json")
    rows: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []

    queue_note_paths: set[str] = set()
    directory_note_paths: set[str] = set()
    source_bindings: dict[str, list[dict[str, str]]] = collections.defaultdict(list)

    for state in CHECKED_STATES:
        items = queue.get("states", {}).get(state, [])
        for item in items:
            if not isinstance(item, dict):
                continue
            note_path = str(item.get("path", ""))
            source_tex = str(item.get("source_tex", ""))
            if note_path:
                queue_note_paths.add(note_path)
            if source_tex:
                source_bindings[source_tex].append({"state": state, "note_path": note_path, "item_id": str(item.get("item_id", ""))})
            rows.append(audit_item(root, item, state))
        for rel in note_files(root, state):
            directory_note_paths.add(rel)

    missing_from_queue = sorted(directory_note_paths - queue_note_paths)
    missing_from_directory = sorted(queue_note_paths - directory_note_paths)
    duplicates = [
        {"source_tex": src, "bindings": bindings}
        for src, bindings in sorted(source_bindings.items())
        if len(bindings) > 1
    ]

    for row in rows:
        for failure in row.get("failures", []):
            failures.append({"note_path": row.get("note_path"), "source_tex": row.get("source_tex"), **failure})
    for rel in missing_from_queue:
        failures.append({"category": "note_file_missing_from_queue_index", "note_path": rel})
    for rel in missing_from_directory:
        failures.append({"category": "queue_index_note_missing_from_directory", "note_path": rel})
    for dup in duplicates:
        failures.append({"category": "duplicate_queue_source_binding", **dup})

    state_counts = {state: len(queue.get("states", {}).get(state, [])) for state in CHECKED_STATES}
    note_counts = {state: len(note_files(root, state)) for state in CHECKED_STATES}
    count_mismatches = {state: {"queue_index": state_counts[state], "directory": note_counts[state]} for state in CHECKED_STATES if state_counts[state] != note_counts[state]}
    for state, detail in count_mismatches.items():
        failures.append({"category": "queue_state_count_mismatch", "state": state, "detail": detail})

    failure_counter = collections.Counter(str(f.get("category", "unknown")) for f in failures)
    bound_rows = [r for r in rows if r.get("status") == "pass"]
    return {
        "status": "pass" if not failures else "fail",
        "generated_for_revision": release["revision"],
        "checked_bundle": release["bundle"],
        "publication_authorized": False,
        "checked_states": CHECKED_STATES,
        "rows": rows,
        "duplicate_source_bindings": duplicates,
        "missing_from_queue_index": missing_from_queue,
        "missing_from_directories": missing_from_directory,
        "summary": {
            "queue_note_count": len(rows),
            "queue_note_pass_count": len(bound_rows),
            "queue_note_fail_count": len(rows) - len(bound_rows),
            "state_counts": state_counts,
            "directory_note_counts": note_counts,
            "duplicate_source_binding_count": len(duplicates),
            "missing_from_queue_index_count": len(missing_from_queue),
            "missing_from_directory_count": len(missing_from_directory),
            "failure_count": len(failures),
            "failure_category_counts": dict(sorted(failure_counter.items())),
        },
        "failures": failures[:100],
        "fail_closed_rule": "If any queue note lacks a current source path/hash binding, default to no publication and repair the queue note before relying on its state.",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--write-report", default="")
    args = parser.parse_args()
    root = pathlib.Path(args.root).resolve()
    report = check(root)
    text = json.dumps(report, indent=2) + "\n"
    if args.write_report:
        out = root / args.write_report
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding="utf-8")
    sys.stdout.write(text)
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
