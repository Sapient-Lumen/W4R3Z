#!/usr/bin/env python3
"""Check JSON/Markdown archive-index parity and current-revision narrative binding."""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys
from typing import Any

REV_RE = re.compile(r"^rev\d{4}$")
LATEST_RE = re.compile(r"Latest revision:\s*`([^`]+)`")
HEADING_RE = re.compile(r"^##\s+(rev\d{4})\s+—\s+(.+?)\s*$", re.MULTILINE)
BUNDLE_RE = re.compile(r"(?:-\s*)?Bundle:\s*`([^`]+)`")
SUMMARY_RE = re.compile(r"-\s*Summary:\s*(.+)")
ACTION_RE = re.compile(r"-\s*Publication action:\s*(.+)")


def load(path: pathlib.Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def slug_words(slug: str) -> set[str]:
    stop = {"and", "the", "for", "with", "gate", "guard", "audit", "fixedpoint", "fixed", "point", "release"}
    return {part for part in re.split(r"[^a-z0-9]+", slug.lower()) if len(part) >= 4 and part not in stop}


def section_map(md: str) -> dict[str, str]:
    headings = list(HEADING_RE.finditer(md))
    sections: dict[str, str] = {}
    for i, match in enumerate(headings):
        start = match.start()
        end = headings[i + 1].start() if i + 1 < len(headings) else len(md)
        sections[match.group(1)] = md[start:end]
    return sections


def first_line_match(pattern: re.Pattern[str], text: str) -> str:
    match = pattern.search(text)
    return match.group(1).strip() if match else ""


def check(root: pathlib.Path) -> dict[str, Any]:
    release = load(root / "RELEASE_MANIFEST.json")
    index = load(root / "ARCHIVE_INDEX.json")
    receipt = load(root / "REVISION_RECEIPT.json") if (root / "REVISION_RECEIPT.json").exists() else {}
    receipt_action = str(receipt.get("publication_action", "none")).strip().lower()
    md_path = root / "ARCHIVE_INDEX.md"
    md = md_path.read_text(encoding="utf-8", errors="replace") if md_path.exists() else ""
    failures: list[dict[str, Any]] = []
    checks: list[dict[str, Any]] = []

    def record(name: str, ok: bool, details: str, failure: dict[str, Any] | None = None) -> None:
        checks.append({"name": name, "status": "pass" if ok else "fail", "details": details})
        if not ok:
            row = {"category": name}
            if failure:
                row.update(failure)
            failures.append(row)

    latest_md = first_line_match(LATEST_RE, md)
    latest_json = str(index.get("latest_revision", ""))
    revisions = index.get("revisions", []) if isinstance(index.get("revisions"), list) else []
    first = revisions[0] if revisions and isinstance(revisions[0], dict) else {}
    sections = section_map(md)

    record(
        "latest_revision_line_matches_json_and_release",
        latest_md == latest_json == release.get("revision") and bool(REV_RE.match(latest_md)),
        f"markdown_latest={latest_md!r} json_latest={latest_json!r} release={release.get('revision')!r}",
        {"markdown_latest": latest_md, "json_latest": latest_json, "release_revision": release.get("revision")},
    )
    record(
        "json_current_entry_matches_release_manifest",
        first.get("revision") == release.get("revision") and first.get("bundle") == release.get("bundle"),
        f"first_revision={first.get('revision')} first_bundle={first.get('bundle')} release_bundle={release.get('bundle')}",
        {"first": first, "release": release},
    )

    current_section = sections.get(str(release.get("revision")), "")
    record(
        "markdown_current_section_present",
        bool(current_section),
        f"section_present={bool(current_section)} section_count={len(sections)}",
        {"missing_revision": release.get("revision")},
    )
    if current_section:
        md_bundle = first_line_match(BUNDLE_RE, current_section)
        md_summary = first_line_match(SUMMARY_RE, current_section)
        md_action = first_line_match(ACTION_RE, current_section).rstrip(".").lower()
        heading_line = current_section.splitlines()[0] if current_section.splitlines() else ""
        record(
            "markdown_current_bundle_matches_json",
            md_bundle == release.get("bundle") == first.get("bundle"),
            f"markdown_bundle={md_bundle!r} release_bundle={release.get('bundle')!r}",
            {"markdown_bundle": md_bundle, "release_bundle": release.get("bundle")},
        )
        record(
            "markdown_current_summary_matches_json",
            md_summary == first.get("summary"),
            f"markdown_summary_len={len(md_summary)} json_summary_len={len(str(first.get('summary', '')))}",
            {"markdown_summary": md_summary, "json_summary": first.get("summary")},
        )
        allowed_md_actions = {"none", "no publication", "no publication; no queue movement"}
        if receipt_action == "publish":
            allowed_md_actions = {"publish", "published"}
        record(
            "markdown_current_action_matches_revision_receipt",
            md_action in allowed_md_actions,
            f"markdown_action={md_action!r} receipt_action={receipt_action!r}",
            {"markdown_action": md_action, "receipt_action": receipt_action},
        )
        heading_has_timestamp_or_date = release.get("timestamp", "") in heading_line or release.get("timestamp", "")[:10].replace(".", "-") in heading_line
        record(
            "markdown_current_heading_is_timestamp_bound",
            heading_has_timestamp_or_date,
            f"heading={heading_line!r} release_timestamp={release.get('timestamp')}",
            {"heading": heading_line, "timestamp": release.get("timestamp")},
        )

    checked_entries: list[dict[str, str]] = []
    for entry in revisions[:5]:
        if not isinstance(entry, dict):
            continue
        rev = str(entry.get("revision", ""))
        sec = sections.get(rev, "")
        bundle = first_line_match(BUNDLE_RE, sec)
        summary = first_line_match(SUMMARY_RE, sec)
        ok = bool(sec) and bundle == entry.get("bundle") and summary == entry.get("summary")
        checked_entries.append({"revision": rev, "status": "pass" if ok else "fail"})
        if not ok:
            failures.append({"category": "recent_revision_markdown_json_mismatch", "revision": rev, "markdown_bundle": bundle, "json_bundle": entry.get("bundle"), "markdown_summary": summary, "json_summary": entry.get("summary")})
    checks.append({"name": "recent_revision_sections_match_json", "status": "pass" if all(row["status"] == "pass" for row in checked_entries) else "fail", "details": f"checked={checked_entries}"})

    notice = (root / "NOTICE").read_text(encoding="utf-8", errors="replace") if (root / "NOTICE").exists() else ""
    codemeta = load(root / "codemeta.json") if (root / "codemeta.json").exists() else {}
    words = slug_words(str(release.get("slug", "")))
    notice_words = {word for word in words if word in notice.lower()}
    codemeta_words = {word for word in words if word in str(codemeta.get("description", "")).lower()}
    record(
        "notice_and_codemeta_descriptions_bind_current_focus",
        release.get("revision") in notice and len(notice_words) >= min(2, len(words)) and release.get("revision") == codemeta.get("version") and len(codemeta_words) >= min(2, len(words)),
        f"slug_words={sorted(words)} notice_words={sorted(notice_words)} codemeta_words={sorted(codemeta_words)} codemeta_version={codemeta.get('version')}",
        {"slug_words": sorted(words), "notice_words": sorted(notice_words), "codemeta_words": sorted(codemeta_words)},
    )

    return {
        "status": "pass" if not failures else "fail",
        "generated_for_revision": release["revision"],
        "checked_bundle": release["bundle"],
        "publication_authorized": False,
        "archive_index_json": "ARCHIVE_INDEX.json",
        "archive_index_markdown": "ARCHIVE_INDEX.md",
        "recent_revision_rows_checked": checked_entries,
        "checks": checks,
        "failures": failures[:50],
        "summary": {
            "checks_passed": sum(1 for row in checks if row["status"] == "pass"),
            "checks_failed": sum(1 for row in checks if row["status"] != "pass"),
            "recent_revision_count_checked": len(checked_entries),
            "markdown_section_count": len(sections),
        },
        "fail_closed_rule": "If archive-index Markdown/JSON, revision-receipt action, or current-focus prose drifts, default to the guarded release posture and repair the operator-facing narrative surfaces.",
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
