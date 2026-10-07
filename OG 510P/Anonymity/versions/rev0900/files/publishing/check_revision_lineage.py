#!/usr/bin/env python3
"""Check explicit delivered-predecessor lineage for the current archive."""

from __future__ import annotations

import argparse, json, pathlib, re, sys
from typing import Any

SHA_RE = re.compile(r"^[0-9a-f]{64}$")
REV_RE = re.compile(r"^rev(\d{4})$")

def load(path: pathlib.Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))

def revnum(s: str) -> int:
    m = REV_RE.match(str(s))
    return int(m.group(1)) if m else -1

def check(root: pathlib.Path) -> dict[str, Any]:
    release = load(root / "RELEASE_MANIFEST.json")
    receipt = load(root / "REVISION_RECEIPT.json")
    index = load(root / "ARCHIVE_INDEX.json")
    queue = load(root / "release_queue/QUEUE_INDEX.json")
    heads = load(root / "published/citation_heads.json")
    lineage = load(root / "REVISION_LINEAGE.json")
    version = (root / "VERSION").read_text(encoding="utf-8").strip()
    failures: list[dict[str, Any]] = []

    current = lineage.get("current", {}) if isinstance(lineage.get("current"), dict) else {}
    pred = lineage.get("predecessor", {}) if isinstance(lineage.get("predecessor"), dict) else {}
    revisions = index.get("revisions", []) if isinstance(index.get("revisions"), list) else []
    first = revisions[0] if revisions else {}
    second = revisions[1] if len(revisions) > 1 else {}
    receipt_rev = f"rev{int(receipt.get('revision', -1)):04d}" if isinstance(receipt.get("revision"), int) else ""

    if lineage.get("publication_authorized") is not False:
        failures.append({"category":"lineage_publication_authorized_not_false"})
    if lineage.get("generated_for_revision") != release["revision"] or lineage.get("checked_bundle") != release["bundle"]:
        failures.append({"category":"lineage_release_binding_mismatch"})
    if current.get("revision") != release["revision"] or current.get("bundle") != release["bundle"] or current.get("timestamp") != release["timestamp"]:
        failures.append({"category":"current_node_mismatch", "current": current, "release": release})
    if version != release["revision"] or receipt_rev != release["revision"]:
        failures.append({"category":"version_or_receipt_mismatch", "version": version, "receipt": receipt_rev, "release": release["revision"]})
    if index.get("latest_revision") != release["revision"] or first.get("revision") != release["revision"] or first.get("bundle") != release["bundle"]:
        failures.append({"category":"archive_index_current_entry_mismatch", "first": first})
    pred_rev = str(pred.get("revision", ""))
    if revnum(release["revision"]) != revnum(pred_rev) + 1:
        failures.append({"category":"predecessor_not_immediate", "current": release["revision"], "predecessor": pred_rev})
    if second.get("revision") != pred_rev or second.get("bundle") != pred.get("bundle"):
        failures.append({"category":"archive_index_predecessor_entry_mismatch", "second": second, "predecessor": pred})
    if not SHA_RE.match(str(pred.get("sha256", ""))):
        failures.append({"category":"predecessor_sha256_missing_or_malformed"})
    expected_queue = lineage.get("queue_posture_after_revision", {}) if isinstance(lineage.get("queue_posture_after_revision"), dict) else {}
    actual_queue = {k: queue.get("summary", {}).get(k, 0) for k in ["candidate", "published_ready", "hold", "published"]}
    if expected_queue != actual_queue:
        failures.append({"category":"queue_posture_mismatch", "expected": expected_queue, "actual": actual_queue})
    transition = lineage.get("publication_transition", {}) if isinstance(lineage.get("publication_transition"), dict) else {}
    new_heads = heads.get("summary", {}).get("new_post_policy_anonymity_head_count", 0)
    receipt_action = str(receipt.get("publication_action", "none"))
    if transition.get("publication_action") != receipt_action or transition.get("published_boundary_expected_new_heads") != new_heads:
        failures.append({"category":"publication_transition_mismatch", "transition": transition, "receipt_action": receipt_action, "new_heads": new_heads})

    return {
        "status": "pass" if not failures else "fail",
        "generated_for_revision": release["revision"],
        "checked_bundle": release["bundle"],
        "publication_authorized": False,
        "lineage_path": "REVISION_LINEAGE.json",
        "current_revision": release["revision"],
        "predecessor_revision": pred_rev,
        "predecessor_bundle": pred.get("bundle"),
        "predecessor_sha256": pred.get("sha256"),
        "summary": {
            "checks_failed": len(failures),
            "current_revision_number": revnum(release["revision"]),
            "predecessor_revision_number": revnum(pred_rev),
            "immediate_predecessor": revnum(release["revision"]) == revnum(pred_rev) + 1,
            "queue_candidate": actual_queue.get("candidate"),
            "queue_published_ready": actual_queue.get("published_ready"),
            "queue_hold": actual_queue.get("hold"),
            "queue_published": actual_queue.get("published"),
            "new_post_policy_anonymity_head_count": new_heads,
        },
        "failures": failures[:50],
        "fail_closed_rule": "If revision lineage fails, do not treat the archive as the coherent next version.",
    }

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--write-report", default="")
    args = ap.parse_args()
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
