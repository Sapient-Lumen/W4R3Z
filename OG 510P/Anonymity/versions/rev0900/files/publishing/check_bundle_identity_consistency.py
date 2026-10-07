#!/usr/bin/env python3
"""Check bundle identity consistency across root control surfaces.

This is narrower than the archive-coherence check: it focuses only on the
revision/timestamp/bundle stem contract that future operators use to identify a
specific delivered datacube.  It fails closed if any of the identity carriers
name a different revision, timestamp, stem, bundle, or no-publication posture.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys
from typing import Any

BUNDLE_RE = re.compile(r"^Anonymity-(rev\d{4})-(\d{4}\.\d{2}\.\d{2}\.\d{2}\.\d{2})-([a-z0-9][a-z0-9-]*[a-z0-9])\.zip$")
REV_RE = re.compile(r"^rev\d{4}$")


def load_json(path: pathlib.Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def record(checks: list[dict[str, Any]], name: str, ok: bool, details: str) -> None:
    checks.append({"name": name, "status": "pass" if ok else "fail", "details": details})


def check(root: pathlib.Path) -> dict[str, Any]:
    release = load_json(root / "RELEASE_MANIFEST.json")
    receipt = load_json(root / "REVISION_RECEIPT.json")
    lineage = load_json(root / "REVISION_LINEAGE.json")
    context = load_json(root / "CONTEXT_PACK.json")
    archive_index = load_json(root / "ARCHIVE_INDEX.json")
    queue_index = load_json(root / "release_queue/QUEUE_INDEX.json")
    latest_decision = load_json(root / "release_queue/LATEST_DECISION.json")
    version_text = (root / "VERSION").read_text(encoding="utf-8").strip()

    revision = str(release.get("revision", ""))
    timestamp = str(release.get("timestamp", ""))
    slug = str(release.get("slug", ""))
    bundle = str(release.get("bundle", ""))
    artifact_stem = str(receipt.get("artifact_stem", ""))
    expected_stem = f"Anonymity-{revision}-{timestamp}-{slug}"
    expected_bundle = expected_stem + ".zip"
    receipt_revision = f"rev{int(receipt.get('revision', -1)):04d}" if isinstance(receipt.get("revision"), int) else ""
    receipt_timestamp = str(receipt.get("timestamp_local", "")).replace("-", ".").replace(" ", ".").replace(":", ".")
    bundle_match = BUNDLE_RE.match(bundle)

    checks: list[dict[str, Any]] = []
    record(checks, "release_manifest_bundle_matches_contract", bool(bundle_match) and bundle_match.groups() == (revision, timestamp, slug), f"bundle={bundle} revision={revision} timestamp={timestamp} slug={slug}")
    record(checks, "version_receipt_release_match", REV_RE.match(version_text) is not None and version_text == revision == receipt_revision, f"VERSION={version_text} release={revision} receipt={receipt_revision}")
    record(checks, "artifact_stem_and_bundle_match_manifest", artifact_stem == expected_stem and bundle == expected_bundle, f"artifact_stem={artifact_stem} expected={expected_stem} bundle={bundle} expected_bundle={expected_bundle}")
    record(checks, "receipt_timestamp_matches_manifest", receipt_timestamp == timestamp, f"receipt_timestamp={receipt_timestamp} manifest_timestamp={timestamp}")

    current = lineage.get("current", {}) if isinstance(lineage.get("current"), dict) else {}
    predecessor = lineage.get("predecessor", {}) if isinstance(lineage.get("predecessor"), dict) else {}
    receipt_action = str(receipt.get("publication_action", "none"))
    lineage_transition = lineage.get("publication_transition", {}) if isinstance(lineage.get("publication_transition"), dict) else {}
    lineage_ok = (
        lineage.get("generated_for_revision") == revision
        and lineage.get("checked_bundle") == bundle
        and lineage.get("publication_authorized") is False
        and current.get("revision") == revision
        and current.get("timestamp") == timestamp
        and current.get("bundle") == bundle
        and int(current.get("revision_number", -1)) == int(revision.removeprefix("rev"))
        and int(predecessor.get("revision_number", -1)) == int(revision.removeprefix("rev")) - 1
        and lineage_transition.get("publication_action") == receipt_action
        and isinstance(lineage_transition.get("queue_moved"), bool)
    )
    record(checks, "revision_lineage_current_and_predecessor_match", lineage_ok, f"lineage_current={current} predecessor={predecessor} transition={lineage.get('publication_transition')} receipt_action={receipt_action}")

    index_first = archive_index.get("revisions", [{}])[0] if isinstance(archive_index.get("revisions"), list) and archive_index.get("revisions") else {}
    index_ok = archive_index.get("latest_revision") == revision and index_first.get("revision") == revision and index_first.get("bundle") == bundle and index_first.get("publication_action", "none") in {receipt_action, ""}
    record(checks, "archive_index_latest_entry_matches_bundle", index_ok, f"latest={archive_index.get('latest_revision')} first={index_first}")

    context_ok = context.get("revision") == revision and context.get("bundle") == bundle and context.get("project") == release.get("project")
    record(checks, "context_pack_identity_matches_manifest", context_ok, f"context_revision={context.get('revision')} context_bundle={context.get('bundle')}")

    queue_ok = queue_index.get("generated_for_revision") == revision and latest_decision.get("generated_for_revision") == revision and bundle in str(latest_decision.get("summary", ""))
    record(checks, "queue_surfaces_name_current_revision_and_bundle", queue_ok, f"queue_revision={queue_index.get('generated_for_revision')} latest_revision={latest_decision.get('generated_for_revision')} latest_path={latest_decision.get('path')}")

    posture = receipt.get("queue_posture_after_revision", {})
    queue_summary = queue_index.get("summary", {})
    posture_ok = posture == {
        "candidate": queue_summary.get("candidate"),
        "published_ready": queue_summary.get("published_ready"),
        "hold": queue_summary.get("hold"),
        "published": queue_summary.get("published", 0),
    }
    record(checks, "receipt_queue_posture_matches_queue_index", posture_ok, f"receipt_posture={posture} queue_summary={queue_summary}")

    publication_action_ok = (
        (receipt_action == "none" and latest_decision.get("publication_action") == "none" and "no-publication" in str(latest_decision.get("decision_id", "")))
        or (receipt_action == "publish" and latest_decision.get("publication_action") == "publish" and "publish" in str(latest_decision.get("decision_id", "")))
    )
    record(checks, "publication_posture_is_explicit", publication_action_ok, f"receipt_action={receipt_action} latest_action={latest_decision.get('publication_action')} decision_id={latest_decision.get('decision_id')}")

    failures = [row for row in checks if row["status"] != "pass"]
    return {
        "status": "pass" if not failures else "fail",
        "generated_for_revision": revision,
        "checked_bundle": bundle,
        "publication_authorized": False,
        "identity_contract": {
            "revision": revision,
            "timestamp": timestamp,
            "slug": slug,
            "artifact_stem": expected_stem,
            "bundle": expected_bundle,
        },
        "checks": checks,
        "failures": failures[:50],
        "summary": {
            "checks_passed": len(checks) - len(failures),
            "checks_failed": len(failures),
            "identity_surface_count": 7,
            "publication_authorized": False,
        },
        "fail_closed_rule": "If the delivered bundle identity disagrees across root control surfaces, default to no publication and repair the identity carriers before trusting reports or packaging.",
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
