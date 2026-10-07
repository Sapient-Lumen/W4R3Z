#!/usr/bin/env python3
"""Validate that planned publication targets are portable before materialization.

Path-portability checks protect files that already exist.  The release lane also
carries *prospective* published paths in plans, evidence packs, freeze packets,
blocker ledgers, and readiness reports.  Those strings must be portable too, or
publication can appear ready until the helper materializes a path that immediately
breaks the archive.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys
from typing import Any

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import publication_target as pt  # noqa: E402

TARGET_KEYS = {"target", "prospective_target", "published_path"}
NAME_KEYS = {"prospective_published_name", "published_name"}
SCAN_PATHS = [
    "release_queue/NEXT_RELEASE_FREEZE_PLAN.json",
    "release_queue/FREEZE_COMPILE_WITNESS.json",
    "release_queue/FREEZE_PACKET_REGISTRY.json",
    "release_queue/EVIDENCE_PACK_REGISTRY.json",
    "release_queue/PUBLICATION_BLOCKERS.json",
    "reports/release_readiness_audit.json",
    "reports/publication_rehearsal.json",
    "reports/publication_blockers.json",
]


def load_json(path: pathlib.Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def iter_json_values(obj: Any, trail: tuple[str, ...] = ()) -> list[tuple[tuple[str, ...], str]]:
    rows: list[tuple[tuple[str, ...], str]] = []
    if isinstance(obj, dict):
        for key, value in obj.items():
            new_trail = (*trail, str(key))
            if key in TARGET_KEYS and isinstance(value, str) and value:
                rows.append((new_trail, value))
            elif key in NAME_KEYS and isinstance(value, str) and value:
                rows.append((new_trail, value))
            rows.extend(iter_json_values(value, new_trail))
    elif isinstance(obj, list):
        for idx, value in enumerate(obj):
            rows.extend(iter_json_values(value, (*trail, str(idx))))
    return rows


def classify_value(key: str, value: str) -> dict[str, Any]:
    if key in TARGET_KEYS:
        ok = pt.is_portable_published_path(value)
        return {
            "kind": "published_path",
            "value": value,
            "portable": ok,
            "reason": "portable_published_path" if ok else "must match published/YYYY-MM-DD_slug_title with no spaces, colons, traversal, or platform-reserved characters",
        }
    ok = pt.is_portable_published_dirname(value)
    return {
        "kind": "published_name",
        "value": value,
        "portable": ok,
        "reason": "portable_published_dirname" if ok else "must match YYYY-MM-DD_slug_title with no spaces, colons, or platform-reserved characters",
    }


def historical_publication_target_paths(root: pathlib.Path) -> dict[str, set[str]]:
    """Return published targets that are now historical evidence, keyed by target path.

    A completed publication leaves prospective target strings in the evidence pack,
    freeze packet, and registries that served as its receipt. Those strings should
    still be portability-checked, but existence of the published directory is no
    longer an error for the historical receipt-bound surfaces.
    """
    out: dict[str, set[str]] = {}
    published_root = root / "published"
    if not published_root.exists():
        return out
    for receipt_path in published_root.glob("*/PUBLICATION_RECEIPT.json"):
        try:
            receipt = load_json(receipt_path)
        except Exception:
            continue
        target = str(receipt.get("published_path", ""))
        if not target:
            continue
        paths = out.setdefault(target, set())
        paths.add("release_queue/FREEZE_PACKET_REGISTRY.json")
        paths.add("release_queue/EVIDENCE_PACK_REGISTRY.json")
        for key in ["evidence_pack_manifest", "freeze_packet_manifest", "compile_witness_snapshot", "published_compile_witness_snapshot"]:
            rel = str(receipt.get(key, ""))
            if rel:
                paths.add(rel)
        evidence_rel = str(receipt.get("evidence_pack_manifest", ""))
        evidence_path = root / evidence_rel if evidence_rel else None
        if evidence_path and evidence_path.exists():
            try:
                evidence = load_json(evidence_path)
                for row in evidence.get("pack_paths", []):
                    if isinstance(row, dict) and row.get("path"):
                        paths.add(str(row["path"]))
            except Exception:
                pass
        freeze_rel = str(receipt.get("freeze_packet_manifest", ""))
        freeze_path = root / freeze_rel if freeze_rel else None
        if freeze_path and freeze_path.exists():
            try:
                freeze = load_json(freeze_path)
                for row in freeze.get("packet_paths", []):
                    if isinstance(row, dict) and row.get("path"):
                        paths.add(str(row["path"]))
            except Exception:
                pass
    return out


def check(root: pathlib.Path) -> dict[str, Any]:
    release = load_json(root / "RELEASE_MANIFEST.json")
    historical_targets = historical_publication_target_paths(root)
    rows: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []

    paths = [root / rel for rel in SCAN_PATHS]
    paths.extend(sorted((root / "release_queue" / "evidence_packs").glob("*/release_preflight_static.json")))
    paths.extend(sorted((root / "release_queue" / "freeze_packets").glob("*/FREEZE_PACKET_MANIFEST.json")))
    paths.extend(sorted((root / "release_queue" / "freeze_packets").glob("*/FREEZE_COMPILE_WITNESS.snapshot.json")))

    seen: set[str] = set()
    for path in paths:
        path_key = str(path)
        if not path.exists() or path_key in seen:
            continue
        seen.add(path_key)
        rel = path.relative_to(root).as_posix()
        try:
            obj = load_json(path)
        except Exception as exc:
            failures.append({"category": "json_load_failed", "path": rel, "error": str(exc)})
            continue
        for trail, value in iter_json_values(obj):
            key = trail[-1]
            # Avoid interpreting generic source/output paths as publication targets.
            if key in TARGET_KEYS and not value.startswith("published/"):
                continue
            classified = classify_value(key, value)
            row = {"path": rel, "json_pointer": "/" + "/".join(trail), **classified}
            rows.append(row)
            if not classified["portable"]:
                failures.append({"category": "nonportable_publication_target", **row})
            if classified["kind"] == "published_path" and (root / value).exists():
                if value in historical_targets and rel in historical_targets[value]:
                    row["historical_published_target"] = True
                    row["publication_receipt_bound"] = True
                else:
                    failures.append({"category": "prospective_target_already_exists", **row})

    target_values = sorted({row["value"] for row in rows if row["kind"] == "published_path"})
    name_values = sorted({row["value"] for row in rows if row["kind"] == "published_name"})
    return {
        "status": "pass" if not failures else "fail",
        "generated_for_revision": release["revision"],
        "checked_bundle": release["bundle"],
        "publication_authorized": False,
        "checked_sources": sorted({row["path"] for row in rows}),
        "target_rows": rows,
        "failures": failures[:80],
        "summary": {
            "checks_failed": len(failures),
            "target_row_count": len(rows),
            "unique_published_path_count": len(target_values),
            "unique_published_name_count": len(name_values),
            "nonportable_count": sum(1 for f in failures if f.get("category") == "nonportable_publication_target"),
            "already_exists_count": sum(1 for f in failures if f.get("category") == "prospective_target_already_exists"),
            "unique_published_paths": target_values,
            "unique_published_names": name_values,
        },
        "fail_closed_rule": "If a prospective publication target is not portable, repair the target contract before executing the publication helper.",
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
    print(text, end="")
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
