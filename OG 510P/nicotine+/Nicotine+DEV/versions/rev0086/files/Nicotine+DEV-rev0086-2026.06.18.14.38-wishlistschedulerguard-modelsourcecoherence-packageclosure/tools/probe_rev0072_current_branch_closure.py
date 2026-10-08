#!/usr/bin/env python3
"""rev0072 exact-current 3.3.x closure and cube-entrypoint refactor gate."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import signal
import shutil
import subprocess
import sys
import tempfile
import zipfile
from dataclasses import asdict
from pathlib import Path
from typing import Any, Iterable

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from source_bundle_locator import (  # noqa: E402
    EXPECTED_SOURCE_SHA256,
    SOURCE_PREFIX,
    SourceBundleError,
    inspect_bundle,
    locate_source_bundle,
)

LANE = "github-branch-3.3.x"
PACKETS = (
    "U-123",
    "PB-01",
    "SEARCH-RESP-01A",
    "SEARCH-RESP-01B-BUDDY",
    "SEARCH-RESP-01C-ROOM",
    "SEARCH-RESP-PARSE-BUDGET-A",
    "SEARCH-RESP-PARSE-BUDGET-B",
)
PACKET_FILES = {
    "U-123": "pynicotine/downloads.py;pynicotine/transfers.py",
    "PB-01": "pynicotine/slskproto.py",
    "SEARCH-RESP-01A": "pynicotine/search.py",
    "SEARCH-RESP-01B-BUDDY": "pynicotine/search.py",
    "SEARCH-RESP-01C-ROOM": "pynicotine/search.py",
    "SEARCH-RESP-PARSE-BUDGET-A": "pynicotine/slskmessages.py",
    "SEARCH-RESP-PARSE-BUDGET-B": "pynicotine/slskmessages.py",
}
BAD_PARTS = {"__pycache__", ".pytest_cache", "source-trees", "git-full", ".git"}

def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_csv(path: Path, rows: list[dict[str, Any]], fields: Iterable[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(fields))
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in writer.fieldnames})


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def source_lane_head(source_zip: Path, lane: str) -> str:
    suffix = f"git-full/.git/worktrees/{lane}/HEAD"
    with zipfile.ZipFile(source_zip) as archive:
        matches = [name for name in archive.namelist() if name.endswith(suffix)]
        if len(matches) != 1:
            raise RuntimeError(f"expected one {suffix}, found {len(matches)}")
        return archive.read(matches[0]).decode("ascii", errors="strict").strip()


def safe_extract_lane(source_zip: Path, lane: str, destination: Path) -> int:
    prefix = SOURCE_PREFIX + lane + "/"
    count = 0
    with zipfile.ZipFile(source_zip) as archive:
        for info in archive.infolist():
            if not info.filename.startswith(prefix) or info.filename.endswith("/"):
                continue
            rel = info.filename[len(prefix):]
            rel_path = Path(rel)
            if rel_path.is_absolute() or ".." in rel_path.parts:
                raise RuntimeError(f"unsafe source entry: {info.filename}")
            target = destination / rel_path
            target.parent.mkdir(parents=True, exist_ok=True)
            with archive.open(info) as src, target.open("wb") as dst:
                shutil.copyfileobj(src, dst)
            count += 1
    return count


def run(
    command: list[str],
    *,
    cwd: Path,
    timeout: int = 240,
    extra_env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"
    if extra_env:
        env.update(extra_env)
    process = subprocess.Popen(
        command,
        cwd=cwd,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        start_new_session=(os.name == "posix"),
    )
    try:
        stdout, _ = process.communicate(timeout=timeout)
        return subprocess.CompletedProcess(command, process.returncode, stdout)
    except subprocess.TimeoutExpired:
        if os.name == "posix":
            os.killpg(process.pid, signal.SIGKILL)
        else:
            process.kill()
        stdout, _ = process.communicate()
        stdout = (stdout or "") + f"\n[rev0072 process-group timeout after {timeout}s]\n"
        return subprocess.CompletedProcess(command, 124, stdout)


def cleanup_caches(path: Path) -> None:
    for cache in list(path.rglob("__pycache__")) + list(path.rglob(".pytest_cache")):
        shutil.rmtree(cache, ignore_errors=True)


def normalize_baseline(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    output: list[dict[str, str]] = []
    for row in rows:
        normalized = dict(row)
        normalized["stage"] = (
            "current-3.3.x-witness"
            if row.get("stage") == "archived-current-witness"
            else "current-3.3.x-unpatched-fixed-regression"
        )
        normalized["basis"] = "exact upstream 3.3.x ref match at rev0072 snapshot"
        output.append(normalized)
    return output


def package_hygiene() -> list[str]:
    bad: list[str] = []
    for path in ROOT.rglob("*"):
        parts = path.relative_to(ROOT).parts
        if any(part in BAD_PARTS for part in parts):
            bad.append(str(path.relative_to(ROOT)))
    return bad


def historical_alias_audit() -> dict[str, Any]:
    pattern = re.compile(r"Nicotine-source\(1\)\.zip")
    files = 0
    references = 0
    active_hits: list[str] = []

    def is_active_path(relative: str) -> bool:
        path = Path(relative)
        if relative in {"README.md", "REVISION.txt", "docs/START-HERE.md", "workspace/NEXT-REVISION-QUEUE.md"}:
            return True
        if relative.startswith("handoff/rev0072/"):
            return True
        if path.parent == Path("docs") and "REV0072" in path.name:
            return True
        if path.parent == Path("tools") and (path.name == "source_bundle_locator.py" or "rev0072" in path.name):
            return True
        return False
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        count = len(pattern.findall(text))
        if not count:
            continue
        files += 1
        references += count
        rel = str(path.relative_to(ROOT))
        if is_active_path(rel):
            active_hits.append(rel)
    return {
        "historical_files": files,
        "historical_references": references,
        "active_entrypoint_hits": sorted(active_hits),
        "status": "pass" if not active_hits else "fail",
    }


def locator_negative_controls() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with tempfile.TemporaryDirectory(prefix="rev0072-locator-") as temp:
        temp_path = Path(temp)
        decoy = temp_path / "Nicotine-source-decoy.zip"
        decoy.write_bytes(b"not a zip")
        inspection = inspect_bundle(decoy)
        rows.append({
            "control": "malformed decoy rejected",
            "status": "pass" if inspection.status == "fail" and not inspection.zip_ok else "fail",
            "detail": inspection.error,
        })
        try:
            locate_source_bundle("auto", search_dirs=[temp_path], env={})
            no_valid_rejected = False
        except SourceBundleError:
            no_valid_rejected = True
        rows.append({
            "control": "directory with no valid bundle fails closed",
            "status": "pass" if no_valid_rejected else "fail",
            "detail": "SourceBundleError expected",
        })
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description="rev0072 exact-current supported-branch closure gate")
    parser.add_argument("--source-zip", default="auto", help="explicit source ZIP path or 'auto'")
    parser.add_argument("--out-dir", default=str(ROOT / "evidence" / "rev0072-current-branch-closure-runtime"))
    parser.add_argument("--write-data", action="store_true", help="write canonical rev0072 matrices under data/")
    args = parser.parse_args()

    out_dir = Path(args.out_dir).resolve()
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True)
    checks: list[dict[str, Any]] = []
    errors: list[str] = []

    try:
        source_zip, candidates = locate_source_bundle(args.source_zip)
    except SourceBundleError as exc:
        print(json.dumps({"revision": "rev0072", "status": "fail", "errors": [str(exc)]}, indent=2))
        return 1
    source_info = inspect_bundle(source_zip)
    checks.append({"check": "content-addressed source selection", "status": source_info.status, **asdict(source_info)})
    if source_info.status != "pass":
        errors.append("source bundle contract")

    snapshot_path = ROOT / "data" / "rev0072_upstream_ref_snapshot.json"
    snapshot = json.loads(snapshot_path.read_text(encoding="utf-8"))
    current_ref = snapshot["refs"]["3.3.x"]["sha"]
    lane_head = source_lane_head(source_zip, LANE)
    exact_ref = lane_head == current_ref == snapshot["archived_lane_refs"][LANE]
    checks.append({
        "check": "supported 3.3.x lane equals observed current upstream ref",
        "status": "pass" if exact_ref else "fail",
        "lane": LANE,
        "lane_head": lane_head,
        "observed_current_ref": current_ref,
        "observed_at": snapshot["observed_at"],
    })
    if not exact_ref:
        errors.append("3.3.x current ref mismatch")

    baseline_dir = out_dir / "unpatched"
    patched_dir = out_dir / "patched"
    with tempfile.TemporaryDirectory(prefix="rev0072-current-branch-") as temp:
        source_root = Path(temp) / "source-root"
        lane_dir = source_root / "source-trees" / LANE
        extracted = safe_extract_lane(source_zip, LANE, lane_dir)
        baseline_proc = run([
            sys.executable,
            str(ROOT / "tools" / "run_rev0056_archived_baseline_delta.py"),
            "--source-dir", str(source_root),
            "--lane", LANE,
            "--out", str(baseline_dir),
        ], cwd=ROOT)
        (out_dir / "unpatched-runner-stdout.txt").write_text(baseline_proc.stdout, encoding="utf-8")
        checks.append({
            "check": "current 3.3.x unpatched witness/delta runner",
            "status": "pass" if baseline_proc.returncode == 0 else "fail",
            "observed_rc": baseline_proc.returncode,
            "files_extracted": extracted,
        })
        if baseline_proc.returncode != 0:
            errors.append("unpatched baseline/delta runner")

        cleanroom_proc = run([
            sys.executable,
            str(ROOT / "handoff" / "rev0062" / "cleanroom-kit" / "run_cleanroom_replay.py"),
            "--source-zip", str(source_zip),
            "--kit-dir", str(ROOT / "handoff" / "rev0062" / "cleanroom-kit"),
            "--out-dir", str(patched_dir),
            "--lanes", LANE,
        ], cwd=ROOT)
        (out_dir / "patched-runner-stdout.txt").write_text(cleanroom_proc.stdout, encoding="utf-8")
        checks.append({
            "check": "current 3.3.x clean-room patch replay",
            "status": "pass" if cleanroom_proc.returncode == 0 else "fail",
            "observed_rc": cleanroom_proc.returncode,
        })
        if cleanroom_proc.returncode != 0:
            errors.append("patched clean-room runner")

    baseline_path = baseline_dir / "rev0056_baseline_delta_matrix.csv"
    patched_path = patched_dir / "cleanroom_fixed_regression_matrix.csv"
    patch_apply_path = patched_dir / "cleanroom_patch_apply_matrix.csv"
    hash_path = patched_dir / "cleanroom_patched_file_hashes.csv"
    baseline_rows = normalize_baseline(read_csv(baseline_path)) if baseline_path.exists() else []
    patched_rows = read_csv(patched_path) if patched_path.exists() else []
    patch_rows = read_csv(patch_apply_path) if patch_apply_path.exists() else []
    hash_rows = read_csv(hash_path) if hash_path.exists() else []

    baseline_fixed = [row for row in baseline_rows if row.get("packet") in PACKETS and "unpatched" in row.get("stage", "")]
    baseline_witness = [row for row in baseline_rows if row.get("stage") == "current-3.3.x-witness"]
    baseline_ok = len(baseline_rows) == 10 and len(baseline_witness) == 3 and len(baseline_fixed) == 7 and all(row.get("status") == "pass" for row in baseline_rows)
    patched_ok = len(patched_rows) == 7 and {row.get("packet") for row in patched_rows} == set(PACKETS) and all(row.get("status") == "pass" for row in patched_rows)
    patch_ok = len(patch_rows) == 4 and all(row.get("status") == "pass" for row in patch_rows)
    hash_ok = len(hash_rows) == 5 and all(row.get("status") == "pass" for row in hash_rows)
    for label, status, rows, expected in (
        ("current unpatched delta matrix", baseline_ok, baseline_rows, 10),
        ("current patched fixed-regression matrix", patched_ok, patched_rows, 7),
        ("current patch apply matrix", patch_ok, patch_rows, 4),
        ("current patched touched-file hashes", hash_ok, hash_rows, 5),
    ):
        checks.append({"check": label, "status": "pass" if status else "fail", "rows": len(rows), "expected_rows": expected})
        if not status:
            errors.append(label)

    unpatched_by_packet = {row["packet"]: row for row in baseline_fixed}
    patched_by_packet = {row["packet"]: row for row in patched_rows}
    packet_rows: list[dict[str, Any]] = []
    for packet in PACKETS:
        before = unpatched_by_packet.get(packet, {})
        after = patched_by_packet.get(packet, {})
        status = "pass" if before.get("status") == "pass" and after.get("status") == "pass" and exact_ref else "fail"
        packet_rows.append({
            "packet": packet,
            "lane": LANE,
            "current_ref": current_ref,
            "touched_files": PACKET_FILES[packet],
            "unpatched_expected": "fixed-behavior regression returns nonzero",
            "unpatched_observed_rc": before.get("observed_rc", ""),
            "unpatched_summary": before.get("summary", ""),
            "patched_expected": "fixed-behavior regression returns 0",
            "patched_observed_rc": after.get("observed_rc", ""),
            "patched_summary": after.get("summary", ""),
            "current_applicability": "confirmed fixed-behavior delta on exact current supported branch",
            "security_severity": "not reclassified by this gate",
            "status": status,
        })
    packet_ok = len(packet_rows) == 7 and all(row["status"] == "pass" for row in packet_rows)
    checks.append({"check": "seven-packet current applicability ledger", "status": "pass" if packet_ok else "fail", "rows": len(packet_rows)})
    if not packet_ok:
        errors.append("packet current applicability ledger")

    controls = locator_negative_controls()
    controls_ok = all(row["status"] == "pass" for row in controls)
    checks.append({"check": "source locator negative controls", "status": "pass" if controls_ok else "fail", "rows": len(controls)})
    if not controls_ok:
        errors.append("source locator negative controls")

    alias_audit = historical_alias_audit()
    checks.append({"check": "active entrypoints avoid session-specific source alias", **alias_audit})
    if alias_audit["status"] != "pass":
        errors.append("active hard-coded source alias")

    readme_lines = len((ROOT / "README.md").read_text(encoding="utf-8").splitlines())
    start_lines = len((ROOT / "docs" / "START-HERE.md").read_text(encoding="utf-8").splitlines())
    archive_ok = (ROOT / "docs" / "archive" / "README-through-rev0071.md").exists() and (ROOT / "docs" / "archive" / "START-HERE-through-rev0071.md").exists()
    entrypoint_ok = readme_lines <= 100 and start_lines <= 180 and archive_ok
    checks.append({
        "check": "concise entrypoint navigation refactor",
        "status": "pass" if entrypoint_ok else "fail",
        "readme_lines": readme_lines,
        "start_here_lines": start_lines,
        "history_archived": archive_ok,
    })
    if not entrypoint_ok:
        errors.append("entrypoint navigation refactor")

    # Legacy baseline fixtures invoke pytest without disabling its cache
    # provider.  Remove only generated cache directories before packaging.
    cleanup_caches(ROOT)
    bad = package_hygiene()
    checks.append({"check": "package hygiene", "status": "pass" if not bad else "fail", "bad_count": len(bad), "examples": bad[:10]})
    if bad:
        errors.extend(f"package hygiene: {item}" for item in bad[:10])

    source_candidates = [asdict(row) for row in candidates]
    ref_rows = [
        {
            "lane": LANE,
            "role": "supported-current-runtime-gate",
            "uploaded_head": lane_head,
            "observed_upstream_head": current_ref,
            "relation": "exact",
            "runtime_rerun": "yes",
            "status": "pass" if exact_ref else "fail",
        },
        {
            "lane": "github-branch-master",
            "role": "development-branch-corroboration",
            "uploaded_head": snapshot["archived_lane_refs"]["github-branch-master"],
            "observed_upstream_head": snapshot["refs"]["master"]["sha"],
            "relation": "behind-by-6-commits; five strict file histories unchanged",
            "runtime_rerun": "archived strict-surface only",
            "status": "corroborated-not-exact",
        },
    ]

    if args.write_data:
        write_csv(ROOT / "data" / "rev0072_current_unpatched_delta_matrix.csv", baseline_rows, list(baseline_rows[0]) if baseline_rows else ["status"])
        write_json(ROOT / "data" / "rev0072_current_unpatched_delta_matrix.json", baseline_rows)
        write_csv(ROOT / "data" / "rev0072_current_patched_regression_matrix.csv", patched_rows, list(patched_rows[0]) if patched_rows else ["status"])
        write_json(ROOT / "data" / "rev0072_current_patched_regression_matrix.json", patched_rows)
        write_csv(ROOT / "data" / "rev0072_current_packet_state.csv", packet_rows, list(packet_rows[0]))
        write_json(ROOT / "data" / "rev0072_current_packet_state.json", packet_rows)
        write_csv(ROOT / "data" / "rev0072_current_ref_ledger.csv", ref_rows, list(ref_rows[0]))
        write_json(ROOT / "data" / "rev0072_current_ref_ledger.json", ref_rows)
        write_csv(ROOT / "data" / "rev0072_source_locator_negative_controls.csv", controls, list(controls[0]))
        write_json(ROOT / "data" / "rev0072_source_locator_negative_controls.json", controls)
        write_json(ROOT / "data" / "rev0072_source_bundle_candidates.json", source_candidates)
        write_json(ROOT / "data" / "rev0072_entrypoint_source_alias_audit.json", alias_audit)

    summary = {
        "revision": "rev0072",
        "status": "pass" if not errors else "fail",
        "observed_at": snapshot["observed_at"],
        "source_zip": str(source_zip),
        "source_sha256": EXPECTED_SOURCE_SHA256,
        "supported_branch": "3.3.x",
        "supported_branch_current_ref": current_ref,
        "uploaded_lane_ref": lane_head,
        "exact_current_ref_match": exact_ref,
        "current_witness_rows": len(baseline_witness),
        "current_unpatched_fixed_regression_rows": len(baseline_fixed),
        "current_unpatched_fixed_regression_expected_failures_observed": sum(row.get("status") == "pass" for row in baseline_fixed),
        "current_patched_fixed_regression_rows": len(patched_rows),
        "current_patched_fixed_regression_pass": sum(row.get("status") == "pass" for row in patched_rows),
        "patch_apply_rows": len(patch_rows),
        "patch_apply_pass": sum(row.get("status") == "pass" for row in patch_rows),
        "patched_file_hash_rows": len(hash_rows),
        "patched_file_hash_pass": sum(row.get("status") == "pass" for row in hash_rows),
        "packets_current_applicable": sum(row.get("status") == "pass" for row in packet_rows),
        "active_legacy_alias_hits": len(alias_audit["active_entrypoint_hits"]),
        "historical_legacy_alias_files_preserved": alias_audit["historical_files"],
        "readme_lines": readme_lines,
        "start_here_lines": start_lines,
        "checks": checks,
        "errors": errors,
    }
    write_json(out_dir / "rev0072_current_branch_closure_summary.json", summary)
    if args.write_data:
        write_json(ROOT / "data" / "rev0072_current_branch_closure_summary.json", summary)
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
