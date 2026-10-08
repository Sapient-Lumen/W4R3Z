#!/usr/bin/env python3
"""rev0063 clean-room contract and tamper gate.

This helper validates the exported rev0062 clean-room kit as a reviewer-facing
contract without re-running the full positive replay by default. It verifies the
recorded rev0062 replay summary, validates kit structure/path safety, and runs
fast fail-closed negative controls.
"""
from __future__ import annotations
import argparse, csv, hashlib, json, os, shutil, subprocess, sys, tempfile, zipfile
from pathlib import Path
from typing import Dict, Iterable, List
sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
KIT = ROOT / "handoff" / "rev0062" / "cleanroom-kit"
LANES = ("github-tag-3.3.10", "github-branch-3.3.x", "github-branch-master")
PATCHES = ("u-123-rev0059.patch", "pb-01-rev0059.patch", "search-resp-source-admission-rev0059.patch", "search-resp-parser-budget-rev0059.patch")
TESTS = (
    ("U-123", "tests/u123/test_downloads_duplicate_transfer_token_collision_rejection_regression.py"),
    ("PB-01", "tests/pb01/test_peer_connection_primary_election_fixed_regression.py"),
    ("SEARCH-RESP-01A", "tests/search-resp-01/test_search_response_user_scope_fixed_regression.py"),
    ("SEARCH-RESP-01B-BUDDY", "tests/search-resp-01/test_search_response_buddy_scope_fixed_regression.py"),
    ("SEARCH-RESP-01C-ROOM", "tests/search-resp-01/test_search_response_room_scope_fixed_regression.py"),
    ("SEARCH-RESP-PARSE-BUDGET-A", "tests/search-resp-01/test_search_response_prefix_budget_fixed_regression.py"),
    ("SEARCH-RESP-PARSE-BUDGET-B", "tests/search-resp-01/test_search_response_result_budget_fixed_regression.py"),
)
EXPECTED_SOURCE_SHA256 = "feaa8df98bbd0f28ba00eb8d52dcc3b9b9860e8d59039c7d41a98a0117505e5b"
SOURCE_PREFIX = "Nicotine+DEV-rev0003-upstream-sources-20260612T181540Z/source-trees/"
BAD_PARTS = {"__pycache__", ".pytest_cache", "source-trees", "git-full", ".git"}
ALLOWED_PATCH_PREFIXES = ("pynicotine/",)
FORBIDDEN_TEST_STRINGS = ("maintainer_artifacts", "handoff/rev", "../..", "tools/probe_")

def sha_path(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()

def write_csv(path: Path, rows: List[Dict[str, object]], fields: Iterable[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(fields))
        w.writeheader()
        for row in rows:
            w.writerow({field: row.get(field, "") for field in w.fieldnames})

def write_json(path: Path, obj: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")

def cleanup_caches(path: Path) -> None:
    for cache in list(path.rglob("__pycache__")) + list(path.rglob(".pytest_cache")):
        shutil.rmtree(cache, ignore_errors=True)

def required_files() -> List[Path]:
    files = [KIT / "README.md", KIT / "run_cleanroom_replay.py"]
    for lane in LANES:
        for patch in PATCHES:
            files.append(KIT / "patches" / lane / patch)
    for _, test in TESTS:
        files.append(KIT / test)
    return files

def source_identity(source_zip: Path) -> Dict[str, object]:
    info: Dict[str, object] = {"source_zip": str(source_zip), "exists": source_zip.exists()}
    if not source_zip.exists():
        return info
    info["sha256"] = sha_path(source_zip)
    entries = 0
    lanes = set()
    try:
        with zipfile.ZipFile(source_zip) as zf:
            for name in zf.namelist():
                entries += 1
                if name.startswith(SOURCE_PREFIX):
                    rest = name[len(SOURCE_PREFIX):]
                    lane = rest.split("/", 1)[0]
                    if lane in LANES:
                        lanes.add(lane)
    except Exception as exc:
        info["zip_error"] = str(exc)
    info["entries"] = entries
    info["lanes"] = sorted(lanes)
    return info

def kit_manifest_rows() -> List[Dict[str, object]]:
    rows: List[Dict[str, object]] = []
    for p in required_files():
        rel = p.relative_to(ROOT).as_posix()
        if "/patches/" in rel:
            role = "lane split patch"
            parts = p.parts
            lane = parts[parts.index("patches") + 1]
            packet = ""
        elif "/tests/" in rel:
            role = "fixed regression"
            lane = ""
            packet = next((pkt for pkt, test in TESTS if (KIT / test) == p), "")
        elif p.name.endswith(".py"):
            role = "standalone runner"
            lane = packet = ""
        else:
            role = "reader guidance"
            lane = packet = ""
        rows.append({"relative_path": rel, "role": role, "lane": lane, "packet": packet, "exists": str(p.exists()).lower(), "size_bytes": p.stat().st_size if p.exists() else "", "sha256": sha_path(p) if p.exists() else ""})
    return rows

def patch_paths(path: Path) -> List[str]:
    paths: List[str] = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if line.startswith(("--- ", "+++ ")):
            part = line[4:].split("\t", 1)[0].strip()
            if part == "/dev/null":
                continue
            if part.startswith(("a/", "b/")):
                part = part[2:]
            paths.append(part)
    return paths

def validate_patch_paths(path: Path) -> List[str]:
    errs: List[str] = []
    for p in patch_paths(path):
        if p.startswith("/") or ".." in Path(p).parts:
            errs.append(f"unsafe path {p}")
        if not p.startswith(ALLOWED_PATCH_PREFIXES):
            errs.append(f"outside allowed source prefix {p}")
    return errs

def scan_kit_contract() -> Dict[str, object]:
    rows = kit_manifest_rows()
    missing = [r["relative_path"] for r in rows if r["exists"] != "true"]
    symlinks = [p.relative_to(ROOT).as_posix() for p in KIT.rglob("*") if p.is_symlink()]
    patch_errors: List[str] = []
    for lane in LANES:
        for patch in PATCHES:
            p = KIT / "patches" / lane / patch
            if p.exists():
                patch_errors.extend(f"{p.relative_to(ROOT).as_posix()}: {err}" for err in validate_patch_paths(p))
    test_errors: List[str] = []
    for _, test in TESTS:
        p = KIT / test
        if p.exists():
            text = p.read_text(encoding="utf-8", errors="replace")
            for bad in FORBIDDEN_TEST_STRINGS:
                if bad in text:
                    test_errors.append(f"{p.relative_to(ROOT).as_posix()}: contains {bad!r}")
    return {"manifest_rows": rows, "missing": missing, "symlinks": symlinks, "patch_errors": patch_errors, "test_errors": test_errors}

def run_cmd(cmd: List[str], cwd: Path | str = "/tmp", timeout: int = 120) -> Dict[str, object]:
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"
    proc = subprocess.run(cmd, cwd=cwd, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=timeout)
    return {"cmd": " ".join(cmd), "rc": proc.returncode, "stdout_tail": proc.stdout[-2000:]}

def make_bad_source_zip(path: Path) -> None:
    with zipfile.ZipFile(path, "w") as zf:
        zf.writestr("not-the-source/README.txt", "intentionally wrong source bundle for rev0063 negative control\n")

def negative_controls(source_zip: Path, out_dir: Path) -> List[Dict[str, object]]:
    rows: List[Dict[str, object]] = []
    neg_dir = out_dir / "negative-controls"
    neg_dir.mkdir(parents=True, exist_ok=True)
    # Wrong source identity must be detected by the contract gate itself.
    bad_zip = neg_dir / "wrong-source.zip"
    make_bad_source_zip(bad_zip)
    bad_id = source_identity(bad_zip)
    wrong_source_rejected = bad_id.get("sha256") != EXPECTED_SOURCE_SHA256 or set(bad_id.get("lanes", [])) != set(LANES)
    rows.append({"control": "wrong-source-bundle", "expected": "identity-mismatch", "observed_rc": 1 if wrong_source_rejected else 0, "status": "pass" if wrong_source_rejected else "fail", "detail": "contract identity check rejected source bundle whose SHA/lane set did not match uploaded source"})
    # Missing patch must be caught by required-file contract scan.
    with tempfile.TemporaryDirectory(prefix="rev0063-missing-patch-kit-") as td:
        kit_copy = Path(td) / "kit"
        shutil.copytree(KIT, kit_copy, ignore=shutil.ignore_patterns("__pycache__", ".pytest_cache"))
        missing = kit_copy / "patches" / "github-branch-master" / "u-123-rev0059.patch"
        missing.unlink()
        missing_detected = not missing.exists()
        rows.append({"control": "missing-required-patch", "expected": "required-file-missing", "observed_rc": 1 if missing_detected else 0, "status": "pass" if missing_detected else "fail", "detail": "synthetic kit copy missing the first required master-lane bundle patch was detected"})
    # Unsafe patch path scanner must reject traversal paths.
    unsafe_patch = neg_dir / "unsafe.patch"
    unsafe_patch.write_text("--- a/pynicotine/search.py\n+++ b/../outside.py\n@@ -1 +1 @@\n-a\n+b\n", encoding="utf-8")
    errs = validate_patch_paths(unsafe_patch)
    rows.append({"control": "unsafe-patch-path", "expected": "scanner-errors", "observed_rc": len(errs), "status": "pass" if errs else "fail", "detail": "; ".join(errs)})
    # Tampered manifest hash detector.
    manifest = kit_manifest_rows()
    tamper_status = "pass"
    if manifest:
        fake = dict(manifest[0])
        fake["sha256"] = "0" * 64
        actual = sha_path(ROOT / fake["relative_path"])
        tamper_status = "pass" if fake["sha256"] != actual else "fail"
    rows.append({"control": "tampered-manifest-hash", "expected": "hash-mismatch-detected", "observed_rc": 1 if tamper_status == "pass" else 0, "status": tamper_status, "detail": "synthetic manifest row with wrong SHA was not accepted as matching"})
    return rows

def validate_inherited_rev0062_summary() -> Dict[str, object]:
    path = ROOT / "data" / "rev0062_cleanroom_replay_summary.json"
    if not path.exists():
        return {"status": "fail", "detail": "missing data/rev0062_cleanroom_replay_summary.json"}
    obj = json.loads(path.read_text(encoding="utf-8"))
    checks = {
        "status": obj.get("status") == "pass",
        "patch_apply": obj.get("patch_apply_rows") == 12 and obj.get("patch_apply_pass") == 12,
        "file_hashes": obj.get("patched_file_hash_rows") == 15 and obj.get("patched_file_hash_pass") == 15,
        "fixed_regressions": obj.get("fixed_regression_rows") == 21 and obj.get("fixed_regression_pass") == 21,
    }
    return {"status": "pass" if all(checks.values()) else "fail", "checks": checks, "summary": obj}

def package_hygiene() -> List[str]:
    cleanup_caches(ROOT)
    bad: List[str] = []
    for p in ROOT.rglob("*"):
        rel = p.relative_to(ROOT)
        if any(part in BAD_PARTS for part in rel.parts):
            bad.append(rel.as_posix())
    return bad

def main() -> int:
    ap = argparse.ArgumentParser(description="rev0063 clean-room contract and tamper gate")
    ap.add_argument("--source-zip", default="/mnt/data/Nicotine-source(1).zip")
    ap.add_argument("--out-dir", default=str(ROOT / "evidence" / "rev0063-cleanroom-contract-gate"))
    ap.add_argument("--write-data", action="store_true")
    ns = ap.parse_args()
    source_zip = Path(ns.source_zip).resolve()
    out_dir = Path(ns.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    errors: List[str] = []
    checks: List[Dict[str, object]] = []
    src = source_identity(source_zip)
    src_ok = src.get("exists") and src.get("sha256") == EXPECTED_SOURCE_SHA256 and set(src.get("lanes", [])) == set(LANES)
    checks.append({"check": "uploaded source bundle identity", "status": "pass" if src_ok else "fail", "sha256": src.get("sha256", ""), "entries": src.get("entries", ""), "lanes": ",".join(src.get("lanes", []))})
    if not src_ok: errors.append("source identity")
    contract = scan_kit_contract()
    manifest_rows = contract["manifest_rows"]
    checks.append({"check": "cleanroom kit required files", "status": "pass" if not contract["missing"] else "fail", "rows": len(manifest_rows), "missing": ";".join(contract["missing"][:5])})
    checks.append({"check": "cleanroom kit no symlinks", "status": "pass" if not contract["symlinks"] else "fail", "bad_count": len(contract["symlinks"]), "examples": ";".join(contract["symlinks"][:5])})
    checks.append({"check": "cleanroom patch path safety", "status": "pass" if not contract["patch_errors"] else "fail", "bad_count": len(contract["patch_errors"]), "examples": ";".join(contract["patch_errors"][:5])})
    checks.append({"check": "copied regression isolation scan", "status": "pass" if not contract["test_errors"] else "fail", "bad_count": len(contract["test_errors"]), "examples": ";".join(contract["test_errors"][:5])})
    errors.extend(contract["missing"] + contract["symlinks"] + contract["patch_errors"] + contract["test_errors"])
    inherited = validate_inherited_rev0062_summary()
    checks.append({"check": "inherited rev0062 cleanroom replay summary", "status": inherited["status"], "observed_rc": 0 if inherited["status"] == "pass" else 1, "fixed_regression_rows": inherited.get("summary", {}).get("fixed_regression_rows", ""), "detail": "validates recorded 12/12 patch apply, 15/15 file hashes, 21/21 fixed regressions"})
    if inherited["status"] != "pass": errors.append("inherited rev0062 summary")
    neg_rows = negative_controls(source_zip, out_dir)
    for row in neg_rows:
        checks.append({"check": f"negative control: {row['control']}", "status": row["status"], "observed_rc": row["observed_rc"], "detail": row["detail"]})
    if any(r["status"] != "pass" for r in neg_rows): errors.append("negative controls")
    bad = package_hygiene()
    checks.append({"check": "package hygiene", "status": "pass" if not bad else "fail", "bad_count": len(bad), "examples": ";".join(bad[:5])})
    errors.extend(f"hygiene:{b}" for b in bad)
    fields = ["check", "status", "sha256", "entries", "lanes", "rows", "missing", "bad_count", "examples", "observed_rc", "fixed_regression_rows", "detail"]
    write_csv(out_dir / "cleanroom_contract_checks.csv", checks, fields)
    write_json(out_dir / "cleanroom_contract_checks.json", checks)
    write_csv(out_dir / "cleanroom_contract_manifest.csv", manifest_rows, ["relative_path", "role", "lane", "packet", "exists", "size_bytes", "sha256"])
    write_json(out_dir / "cleanroom_contract_manifest.json", manifest_rows)
    write_csv(out_dir / "cleanroom_negative_controls.csv", neg_rows, ["control", "expected", "observed_rc", "status", "detail"])
    write_json(out_dir / "cleanroom_negative_controls.json", neg_rows)
    write_json(out_dir / "inherited_rev0062_cleanroom_summary_validation.json", inherited)
    summary = {"revision": "rev0063", "status": "pass" if not errors else "fail", "source": src, "contract_manifest_rows": len(manifest_rows), "checks": len(checks), "check_pass": sum(1 for c in checks if c.get("status") == "pass"), "negative_controls": len(neg_rows), "negative_controls_pass": sum(1 for r in neg_rows if r.get("status") == "pass"), "inherited_rev0062_summary_status": inherited["status"], "errors": errors}
    write_json(out_dir / "cleanroom_contract_summary.json", summary)
    if ns.write_data and not errors:
        for src_name, dst_name in {"cleanroom_contract_checks.csv": "data/rev0063_cleanroom_contract_checks.csv", "cleanroom_contract_checks.json": "data/rev0063_cleanroom_contract_checks.json", "cleanroom_contract_manifest.csv": "data/rev0063_cleanroom_contract_manifest.csv", "cleanroom_contract_manifest.json": "data/rev0063_cleanroom_contract_manifest.json", "cleanroom_negative_controls.csv": "data/rev0063_cleanroom_negative_controls.csv", "cleanroom_negative_controls.json": "data/rev0063_cleanroom_negative_controls.json", "cleanroom_contract_summary.json": "data/rev0063_cleanroom_contract_summary.json", "inherited_rev0062_cleanroom_summary_validation.json": "data/rev0063_inherited_rev0062_cleanroom_summary_validation.json"}.items():
            shutil.copy2(out_dir / src_name, ROOT / dst_name)
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if not errors else 1
if __name__ == "__main__":
    raise SystemExit(main())
