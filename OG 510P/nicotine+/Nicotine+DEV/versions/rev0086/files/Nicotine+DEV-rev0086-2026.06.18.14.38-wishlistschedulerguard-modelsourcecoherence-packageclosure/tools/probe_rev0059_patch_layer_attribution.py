#!/usr/bin/env python3
"""rev0059 bundle patch attribution and independence gate.

This helper verifies the reviewer-facing split of the strict/front selected stack
into four filing-bundle patches.  With --run-tests it regenerates the rev0059
patch files from the uploaded archived source bundle, validates patch roundtrip
behavior, and runs target-only / all-except-bundle / all-bundles regression
matrices.
"""
from __future__ import annotations

import argparse
import csv
import difflib
import hashlib
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Tuple

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_SOURCE_SHA256 = "feaa8df98bbd0f28ba00eb8d52dcc3b9b9860e8d59039c7d41a98a0117505e5b"
SOURCE_PREFIX = "Nicotine+DEV-rev0003-upstream-sources-20260612T181540Z/source-trees/"
LANES = ("github-tag-3.3.10", "github-branch-3.3.x", "github-branch-master")
BAD_PARTS = {"__pycache__", ".pytest_cache", "source-trees", "git-full", ".git"}

BUNDLES: Tuple[Dict[str, object], ...] = (
    {
        "bundle": "U-123",
        "title": "download transfer-token active-owner collision",
        "helper": "tools/apply_u123_collision_gate_patch_rev0046.py",
        "files": ("pynicotine/downloads.py", "pynicotine/transfers.py"),
        "packets": ("U-123",),
    },
    {
        "bundle": "PB-01",
        "title": "peer primary-election replacement/promotion guard",
        "helper": "tools/apply_pb01_primary_guard_patch_rev0038.py",
        "files": ("pynicotine/slskproto.py",),
        "packets": ("PB-01",),
    },
    {
        "bundle": "SEARCH-RESP-SOURCE-ADMISSION",
        "title": "FileSearchResponse user/buddy/room source-admission guards",
        "helper": "tools/apply_search_resp_room_scope_patch_rev0043.py",
        "files": ("pynicotine/search.py",),
        "packets": ("SEARCH-RESP-01A", "SEARCH-RESP-01B-BUDDY", "SEARCH-RESP-01C-ROOM"),
    },
    {
        "bundle": "SEARCH-RESP-PARSER-BUDGET",
        "title": "FileSearchResponse prefix and accepted-result budgets",
        "helper": "tools/apply_search_resp_result_budget_patch_rev0042.py",
        "files": ("pynicotine/slskmessages.py",),
        "packets": ("SEARCH-RESP-PARSE-BUDGET-A", "SEARCH-RESP-PARSE-BUDGET-B"),
    },
)

PACKET_TESTS: Dict[str, Tuple[str, str, str]] = {
    "U-123": ("maintainer_artifacts/u123/test_downloads_duplicate_transfer_token_collision_rejection_regression.py", "unittest", "PYTHONPATH"),
    "PB-01": ("maintainer_artifacts/pb01/test_peer_connection_primary_election_fixed_regression.py", "pytest", "NICOTINE_SOURCE"),
    "SEARCH-RESP-01A": ("maintainer_artifacts/search-resp-01/test_search_response_user_scope_fixed_regression.py", "pytest", "PYTHONPATH"),
    "SEARCH-RESP-01B-BUDDY": ("maintainer_artifacts/search-resp-01/test_search_response_buddy_scope_fixed_regression.py", "pytest", "PYTHONPATH"),
    "SEARCH-RESP-01C-ROOM": ("maintainer_artifacts/search-resp-01/test_search_response_room_scope_fixed_regression.py", "pytest", "PYTHONPATH"),
    "SEARCH-RESP-PARSE-BUDGET-A": ("maintainer_artifacts/search-resp-01/test_search_response_prefix_budget_fixed_regression.py", "pytest", "PYTHONPATH"),
    "SEARCH-RESP-PARSE-BUDGET-B": ("maintainer_artifacts/search-resp-01/test_search_response_result_budget_fixed_regression.py", "pytest", "PYTHONPATH"),
}


def sha_path(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def write_csv(path: Path, rows: List[Dict[str, object]], fields: Iterable[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(fields))
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in writer.fieldnames})


def read_csv(rel: str) -> List[Dict[str, str]]:
    with (ROOT / rel).open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def source_identity(source_zip: Path) -> Dict[str, object]:
    info: Dict[str, object] = {"source_zip": str(source_zip), "exists": source_zip.exists()}
    if not source_zip.exists():
        return info
    info["sha256"] = sha_path(source_zip)
    lanes = set()
    entries = 0
    with zipfile.ZipFile(source_zip) as zf:
        for name in zf.namelist():
            entries += 1
            if name.startswith(SOURCE_PREFIX):
                rest = name[len(SOURCE_PREFIX):]
                lane = rest.split("/", 1)[0]
                if lane in LANES:
                    lanes.add(lane)
    info["entries"] = entries
    info["lanes"] = sorted(lanes)
    return info


def extract_lane(source_zip: Path, lane: str, dest: Path) -> int:
    prefix = SOURCE_PREFIX + lane + "/"
    count = 0
    with zipfile.ZipFile(source_zip) as zf:
        for zi in zf.infolist():
            name = zi.filename
            if not name.startswith(prefix) or name.endswith("/"):
                continue
            rel = name[len(prefix):]
            if not rel:
                continue
            target = dest / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            with zf.open(zi) as src, target.open("wb") as dst:
                shutil.copyfileobj(src, dst)
            count += 1
    return count


def bundle_by_name(name: str) -> Dict[str, object]:
    for bundle in BUNDLES:
        if bundle["bundle"] == name:
            return bundle
    raise KeyError(name)


def helper_cmd(helper_rel: str, checkout: Path) -> List[str]:
    return [sys.executable, str(ROOT / helper_rel), str(checkout)]


def apply_helper(bundle: Dict[str, object], checkout: Path) -> None:
    proc = subprocess.run(
        helper_cmd(str(bundle["helper"]), checkout),
        cwd=str(ROOT),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        timeout=60,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"helper failed for {bundle['bundle']} rc={proc.returncode}\n{proc.stdout}")


def patch_text_for_bundle(original: Path, modified: Path, bundle: Dict[str, object]) -> str:
    chunks: List[str] = []
    for file_rel in bundle["files"]:  # type: ignore[index]
        old_path = original / str(file_rel)
        new_path = modified / str(file_rel)
        old_lines = old_path.read_text(encoding="utf-8").splitlines()
        new_lines = new_path.read_text(encoding="utf-8").splitlines()
        if old_lines == new_lines:
            continue
        chunks.extend(difflib.unified_diff(
            old_lines,
            new_lines,
            fromfile=str(file_rel),
            tofile=str(file_rel),
            lineterm="",
        ))
    if not chunks:
        raise RuntimeError(f"no diff generated for {bundle['bundle']}")
    text = "\n".join(chunks)
    if not text.endswith("\n"):
        text += "\n"
    return text


def count_patch_stats(text: str) -> Dict[str, int]:
    return {
        "hunks": sum(1 for line in text.splitlines() if line.startswith("@@")),
        "insertions": sum(1 for line in text.splitlines() if line.startswith("+") and not line.startswith("+++")),
        "deletions": sum(1 for line in text.splitlines() if line.startswith("-") and not line.startswith("---")),
    }


def generate_bundle_patches(source_zip: Path, work_dir: Path) -> Tuple[List[Dict[str, object]], List[Dict[str, object]]]:
    patch_rows: List[Dict[str, object]] = []
    file_rows: List[Dict[str, object]] = []
    patch_root = ROOT / "handoff" / "rev0059" / "patches"
    patch_root.mkdir(parents=True, exist_ok=True)
    for lane in LANES:
        lane_base = work_dir / "source" / lane
        extract_lane(source_zip, lane, lane_base)
        for bundle in BUNDLES:
            print(f"GEN {lane} {bundle["bundle"]}", file=sys.stderr, flush=True)
            mod = work_dir / "modified" / lane / str(bundle["bundle"])
            if mod.exists():
                shutil.rmtree(mod)
            shutil.copytree(lane_base, mod)
            apply_helper(bundle, mod)
            text = patch_text_for_bundle(lane_base, mod, bundle)
            patch_rel = Path("handoff") / "rev0059" / "patches" / lane / f"{bundle['bundle'].lower().replace('/', '-').replace('_', '-')}-rev0059.patch"
            patch_path = ROOT / patch_rel
            patch_path.parent.mkdir(parents=True, exist_ok=True)
            patch_path.write_text(text, encoding="utf-8")
            stats = count_patch_stats(text)
            files_changed = []
            for file_rel in bundle["files"]:  # type: ignore[index]
                old_sha = sha_path(lane_base / str(file_rel))
                new_sha = sha_path(mod / str(file_rel))
                if old_sha != new_sha:
                    files_changed.append(str(file_rel))
                    file_rows.append({
                        "lane": lane,
                        "bundle": bundle["bundle"],
                        "file": str(file_rel),
                        "base_sha256": old_sha,
                        "patched_sha256": new_sha,
                        "status": "pass",
                    })
            patch_rows.append({
                "lane": lane,
                "bundle": bundle["bundle"],
                "title": bundle["title"],
                "patch": str(patch_rel),
                "sha256": sha_path(patch_path),
                "bytes": patch_path.stat().st_size,
                "files_changed": ";".join(files_changed),
                "hunks": stats["hunks"],
                "insertions": stats["insertions"],
                "deletions": stats["deletions"],
                "status": "generated-from-uploaded-source-bundle",
            })
    return patch_rows, file_rows


def patch_cmd(cwd: Path, patch_path: Path, stage: str) -> Dict[str, object]:
    if stage == "forward-dry-run":
        cmd = ["patch", "--batch", "--forward", "--dry-run", "-p0", "-i", str(patch_path)]
        expected = 0
    elif stage == "forward-apply":
        cmd = ["patch", "--batch", "--forward", "-p0", "-i", str(patch_path)]
        expected = 0
    elif stage == "reverse-dry-run-after-apply":
        cmd = ["patch", "--batch", "--reverse", "--dry-run", "-p0", "-i", str(patch_path)]
        expected = 0
    elif stage == "second-forward-dry-run-rejected":
        cmd = ["patch", "--batch", "--forward", "--dry-run", "-p0", "-i", str(patch_path)]
        expected = 1
    else:
        raise ValueError(stage)
    proc = subprocess.run(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=45)
    lines = [line.strip() for line in proc.stdout.splitlines() if line.strip()]
    return {
        "stage": stage,
        "expected_rc": str(expected),
        "observed_rc": str(proc.returncode),
        "status": "pass" if proc.returncode == expected else "fail",
        "summary": " | ".join(lines[-8:]),
    }


def validate_patch_roundtrip(source_zip: Path, patch_rows: List[Dict[str, object]], work_dir: Path) -> List[Dict[str, object]]:
    rows: List[Dict[str, object]] = []
    for lane in LANES:
        lane_base = work_dir / "roundtrip-source" / lane
        extract_lane(source_zip, lane, lane_base)
        for patch_row in [r for r in patch_rows if r["lane"] == lane]:
            checkout = work_dir / "roundtrip-work" / lane / str(patch_row["bundle"])
            if checkout.exists():
                shutil.rmtree(checkout)
            shutil.copytree(lane_base, checkout)
            patch_path = ROOT / str(patch_row["patch"])
            for stage in ("forward-dry-run", "forward-apply", "reverse-dry-run-after-apply", "second-forward-dry-run-rejected"):
                print(f"ROUND {lane} {patch_row["bundle"]} {stage}", file=sys.stderr, flush=True)
                result = patch_cmd(checkout, patch_path, stage)
                rows.append({"lane": lane, "bundle": patch_row["bundle"], "patch": patch_row["patch"], **result})
                if result["status"] != "pass" and stage in {"forward-dry-run", "forward-apply"}:
                    break
    return rows


def apply_patch_file(checkout: Path, patch_rel: str) -> Dict[str, object]:
    proc = subprocess.run(
        ["patch", "--batch", "--forward", "-p0", "-i", str(ROOT / patch_rel)],
        cwd=checkout,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        timeout=45,
    )
    return {"rc": proc.returncode, "summary": " | ".join([line.strip() for line in proc.stdout.splitlines() if line.strip()][-8:])}


def test_summary(output: str) -> str:
    lines = [line.strip() for line in output.splitlines() if line.strip()]
    for line in reversed(lines):
        if re.search(r"\d+ (failed|passed|errors?|error)|^OK$|^FAILED", line, re.I):
            return line
    return lines[-1] if lines else ""


def run_packet_test(lane: str, source_dir: Path, packet: str, scenario: str, expected: str, patches_applied: Sequence[str], out_dir: Path) -> Dict[str, object]:
    test_rel, runner, env_kind = PACKET_TESTS[packet]
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"
    if env_kind == "NICOTINE_SOURCE":
        env.pop("PYTHONPATH", None)
        env["NICOTINE_SOURCE"] = str(source_dir)
    else:
        env["PYTHONPATH"] = str(source_dir)
    if runner == "unittest":
        cmd = [sys.executable, str(ROOT / test_rel)]
    else:
        cmd = [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "--tb=short", str(ROOT / test_rel)]
    out_dir.mkdir(parents=True, exist_ok=True)
    safe_name = f"{lane}__{scenario}__{packet}.txt".replace("/", "_")
    output_file = out_dir / safe_name
    with output_file.open("w", encoding="utf-8") as fh:
        proc = subprocess.Popen(cmd, cwd="/tmp", env=env, stdout=fh, stderr=subprocess.STDOUT, text=True, start_new_session=True)
        try:
            rc = proc.wait(timeout=90)
        except subprocess.TimeoutExpired:
            os.killpg(proc.pid, signal.SIGKILL)
            rc = 124
    text = output_file.read_text(encoding="utf-8", errors="replace")
    if expected == "0":
        ok = rc == 0
    elif expected == "nonzero":
        ok = rc != 0 and rc != 124
    else:
        raise ValueError(expected)
    return {
        "lane": lane,
        "packet": packet,
        "scenario": scenario,
        "patches_applied": ";".join(patches_applied),
        "runner": runner,
        "env_kind": env_kind,
        "expected_rc": expected,
        "observed_rc": str(rc),
        "status": "pass" if ok else "fail",
        "summary": test_summary(text),
        "test": test_rel,
        "output_file": str(output_file.relative_to(ROOT)),
    }


def run_attribution(source_zip: Path, patch_rows: List[Dict[str, object]], work_dir: Path, out_dir: Path) -> Tuple[List[Dict[str, object]], List[Dict[str, object]]]:
    patch_map = {(str(r["lane"]), str(r["bundle"])): str(r["patch"]) for r in patch_rows}
    attribution_rows: List[Dict[str, object]] = []
    stack_rows: List[Dict[str, object]] = []
    for lane in LANES:
        lane_base = work_dir / "attrib-source" / lane
        extract_lane(source_zip, lane, lane_base)
        for bundle in BUNDLES:
            bundle_name = str(bundle["bundle"])
            target_packets = tuple(bundle["packets"])  # type: ignore[arg-type]
            scenarios = [
                ("target-bundle-only", (bundle_name,), "0"),
                ("all-except-target-bundle", tuple(str(b["bundle"]) for b in BUNDLES if b["bundle"] != bundle_name), "nonzero"),
            ]
            for scenario, bundles_to_apply, expected in scenarios:
                checkout = work_dir / "attrib-work" / lane / bundle_name / scenario
                if checkout.exists():
                    shutil.rmtree(checkout)
                shutil.copytree(lane_base, checkout)
                applied: List[str] = []
                patch_errors: List[str] = []
                for apply_bundle in bundles_to_apply:
                    result = apply_patch_file(checkout, patch_map[(lane, apply_bundle)])
                    if result["rc"] != 0:
                        patch_errors.append(f"{apply_bundle}:rc={result['rc']}:{result['summary']}")
                    else:
                        applied.append(apply_bundle)
                for packet in target_packets:
                    if patch_errors:
                        attribution_rows.append({
                            "lane": lane,
                            "packet": packet,
                            "scenario": scenario,
                            "patches_applied": ";".join(applied),
                            "runner": PACKET_TESTS[packet][1],
                            "env_kind": PACKET_TESTS[packet][2],
                            "expected_rc": expected,
                            "observed_rc": "patch-apply-error",
                            "status": "fail",
                            "summary": " || ".join(patch_errors),
                            "test": PACKET_TESTS[packet][0],
                            "output_file": "",
                        })
                    else:
                        print(f"ATTRIB {lane} {bundle_name} {scenario} {packet}", file=sys.stderr, flush=True)
                        attribution_rows.append(run_packet_test(lane, checkout, packet, scenario, expected, applied, out_dir))
        # Full split-bundle stack compatibility from the four generated bundle patches.
        checkout = work_dir / "stack-work" / lane
        if checkout.exists():
            shutil.rmtree(checkout)
        shutil.copytree(lane_base, checkout)
        applied_stack: List[str] = []
        for bundle in BUNDLES:
            bundle_name = str(bundle["bundle"])
            result = apply_patch_file(checkout, patch_map[(lane, bundle_name)])
            if result["rc"] != 0:
                raise RuntimeError(f"full-stack patch apply failed lane={lane} bundle={bundle_name}: {result}")
            applied_stack.append(bundle_name)
        for packet in PACKET_TESTS:
            print(f"STACK {lane} {packet}", file=sys.stderr, flush=True)
            stack_rows.append(run_packet_test(lane, checkout, packet, "all-bundles-stack", "0", applied_stack, out_dir))
    return attribution_rows, stack_rows


def manifest_errors(rel: str) -> List[str]:
    path = ROOT / rel
    if not path.exists():
        return [f"missing manifest {rel}"]
    errors: List[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            want, file_rel = line.split("  ", 1)
        except ValueError:
            errors.append(f"bad manifest line {line!r}")
            continue
        file_path = ROOT / file_rel
        if not file_path.exists():
            errors.append(f"missing manifest target {file_rel}")
        elif sha_path(file_path) != want:
            errors.append(f"hash mismatch {file_rel}")
    return errors


def package_hygiene() -> List[str]:
    bad: List[str] = []
    for path in ROOT.rglob("*"):
        parts = path.relative_to(ROOT).parts
        if any(part in BAD_PARTS for part in parts):
            bad.append(str(path.relative_to(ROOT)))
    return bad


def write_outputs(patch_rows: List[Dict[str, object]], file_rows: List[Dict[str, object]], roundtrip_rows: List[Dict[str, object]], attribution_rows: List[Dict[str, object]], stack_rows: List[Dict[str, object]]) -> None:
    write_csv(ROOT / "data/rev0059_bundle_patch_manifest.csv", patch_rows, ["lane", "bundle", "title", "patch", "sha256", "bytes", "files_changed", "hunks", "insertions", "deletions", "status"])
    (ROOT / "data/rev0059_bundle_patch_manifest.json").write_text(json.dumps(patch_rows, indent=2), encoding="utf-8")
    write_csv(ROOT / "data/rev0059_bundle_patch_file_hashes.csv", file_rows, ["lane", "bundle", "file", "base_sha256", "patched_sha256", "status"])
    (ROOT / "data/rev0059_bundle_patch_file_hashes.json").write_text(json.dumps(file_rows, indent=2), encoding="utf-8")
    write_csv(ROOT / "data/rev0059_bundle_patch_roundtrip_matrix.csv", roundtrip_rows, ["lane", "bundle", "patch", "stage", "expected_rc", "observed_rc", "status", "summary"])
    (ROOT / "data/rev0059_bundle_patch_roundtrip_matrix.json").write_text(json.dumps(roundtrip_rows, indent=2), encoding="utf-8")
    write_csv(ROOT / "data/rev0059_bundle_attribution_matrix.csv", attribution_rows, ["lane", "packet", "scenario", "patches_applied", "runner", "env_kind", "expected_rc", "observed_rc", "status", "summary", "test", "output_file"])
    (ROOT / "data/rev0059_bundle_attribution_matrix.json").write_text(json.dumps(attribution_rows, indent=2), encoding="utf-8")
    write_csv(ROOT / "data/rev0059_bundle_stack_regression_matrix.csv", stack_rows, ["lane", "packet", "scenario", "patches_applied", "runner", "env_kind", "expected_rc", "observed_rc", "status", "summary", "test", "output_file"])
    (ROOT / "data/rev0059_bundle_stack_regression_matrix.json").write_text(json.dumps(stack_rows, indent=2), encoding="utf-8")
    summary_rows = [
        {"metric": "source_bundle_used", "value": "yes"},
        {"metric": "source_zip_sha256", "value": EXPECTED_SOURCE_SHA256},
        {"metric": "bundle_patch_files", "value": str(len(patch_rows))},
        {"metric": "bundle_patch_file_hash_rows", "value": str(len(file_rows))},
        {"metric": "bundle_patch_roundtrip_rows", "value": str(len(roundtrip_rows))},
        {"metric": "bundle_patch_roundtrip_pass", "value": str(sum(1 for r in roundtrip_rows if r.get("status") == "pass"))},
        {"metric": "attribution_rows", "value": str(len(attribution_rows))},
        {"metric": "attribution_pass", "value": str(sum(1 for r in attribution_rows if r.get("status") == "pass"))},
        {"metric": "split_bundle_stack_rows", "value": str(len(stack_rows))},
        {"metric": "split_bundle_stack_pass", "value": str(sum(1 for r in stack_rows if r.get("status") == "pass"))},
        {"metric": "new_private_packets", "value": "0"},
        {"metric": "fresh_current_checkout_completed", "value": "no"},
    ]
    write_csv(ROOT / "data/rev0059_bundle_attribution_summary.csv", summary_rows, ["metric", "value"])
    (ROOT / "data/rev0059_bundle_attribution_summary.json").write_text(json.dumps(summary_rows, indent=2), encoding="utf-8")


def recorded_counts() -> Dict[str, object]:
    specs = (
        ("bundle_patch_files", "data/rev0059_bundle_patch_manifest.csv"),
        ("bundle_patch_file_hash_rows", "data/rev0059_bundle_patch_file_hashes.csv"),
        ("bundle_patch_roundtrip_rows", "data/rev0059_bundle_patch_roundtrip_matrix.csv"),
        ("attribution_rows", "data/rev0059_bundle_attribution_matrix.csv"),
        ("split_bundle_stack_rows", "data/rev0059_bundle_stack_regression_matrix.csv"),
    )
    counts: Dict[str, object] = {}
    for key, rel in specs:
        path = ROOT / rel
        if not path.exists():
            counts[key] = 0
            counts[key + "_pass"] = 0
            continue
        rows = read_csv(rel)
        counts[key] = len(rows)
        counts[key + "_pass"] = sum(1 for r in rows if r.get("status") == "pass" or key == "bundle_patch_files")
    return counts


def main() -> int:
    ap = argparse.ArgumentParser(description="rev0059 strict/front bundle patch attribution gate")
    ap.add_argument("--source-zip", default="/mnt/data/Nicotine-source(1).zip")
    ap.add_argument("--run-tests", action="store_true", help="regenerate rev0059 bundle patches and run attribution/stack tests")
    ap.add_argument("--out-dir", default="evidence/rev0059-bundle-attribution-rerun")
    ap.add_argument("--write-data", action="store_true", help="write rev0059 data files during --run-tests")
    ns = ap.parse_args()

    source_zip = Path(ns.source_zip)
    checks: List[Dict[str, object]] = []
    errors: List[str] = []
    source_info = source_identity(source_zip)
    source_ok = bool(source_info.get("exists")) and source_info.get("sha256") == EXPECTED_SOURCE_SHA256 and set(source_info.get("lanes", [])) == set(LANES)
    checks.append({"check": "uploaded source bundle identity", "status": "pass" if source_ok else "fail", **source_info})
    if not source_ok:
        errors.append("uploaded source bundle identity")

    if ns.run_tests:
        if not source_ok:
            errors.append("run-tests blocked by source identity")
        else:
            with tempfile.TemporaryDirectory(prefix="rev0059-attrib-") as td:
                work_dir = Path(td)
                patch_rows, file_rows = generate_bundle_patches(source_zip, work_dir)
                roundtrip_rows = validate_patch_roundtrip(source_zip, patch_rows, work_dir)
                attribution_rows, stack_rows = run_attribution(source_zip, patch_rows, work_dir, ROOT / ns.out_dir)
                checks.extend([
                    {"check": "bundle patch generation", "status": "pass" if len(patch_rows) == 12 and all(Path(ROOT / str(r["patch"])).exists() for r in patch_rows) else "fail", "rows": len(patch_rows)},
                    {"check": "bundle patch file hashes", "status": "pass" if len(file_rows) == 15 and all(r.get("status") == "pass" for r in file_rows) else "fail", "rows": len(file_rows)},
                    {"check": "bundle patch roundtrip", "status": "pass" if len(roundtrip_rows) == 48 and all(r.get("status") == "pass" for r in roundtrip_rows) else "fail", "rows": len(roundtrip_rows), "pass_rows": sum(1 for r in roundtrip_rows if r.get("status") == "pass")},
                    {"check": "target-only and all-except attribution", "status": "pass" if len(attribution_rows) == 42 and all(r.get("status") == "pass" for r in attribution_rows) else "fail", "rows": len(attribution_rows), "pass_rows": sum(1 for r in attribution_rows if r.get("status") == "pass")},
                    {"check": "split bundle full-stack regression", "status": "pass" if len(stack_rows) == 21 and all(r.get("status") == "pass" for r in stack_rows) else "fail", "rows": len(stack_rows), "pass_rows": sum(1 for r in stack_rows if r.get("status") == "pass")},
                ])
                for c in checks[-5:]:
                    if c["status"] != "pass":
                        errors.append(str(c["check"]))
                if ns.write_data:
                    write_outputs(patch_rows, file_rows, roundtrip_rows, attribution_rows, stack_rows)
    else:
        counts = recorded_counts()
        ok = (
            counts.get("bundle_patch_files") == 12 and
            counts.get("bundle_patch_file_hash_rows") == 15 and counts.get("bundle_patch_file_hash_rows_pass") == 15 and
            counts.get("bundle_patch_roundtrip_rows") == 48 and counts.get("bundle_patch_roundtrip_rows_pass") == 48 and
            counts.get("attribution_rows") == 42 and counts.get("attribution_rows_pass") == 42 and
            counts.get("split_bundle_stack_rows") == 21 and counts.get("split_bundle_stack_rows_pass") == 21
        )
        checks.append({"check": "recorded rev0059 bundle attribution data", "status": "pass" if ok else "fail", **counts})
        if not ok:
            errors.append("recorded rev0059 bundle attribution data")

    for rel in ("handoff/rev0058/MANIFEST.sha256", "handoff/rev0059/MANIFEST.sha256"):
        if (ROOT / rel).exists():
            e = manifest_errors(rel)
            checks.append({"check": f"manifest {rel}", "status": "pass" if not e else "fail", "errors": e[:5]})
            errors.extend(e)

    bad = package_hygiene()
    checks.append({"check": "package hygiene", "status": "pass" if not bad else "fail", "bad_count": len(bad), "examples": bad[:10]})
    errors.extend([f"hygiene:{x}" for x in bad])

    output = {"revision": "rev0059", "status": "pass" if not errors else "fail", "checks": checks, "errors": errors}
    print(json.dumps(output, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
