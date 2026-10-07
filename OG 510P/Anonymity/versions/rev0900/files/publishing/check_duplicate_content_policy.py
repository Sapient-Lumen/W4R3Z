#!/usr/bin/env python3
"""Fail closed on unexpected duplicate file contents.

Exact content duplicates are sometimes intentional evidence bindings.  This
report requires every duplicate SHA-256 group to be explicitly allowlisted so a
future accidental frozen source, copied report, or leaked build product cannot be
silently normalized by the manifest alone.
"""

from __future__ import annotations

import argparse
import collections
import hashlib
import json
import pathlib
import sys
from typing import Any

ALLOWED_DUPLICATE_GROUPS = [
    {
        "reason": "published Certified Menus preserves source, frozen source, and public source copy as one receipt-bound byte identity",
        "paths": [
            "series/certified_series/paperA_certified_menus_anonymous_dht/paper.tex",
            "release_queue/freeze_packets/2026.05.21-certified-menus-for-anonymous-dht-lookups/FROZEN_SOURCE.tex",
            "published/2026-06-16_certified_menus_for_anonymous_dht_lookups/paper.tex",
        ],
    },
    {
        "reason": "published Certified Menus keeps the public compile-witness snapshot identical to the freeze-packet snapshot",
        "paths": [
            "release_queue/freeze_packets/2026.05.21-certified-menus-for-anonymous-dht-lookups/FREEZE_COMPILE_WITNESS.snapshot.json",
            "published/2026-06-16_certified_menus_for_anonymous_dht_lookups/FREEZE_COMPILE_WITNESS.snapshot.json",
        ],
    },
    {
        "reason": "published Routing-Signature Compression preserves source, frozen source, and public source copy as one receipt-bound byte identity",
        "paths": [
            "series/certified_series/paperB_routing_signature_compression/paper.tex",
            "release_queue/freeze_packets/2026.06.16-routing-signature-compression-for-many-testing-safe-anonymous-dht-tuning/FROZEN_SOURCE.tex",
            "published/2026-06-16_routing_signature_compression_for_many_testing_safe_anonymous_dht_tuning/paper.tex",
        ],
    },
    {
        "reason": "published Routing-Signature Compression keeps the public compile-witness snapshot identical to the freeze-packet snapshot",
        "paths": [
            "release_queue/freeze_packets/2026.06.16-routing-signature-compression-for-many-testing-safe-anonymous-dht-tuning/FREEZE_COMPILE_WITNESS.snapshot.json",
            "published/2026-06-16_routing_signature_compression_for_many_testing_safe_anonymous_dht_tuning/FREEZE_COMPILE_WITNESS.snapshot.json",
        ],
    },
    {
        "reason": "published Congestion-EQ preserves source, frozen source, and public source copy as one receipt-bound byte identity",
        "paths": [
            "series/congestion_series/paper1_congestion_eq/paper.tex",
            "release_queue/freeze_packets/2026.06.16-congestion-eq/FROZEN_SOURCE.tex",
            "published/2026-06-16_congestion_eq/paper.tex",
        ],
    },
    {
        "reason": "published Congestion-EQ keeps the public compile-witness snapshot identical to the freeze-packet snapshot",
        "paths": [
            "release_queue/freeze_packets/2026.06.16-congestion-eq/FREEZE_COMPILE_WITNESS.snapshot.json",
            "published/2026-06-16_congestion_eq/FREEZE_COMPILE_WITNESS.snapshot.json",
        ],
    },
    {
        "reason": "published PSC-Q preserves source, frozen source, and public source copy as one receipt-bound byte identity",
        "paths": [
            "series/congestion_series/paper2_psc_q/paper.tex",
            "release_queue/freeze_packets/2026.06.16-psc-q/FROZEN_SOURCE.tex",
            "published/2026-06-16_psc_q/paper.tex",
        ],
    },
    {
        "reason": "published PSC-Q keeps the public compile-witness snapshot identical to the freeze-packet snapshot",
        "paths": [
            "release_queue/freeze_packets/2026.06.16-psc-q/FREEZE_COMPILE_WITNESS.snapshot.json",
            "published/2026-06-16_psc_q/FREEZE_COMPILE_WITNESS.snapshot.json",
        ],
    },
    {
        "reason": "published W-Congestion-EQ preserves source, frozen source, and public source copy as one receipt-bound byte identity",
        "paths": [
            "series/congestion_series/paper3_w_congestion_eq/paper.tex",
            "release_queue/freeze_packets/2026.06.16-w-congestion-eq/FROZEN_SOURCE.tex",
            "published/2026-06-16_w_congestion_eq/paper.tex",
        ],
    },
    {
        "reason": "published W-Congestion-EQ keeps the public compile-witness snapshot identical to the freeze-packet snapshot",
        "paths": [
            "release_queue/freeze_packets/2026.06.16-w-congestion-eq/FREEZE_COMPILE_WITNESS.snapshot.json",
            "published/2026-06-16_w_congestion_eq/FREEZE_COMPILE_WITNESS.snapshot.json",
        ],
    },
    {
        "reason": "published Calibration Recipes preserves source, frozen source, and public source copy as one receipt-bound byte identity",
        "paths": [
            "series/evaluation_series/paper3_calibration_recipes_anondht/paper.tex",
            "release_queue/freeze_packets/2026.06.16-calibration-recipes-for-anonymous-dht-deployments/FROZEN_SOURCE.tex",
            "published/2026-06-16_calibration_recipes_for_anonymous_dht_deployments/paper.tex",
        ],
    },
    {
        "reason": "published Calibration Recipes keeps the public compile-witness snapshot identical to the freeze-packet snapshot",
        "paths": [
            "release_queue/freeze_packets/2026.06.16-calibration-recipes-for-anonymous-dht-deployments/FREEZE_COMPILE_WITNESS.snapshot.json",
            "published/2026-06-16_calibration_recipes_for_anonymous_dht_deployments/FREEZE_COMPILE_WITNESS.snapshot.json",
        ],
    },
    {
        "reason": "published State-Dependent Anonymity preserves source, frozen source, and public source copy as one receipt-bound byte identity",
        "paths": [
            "series/anondht_state_series/paper1_state_dependent_anonymity/paper.tex",
            "release_queue/freeze_packets/2026.06.16-state-dependent-anonymity/FROZEN_SOURCE.tex",
            "published/2026-06-16_state_dependent_anonymity/paper.tex",
        ],
    },
    {
        "reason": "published State-Dependent Anonymity keeps the public compile-witness snapshot identical to the freeze-packet snapshot",
        "paths": [
            "release_queue/freeze_packets/2026.06.16-state-dependent-anonymity/FREEZE_COMPILE_WITNESS.snapshot.json",
            "published/2026-06-16_state_dependent_anonymity/FREEZE_COMPILE_WITNESS.snapshot.json",
        ],
    },

]

def load_json(path: pathlib.Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def check(root: pathlib.Path) -> dict[str, Any]:
    release = load_json(root / "RELEASE_MANIFEST.json")
    allowed_sets = {tuple(sorted(group["paths"])): group["reason"] for group in ALLOWED_DUPLICATE_GROUPS}
    missing_allowlist_paths = sorted(path for group in ALLOWED_DUPLICATE_GROUPS for path in group["paths"] if not (root / path).exists())

    by_digest: dict[str, list[str]] = collections.defaultdict(list)
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(root).as_posix()
        by_digest[sha256_file(path)].append(rel)

    duplicate_rows: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    for digest, paths in sorted(by_digest.items()):
        if len(paths) < 2:
            continue
        key = tuple(sorted(paths))
        reason = allowed_sets.get(key)
        row_failures: list[dict[str, Any]] = []
        if reason is None:
            row_failures.append({"category": "duplicate_group_not_allowlisted"})
        row = {"sha256": digest, "paths": sorted(paths), "status": "pass" if not row_failures else "fail", "allowlist_reason": reason or "", "failures": row_failures}
        duplicate_rows.append(row)
        if row_failures:
            failures.append(row)

    for path in missing_allowlist_paths:
        failures.append({"sha256": "", "paths": [path], "status": "fail", "failures": [{"category": "allowlist_path_missing"}]})

    return {
        "status": "pass" if not failures else "fail",
        "generated_for_revision": release["revision"],
        "checked_bundle": release["bundle"],
        "publication_authorized": False,
        "allowlisted_duplicate_groups": ALLOWED_DUPLICATE_GROUPS,
        "duplicate_groups": duplicate_rows,
        "failures": failures[:50],
        "summary": {
            "checks_failed": len(failures),
            "file_count": sum(len(paths) for paths in by_digest.values()),
            "duplicate_group_count": len(duplicate_rows),
            "duplicate_file_count": sum(len(row["paths"]) for row in duplicate_rows),
            "allowlisted_duplicate_group_count": sum(1 for row in duplicate_rows if row["status"] == "pass"),
            "unexpected_duplicate_group_count": sum(1 for row in duplicate_rows if row["status"] != "pass"),
            "missing_allowlist_path_count": len(missing_allowlist_paths),
        },
        "fail_closed_rule": "If duplicate file bytes appear outside the explicit freeze-evidence allowlist, default to no publication and classify or remove the duplicate before shipping.",
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
