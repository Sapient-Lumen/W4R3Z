#!/usr/bin/env python3
"""rev0060 patch-order permutation and series-order gate.

This helper treats the rev0059 split bundle patches as reviewer-facing patch
artifacts and verifies that the four archived-source filing-bundle patches per
lane are order-independent.  With --run-tests it applies all 24 bundle orders
per lane, checks final source-file hashes, and reruns fixed regressions on the
canonical and reverse orders.
"""
from __future__ import annotations

import argparse
import csv
import itertools
import json
import os
import shutil
import subprocess
import sys
# Keep verification helpers from polluting package hygiene checks with __pycache__ files.
sys.dont_write_bytecode = True
import tempfile
import zipfile
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Tuple

# Reuse rev0059's source extraction, test, patch, manifest, and hygiene helpers.
from probe_rev0059_patch_layer_attribution import (  # type: ignore
    BUNDLES,
    EXPECTED_SOURCE_SHA256,
    LANES,
    PACKET_TESTS,
    ROOT,
    apply_patch_file,
    extract_lane,
    manifest_errors,
    package_hygiene,
    run_packet_test,
    sha_path,
    source_identity,
    write_csv,
)

REV = "rev0060"
CANONICAL_ORDER = tuple(str(bundle["bundle"]) for bundle in BUNDLES)
REVERSE_ORDER = tuple(reversed(CANONICAL_ORDER))


def read_csv(rel: str) -> List[Dict[str, str]]:
    path = ROOT / rel
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def rev0059_patch_map() -> Dict[Tuple[str, str], Dict[str, str]]:
    rows = read_csv("data/rev0059_bundle_patch_manifest.csv")
    return {(row["lane"], row["bundle"]): row for row in rows}


def expected_final_hashes() -> Dict[str, Dict[str, str]]:
    rows = read_csv("data/rev0059_bundle_patch_file_hashes.csv")
    expected: Dict[str, Dict[str, str]] = {lane: {} for lane in LANES}
    for row in rows:
        expected[row["lane"]][row["file"]] = row["patched_sha256"]
    return expected


def touched_files() -> List[str]:
    files: List[str] = []
    for bundle in BUNDLES:
        for file_rel in bundle["files"]:  # type: ignore[index]
            if str(file_rel) not in files:
                files.append(str(file_rel))
    return files


def patch_cmd(checkout: Path, patch_rel: str, dry_run: bool = False) -> Dict[str, object]:
    cmd = ["patch", "--batch", "--forward"]
    if dry_run:
        cmd.append("--dry-run")
    cmd.extend(["-p0", "-i", str(ROOT / patch_rel)])
    proc = subprocess.run(cmd, cwd=checkout, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=45)
    lines = [line.strip() for line in proc.stdout.splitlines() if line.strip()]
    return {
        "rc": proc.returncode,
        "summary": " | ".join(lines[-8:]),
    }


def apply_order(checkout: Path, lane: str, order: Sequence[str], patch_map: Dict[Tuple[str, str], Dict[str, str]]) -> Tuple[bool, List[str]]:
    summaries: List[str] = []
    ok = True
    for index, bundle in enumerate(order, start=1):
        patch_rel = patch_map[(lane, bundle)]["patch"]
        result = patch_cmd(checkout, patch_rel, dry_run=False)
        summaries.append(f"{index}:{bundle}:rc={result['rc']}")
        if result["rc"] != 0:
            ok = False
            summaries.append(str(result.get("summary", "")))
            break
    return ok, summaries


def copy_minimal_tree(base: Path, checkout: Path, files: Sequence[str]) -> None:
    if checkout.exists():
        shutil.rmtree(checkout)
    for file_rel in files:
        src = base / file_rel
        dst = checkout / file_rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)


def run_permutation_gate(source_zip: Path, work_dir: Path) -> Tuple[List[Dict[str, object]], List[Dict[str, object]]]:
    patch_map = rev0059_patch_map()
    expected = expected_final_hashes()
    files = touched_files()
    perm_rows: List[Dict[str, object]] = []
    hash_rows: List[Dict[str, object]] = []
    orders = list(itertools.permutations(CANONICAL_ORDER))

    for lane in LANES:
        base = work_dir / "source" / lane
        extract_lane(source_zip, lane, base)
        for order_index, order in enumerate(orders, start=1):
            checkout = work_dir / "perm" / lane / f"order-{order_index:02d}"
            copy_minimal_tree(base, checkout, files)
            print(f"PERM {lane} {order_index:02d} {' > '.join(order)}", file=sys.stderr, flush=True)
            apply_ok, summaries = apply_order(checkout, lane, order, patch_map)
            hash_ok = True
            if apply_ok:
                for file_rel in files:
                    observed = sha_path(checkout / file_rel)
                    want = expected[lane].get(file_rel, "")
                    status = "pass" if observed == want else "fail"
                    if status != "pass":
                        hash_ok = False
                    hash_rows.append({
                        "lane": lane,
                        "order_index": order_index,
                        "order": ";".join(order),
                        "file": file_rel,
                        "expected_sha256": want,
                        "observed_sha256": observed,
                        "status": status,
                    })
            else:
                hash_ok = False
                for file_rel in files:
                    hash_rows.append({
                        "lane": lane,
                        "order_index": order_index,
                        "order": ";".join(order),
                        "file": file_rel,
                        "expected_sha256": expected[lane].get(file_rel, ""),
                        "observed_sha256": "patch-apply-failed",
                        "status": "fail",
                    })
            perm_rows.append({
                "lane": lane,
                "order_index": order_index,
                "order": ";".join(order),
                "patch_count": len(order),
                "apply_status": "pass" if apply_ok else "fail",
                "hash_status": "pass" if hash_ok else "fail",
                "status": "pass" if apply_ok and hash_ok else "fail",
                "apply_summary": " | ".join(summaries),
            })
    return perm_rows, hash_rows


def run_order_regressions(source_zip: Path, work_dir: Path, out_dir: Path) -> List[Dict[str, object]]:
    patch_map = rev0059_patch_map()
    rows: List[Dict[str, object]] = []
    orders = [("canonical-order", CANONICAL_ORDER), ("reverse-order", REVERSE_ORDER)]
    for lane in LANES:
        base = work_dir / "reg-source" / lane
        extract_lane(source_zip, lane, base)
        for scenario, order in orders:
            checkout = work_dir / "reg-work" / lane / scenario
            if checkout.exists():
                shutil.rmtree(checkout)
            shutil.copytree(base, checkout)
            apply_ok, summaries = apply_order(checkout, lane, order, patch_map)
            if not apply_ok:
                for packet in PACKET_TESTS:
                    rows.append({
                        "lane": lane,
                        "packet": packet,
                        "scenario": scenario,
                        "patches_applied": ";".join(order),
                        "runner": PACKET_TESTS[packet][1],
                        "env_kind": PACKET_TESTS[packet][2],
                        "expected_rc": "0",
                        "observed_rc": "patch-apply-error",
                        "status": "fail",
                        "summary": " | ".join(summaries),
                        "test": PACKET_TESTS[packet][0],
                        "output_file": "",
                    })
                continue
            for packet in PACKET_TESTS:
                print(f"REG {lane} {scenario} {packet}", file=sys.stderr, flush=True)
                row = run_packet_test(lane, checkout, packet, scenario, "0", order, out_dir)
                rows.append(row)
    return rows


def write_outputs(perm_rows: List[Dict[str, object]], hash_rows: List[Dict[str, object]], regression_rows: List[Dict[str, object]]) -> None:
    write_csv(ROOT / "data/rev0060_patch_order_permutation_matrix.csv", perm_rows, ["lane", "order_index", "order", "patch_count", "apply_status", "hash_status", "status", "apply_summary"])
    (ROOT / "data/rev0060_patch_order_permutation_matrix.json").write_text(json.dumps(perm_rows, indent=2), encoding="utf-8")

    write_csv(ROOT / "data/rev0060_patch_order_file_hash_matrix.csv", hash_rows, ["lane", "order_index", "order", "file", "expected_sha256", "observed_sha256", "status"])
    (ROOT / "data/rev0060_patch_order_file_hash_matrix.json").write_text(json.dumps(hash_rows, indent=2), encoding="utf-8")

    write_csv(ROOT / "data/rev0060_patch_order_regression_matrix.csv", regression_rows, ["lane", "packet", "scenario", "patches_applied", "runner", "env_kind", "expected_rc", "observed_rc", "status", "summary", "test", "output_file"])
    (ROOT / "data/rev0060_patch_order_regression_matrix.json").write_text(json.dumps(regression_rows, indent=2), encoding="utf-8")

    summary_rows = [
        {"metric": "source_bundle_used", "value": "yes"},
        {"metric": "source_zip_sha256", "value": EXPECTED_SOURCE_SHA256},
        {"metric": "bundle_patch_orders", "value": str(len(perm_rows))},
        {"metric": "bundle_patch_orders_pass", "value": str(sum(1 for r in perm_rows if r.get("status") == "pass"))},
        {"metric": "bundle_patch_order_file_hash_rows", "value": str(len(hash_rows))},
        {"metric": "bundle_patch_order_file_hash_rows_pass", "value": str(sum(1 for r in hash_rows if r.get("status") == "pass"))},
        {"metric": "canonical_reverse_regression_rows", "value": str(len(regression_rows))},
        {"metric": "canonical_reverse_regression_rows_pass", "value": str(sum(1 for r in regression_rows if r.get("status") == "pass"))},
        {"metric": "new_private_packets", "value": "0"},
        {"metric": "fresh_current_checkout_completed", "value": "no"},
    ]
    write_csv(ROOT / "data/rev0060_patch_order_summary.csv", summary_rows, ["metric", "value"])
    (ROOT / "data/rev0060_patch_order_summary.json").write_text(json.dumps(summary_rows, indent=2), encoding="utf-8")


def recorded_counts() -> Dict[str, object]:
    specs = (
        ("bundle_patch_orders", "data/rev0060_patch_order_permutation_matrix.csv"),
        ("bundle_patch_order_file_hash_rows", "data/rev0060_patch_order_file_hash_matrix.csv"),
        ("canonical_reverse_regression_rows", "data/rev0060_patch_order_regression_matrix.csv"),
    )
    counts: Dict[str, object] = {}
    for key, rel in specs:
        rows = read_csv(rel)
        counts[key] = len(rows)
        counts[key + "_pass"] = sum(1 for r in rows if r.get("status") == "pass")
    return counts


def main() -> int:
    ap = argparse.ArgumentParser(description="rev0060 patch-order permutation gate")
    ap.add_argument("--source-zip", default="/mnt/data/Nicotine-source(1).zip")
    ap.add_argument("--run-tests", action="store_true", help="apply all patch permutations and run canonical/reverse regressions")
    ap.add_argument("--write-data", action="store_true", help="write rev0060 data files during --run-tests")
    ap.add_argument("--out-dir", default="evidence/rev0060-patch-order-rerun")
    ns = ap.parse_args()

    source_zip = Path(ns.source_zip)
    checks: List[Dict[str, object]] = []
    errors: List[str] = []

    source_info = source_identity(source_zip)
    source_ok = bool(source_info.get("exists")) and source_info.get("sha256") == EXPECTED_SOURCE_SHA256 and set(source_info.get("lanes", [])) == set(LANES)
    checks.append({"check": "uploaded source bundle identity", "status": "pass" if source_ok else "fail", **source_info})
    if not source_ok:
        errors.append("uploaded source bundle identity")

    patch_rows = read_csv("data/rev0059_bundle_patch_manifest.csv")
    patch_ok = len(patch_rows) == 12 and all((ROOT / row.get("patch", "")).exists() for row in patch_rows)
    checks.append({"check": "rev0059 split bundle patch files available", "status": "pass" if patch_ok else "fail", "rows": len(patch_rows)})
    if not patch_ok:
        errors.append("rev0059 split bundle patch files available")

    if ns.run_tests:
        if not source_ok or not patch_ok:
            errors.append("run-tests blocked by missing source or patches")
        else:
            with tempfile.TemporaryDirectory(prefix="rev0060-order-") as td:
                work_dir = Path(td)
                perm_rows, hash_rows = run_permutation_gate(source_zip, work_dir)
                regression_rows = run_order_regressions(source_zip, work_dir, ROOT / ns.out_dir)
                checks.extend([
                    {"check": "all bundle patch permutations", "status": "pass" if len(perm_rows) == 72 and all(r.get("status") == "pass" for r in perm_rows) else "fail", "rows": len(perm_rows), "pass_rows": sum(1 for r in perm_rows if r.get("status") == "pass")},
                    {"check": "permutation final file hashes", "status": "pass" if len(hash_rows) == 360 and all(r.get("status") == "pass" for r in hash_rows) else "fail", "rows": len(hash_rows), "pass_rows": sum(1 for r in hash_rows if r.get("status") == "pass")},
                    {"check": "canonical and reverse fixed regressions", "status": "pass" if len(regression_rows) == 42 and all(r.get("status") == "pass" for r in regression_rows) else "fail", "rows": len(regression_rows), "pass_rows": sum(1 for r in regression_rows if r.get("status") == "pass")},
                ])
                for c in checks[-3:]:
                    if c["status"] != "pass":
                        errors.append(str(c["check"]))
                if ns.write_data:
                    write_outputs(perm_rows, hash_rows, regression_rows)
    else:
        counts = recorded_counts()
        ok = (
            counts.get("bundle_patch_orders") == 72 and counts.get("bundle_patch_orders_pass") == 72 and
            counts.get("bundle_patch_order_file_hash_rows") == 360 and counts.get("bundle_patch_order_file_hash_rows_pass") == 360 and
            counts.get("canonical_reverse_regression_rows") == 42 and counts.get("canonical_reverse_regression_rows_pass") == 42
        )
        checks.append({"check": "recorded rev0060 patch-order data", "status": "pass" if ok else "fail", **counts})
        if not ok:
            errors.append("recorded rev0060 patch-order data")

    for rel in ("handoff/rev0059/MANIFEST.sha256", "handoff/rev0060/MANIFEST.sha256"):
        if (ROOT / rel).exists():
            e = manifest_errors(rel)
            checks.append({"check": f"manifest {rel}", "status": "pass" if not e else "fail", "errors": e[:5]})
            errors.extend(e)

    # The helper imports an inherited local module; clean import-time cache files before
    # evaluating package hygiene so the helper does not fail its own smoke check.
    for cache_dir in ROOT.rglob("__pycache__"):
        shutil.rmtree(cache_dir, ignore_errors=True)
    for cache_dir in ROOT.rglob(".pytest_cache"):
        shutil.rmtree(cache_dir, ignore_errors=True)

    bad = package_hygiene()
    checks.append({"check": "package hygiene", "status": "pass" if not bad else "fail", "bad_count": len(bad), "examples": bad[:10]})
    errors.extend([f"hygiene:{x}" for x in bad])

    output = {"revision": REV, "status": "pass" if not errors else "fail", "checks": checks, "errors": errors}
    print(json.dumps(output, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
