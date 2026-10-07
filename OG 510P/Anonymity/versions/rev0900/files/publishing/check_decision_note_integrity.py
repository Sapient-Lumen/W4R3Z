#!/usr/bin/env python3
"""Fail-closed structural checks for release_queue/decisions/*.md.

The decision index is compact and useful, but it is derived from Markdown.  This
checker guards the source notes themselves so publication posture, subject paths,
latest-note ordering, and revision/bundle snippets cannot silently drift.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys
from typing import Any

FILENAME_RE = re.compile(r"^(?P<date>\d{4}\.\d{2}\.\d{2})-(?P<time>\d{4}[^-]*)-(?P<slug>.+)\.md$")
SUBJECT_RE = re.compile(r"^- Subject:\s*`([^`]+\.tex)`\s*$", re.MULTILINE)
REVISION_RE = re.compile(r"^- Revision:\s*(rev\d{4})\s*$", re.MULTILINE)
BUNDLE_RE = re.compile(r"^- Bundle:\s*`([^`]+\.zip)`\s*$", re.MULTILINE)
ACTION_RE = re.compile(r"^- Action:\s*(.+?)\s*$", re.MULTILINE)
QUEUE_POSTURE_RE = re.compile(r"^- Queue posture:\s*(.+?)\s*$", re.MULTILINE)
DATE_FIELD_RE = re.compile(r"^- Date:\s*(.+?)\s*$", re.MULTILINE)

NO_PUBLICATION_PHRASES = (
    "no publication",
    "publish nothing",
    "published nothing",
    "no paper moved",
    "no paper was published",
    "publication action\n\nnone",
    "publication action\r\n\r\nnone",
)


def load_json(path: pathlib.Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def first_line(text: str) -> str:
    return text.splitlines()[0].strip() if text.splitlines() else ""


def sorted_decision_paths(root: pathlib.Path) -> list[pathlib.Path]:
    return sorted((root / "release_queue" / "decisions").glob("*.md"), key=lambda p: p.name)


def check_revision_note(rel: str, text: str, release: dict[str, Any]) -> list[dict[str, Any]]:
    failures: list[dict[str, Any]] = []
    rev_match = REVISION_RE.search(text)
    bundle_match = BUNDLE_RE.search(text)
    action_match = ACTION_RE.search(text)
    posture_match = QUEUE_POSTURE_RE.search(text)
    date_match = DATE_FIELD_RE.search(text)
    is_revision_note = bool(rev_match or bundle_match or action_match or posture_match)
    if not is_revision_note:
        return failures
    required = {
        "date": date_match,
        "revision": rev_match,
        "bundle": bundle_match,
        "action": action_match,
        "queue_posture": posture_match,
    }
    for name, match in required.items():
        if match is None:
            failures.append({"category": "revision_note_missing_field", "path": rel, "field": name})
    if rev_match and bundle_match:
        revision = rev_match.group(1)
        bundle = bundle_match.group(1)
        if not bundle.startswith(f"Anonymity-{revision}-"):
            failures.append({"category": "revision_bundle_mismatch", "path": rel, "revision": revision, "bundle": bundle})
        if revision == release.get("revision") and bundle != release.get("bundle"):
            failures.append({"category": "current_revision_bundle_not_current_release", "path": rel, "bundle": bundle, "expected_bundle": release.get("bundle")})
    if action_match and "no publication" not in action_match.group(1).lower():
        failures.append({"category": "revision_action_not_explicit_no_publication", "path": rel, "action": action_match.group(1)})
    if posture_match:
        posture = posture_match.group(1)
        for fragment in ["Candidate", "Published-ready", "Hold", "published"]:
            if fragment not in posture:
                failures.append({"category": "queue_posture_missing_fragment", "path": rel, "fragment": fragment, "queue_posture": posture})
    return failures


def check(root: pathlib.Path) -> dict[str, Any]:
    release = load_json(root / "RELEASE_MANIFEST.json")
    decision_index = load_json(root / "release_queue" / "DECISION_INDEX.json")
    latest_json = load_json(root / "release_queue" / "LATEST_DECISION.json")
    paths = sorted_decision_paths(root)
    rows: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    stems_seen: set[str] = set()
    subject_count = 0
    revision_note_count = 0

    for path in paths:
        rel = path.relative_to(root).as_posix()
        text = path.read_text(encoding="utf-8", errors="replace")
        lower = text.lower()
        stem = path.stem
        path_failures: list[dict[str, Any]] = []
        match = FILENAME_RE.match(path.name)
        if not match:
            path_failures.append({"category": "decision_filename_not_timestamp_slug_no_publication_form", "path": rel})
        if stem in stems_seen:
            path_failures.append({"category": "duplicate_decision_stem", "path": rel, "stem": stem})
        stems_seen.add(stem)
        heading = first_line(text)
        if not heading.startswith("#"):
            path_failures.append({"category": "missing_markdown_heading", "path": rel, "heading": heading})
        if path.name.endswith("-no-publication.md") and not any(phrase in lower for phrase in NO_PUBLICATION_PHRASES):
            path_failures.append({"category": "no_publication_filename_without_textual_no_publication_marker", "path": rel})
        if "publication_authorized" in lower and "publication_authorized=false" not in lower:
            path_failures.append({"category": "decision_note_contains_publication_authorized_token", "path": rel})
        for subject in SUBJECT_RE.findall(text):
            subject_count += 1
            if not (root / subject).exists():
                path_failures.append({"category": "subject_path_missing", "path": rel, "subject": subject})
        revision_failures = check_revision_note(rel, text, release)
        if revision_failures:
            path_failures.extend(revision_failures)
        if REVISION_RE.search(text):
            revision_note_count += 1
        rows.append({
            "path": rel,
            "decision_id": stem,
            "status": "pass" if not path_failures else "fail",
            "heading": heading,
            "subject_paths": SUBJECT_RE.findall(text),
            "revision": REVISION_RE.search(text).group(1) if REVISION_RE.search(text) else "",
            "bundle": BUNDLE_RE.search(text).group(1) if BUNDLE_RE.search(text) else "",
            "failures": path_failures,
        })
        failures.extend(path_failures)

    direct_paths = [p.relative_to(root).as_posix() for p in paths]
    index_paths = [str(item.get("path", "")) for item in decision_index.get("decisions", []) if isinstance(item, dict)]
    index_path_set = set(index_paths)
    direct_path_set = set(direct_paths)
    latest_direct = direct_paths[-1] if direct_paths else ""
    index_latest = str(decision_index.get("latest_decision", ""))
    latest_json_path = str(latest_json.get("path", ""))

    if decision_index.get("decision_count") != len(paths):
        failures.append({"category": "decision_index_count_mismatch", "index_count": decision_index.get("decision_count"), "actual_count": len(paths)})
    missing_from_index = sorted(direct_path_set - index_path_set)
    extra_in_index = sorted(index_path_set - direct_path_set)
    if missing_from_index:
        failures.append({"category": "decision_notes_missing_from_index", "paths": missing_from_index[:50], "count": len(missing_from_index)})
    if extra_in_index:
        failures.append({"category": "decision_index_paths_missing_on_disk", "paths": extra_in_index[:50], "count": len(extra_in_index)})
    if latest_direct != index_latest or latest_direct != latest_json_path:
        failures.append({"category": "latest_decision_pointer_mismatch", "latest_direct": latest_direct, "decision_index_latest": index_latest, "latest_json_path": latest_json_path})

    latest_semantic_fields = ["subject", "decision", "state_before", "state_after", "reason", "follow_up_needed"]
    latest_missing_semantic_fields = [
        field for field in latest_semantic_fields
        if not str(latest_json.get(field, "")).strip()
    ]
    if latest_missing_semantic_fields:
        failures.append({
            "category": "latest_decision_missing_semantic_fields",
            "latest_decision": latest_json_path,
            "missing_fields": latest_missing_semantic_fields,
            "rule": "the newest compact decision surface must explain subject, decision, state transition, reason, and follow-up without requiring prose-only recovery",
        })

    action_counts = decision_index.get("publication_action_counts", {}) if isinstance(decision_index.get("publication_action_counts"), dict) else {}
    indexed_actions_total = sum(int(value) for value in action_counts.values() if isinstance(value, int))
    allowed_actions_total = int(action_counts.get("none", 0)) + int(action_counts.get("publish", 0))
    if indexed_actions_total != len(paths) or allowed_actions_total != len(paths):
        failures.append({"category": "decision_index_publication_action_not_accounted_for", "publication_action_counts": action_counts, "decision_count": len(paths), "allowed_actions": ["none", "publish"]})

    summary = {
        "checks_failed": len(failures),
        "decision_note_count": len(paths),
        "decision_index_count": decision_index.get("decision_count"),
        "revision_note_count": revision_note_count,
        "subject_path_count": subject_count,
        "subject_path_missing_count": sum(1 for row in failures if row.get("category") == "subject_path_missing"),
        "latest_decision": latest_direct,
        "publication_action_counts": action_counts,
    }
    return {
        "status": "pass" if not failures else "fail",
        "generated_for_revision": release["revision"],
        "checked_bundle": release["bundle"],
        "publication_authorized": False,
        "decision_directory": "release_queue/decisions",
        "decision_index": "release_queue/DECISION_INDEX.json",
        "latest_decision": "release_queue/LATEST_DECISION.json",
        "decision_rows": rows,
        "failures": failures[:100],
        "summary": summary,
        "fail_closed_rule": "If a decision note is structurally ambiguous, absent from the decision index, missing its subject path, or carries an unaccounted-for publication action, default to no further publication and repair the decision ledger before relying on queue history.",
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
