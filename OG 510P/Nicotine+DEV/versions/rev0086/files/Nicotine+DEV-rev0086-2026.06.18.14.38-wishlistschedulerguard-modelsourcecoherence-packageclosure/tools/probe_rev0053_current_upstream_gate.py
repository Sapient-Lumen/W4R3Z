#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import zipfile
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {
    "U-123",
    "PB-01",
    "SEARCH-RESP-01A",
    "SEARCH-RESP-01B-BUDDY",
    "SEARCH-RESP-01C-ROOM",
    "SEARCH-RESP-PARSE-BUDGET-A",
    "SEARCH-RESP-PARSE-BUDGET-B",
}
LANES = ["github-tag-3.3.10", "github-branch-3.3.x", "github-branch-master"]
BAD = {"__pycache__", ".pytest_cache", "source-trees", "git-full", ".git"}
MARKERS = {
    "U-123": [
        ("pynicotine/transfers.py", "active_transfer is transfer"),
        ("pynicotine/transfers.py", "deactivated = False"),
        ("pynicotine/downloads.py", "Rejected duplicate download request"),
        ("pynicotine/downloads.py", "active_download is not None and active_download is not download"),
    ],
    "PB-01": [
        ("pynicotine/slskproto.py", "Rejecting replacement connection"),
        ("pynicotine/slskproto.py", "keeping established primary connection"),
        ("pynicotine/slskproto.py", "if not self._replace_existing_connection(init):"),
    ],
    "SEARCH-RESP-01A": [
        ("pynicotine/search.py", "expected_users = search.users"),
        ("pynicotine/search.py", "username not in expected_users"),
    ],
    "SEARCH-RESP-01B-BUDDY": [
        ("pynicotine/search.py", "users = tuple(core.buddies.users)"),
        ("pynicotine/search.py", 'search.mode == "buddies" and search.users is not None'),
    ],
    "SEARCH-RESP-01C-ROOM": [
        ("pynicotine/search.py", "room_obj = getattr"),
        ("pynicotine/search.py", 'search.mode == "rooms" and search.users is not None'),
    ],
    "SEARCH-RESP-PARSE-BUDGET-A": [
        ("pynicotine/slskmessages.py", "MAX_SEARCH_RESPONSE_USERNAME_LENGTH"),
        ("pynicotine/slskmessages.py", "username_len > MAX_SEARCH_RESPONSE_USERNAME_LENGTH"),
    ],
    "SEARCH-RESP-PARSE-BUDGET-B": [
        ("pynicotine/slskmessages.py", "MAX_SEARCH_RESPONSE_RESULT_COUNT"),
        ("pynicotine/slskmessages.py", "accepted_result_count > MAX_SEARCH_RESPONSE_RESULT_COUNT"),
        ("pynicotine/slskmessages.py", "max_results=MAX_SEARCH_RESPONSE_RESULT_COUNT"),
    ],
}


def rows(rel: str) -> List[Dict[str, str]]:
    with (ROOT / rel).open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def manifest(rel: str) -> List[str]:
    errors: List[str] = []
    path = ROOT / rel
    if not path.exists():
        return [f"missing {rel}"]
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            want, r = line.split("  ", 1)
        except ValueError:
            errors.append(f"bad manifest line in {rel}: {line!r}")
            continue
        q = ROOT / r
        if not q.exists():
            errors.append(f"missing {r}")
        elif sha(q) != want:
            errors.append(f"hash {r}")
    return errors


def hygiene() -> List[str]:
    bad: List[str] = []
    for p in ROOT.rglob("*"):
        parts = p.relative_to(ROOT).parts
        if any(part in BAD for part in parts):
            bad.append(str(p.relative_to(ROOT)))
    return bad


def summarize(scans: List[Dict[str, object]]) -> Dict[str, object]:
    return {
        "rows": len(scans),
        "lanes": sorted({str(s["lane"]) for s in scans}),
        "packets": sorted({str(s["packet"]) for s in scans}),
        "total_markers_present": sum(len(s["present"]) for s in scans),
        "total_markers_missing": sum(len(s["missing"]) for s in scans),
        "examples": scans[:3],
    }


def scan_zip(zippath: Path, expect_archived: bool = False) -> Tuple[List[Dict[str, object]], List[str]]:
    scans: List[Dict[str, object]] = []
    errors: List[str] = []
    with zipfile.ZipFile(zippath) as zf:
        idx: Dict[Tuple[str, str], str] = {}
        for n in zf.namelist():
            if "/source-trees/" in n and "/pynicotine/" in n:
                tail = n.split("/source-trees/", 1)[1]
                parts = tail.split("/", 2)
                if len(parts) == 3 and parts[1] == "pynicotine":
                    idx[(parts[0], "pynicotine/" + parts[2])] = n
        for lane in LANES:
            for packet, specs in MARKERS.items():
                present: List[str] = []
                missing: List[str] = []
                for rel, marker in specs:
                    n = idx.get((lane, rel))
                    if not n:
                        missing.append(f"{rel}::<source file missing>")
                        continue
                    txt = zf.read(n).decode("utf-8", "replace")
                    (present if marker in txt else missing).append(f"{rel}::{marker}")
                scans.append({"lane": lane, "packet": packet, "present": present, "missing": missing})
                if expect_archived and present:
                    errors.append(f"archived baseline unexpectedly contains selected marker {lane} {packet}")
    return scans, errors


def lane_roots(source_dir: Path) -> Dict[str, Path]:
    roots: Dict[str, Path] = {}
    if (source_dir / "pynicotine").is_dir():
        roots["current-checkout"] = source_dir
    for lane in LANES:
        direct = source_dir / "source-trees" / lane
        if (direct / "pynicotine").is_dir():
            roots[lane] = direct
    if not roots:
        for lane in LANES:
            matches = [p.parent for p in source_dir.rglob(f"source-trees/{lane}/pynicotine")]
            if matches:
                roots[lane] = matches[0]
    return roots


def scan_dir(source_dir: Path, expect_archived: bool = False) -> Tuple[List[Dict[str, object]], List[str]]:
    scans: List[Dict[str, object]] = []
    errors: List[str] = []
    roots = lane_roots(source_dir)
    if not roots:
        return scans, [f"no recognizable Nicotine+ source root under {source_dir}"]
    for lane, base in sorted(roots.items()):
        for packet, specs in MARKERS.items():
            present: List[str] = []
            missing: List[str] = []
            for rel, marker in specs:
                p = base / rel
                if not p.exists():
                    missing.append(f"{rel}::<source file missing>")
                    continue
                txt = p.read_text(encoding="utf-8", errors="replace")
                (present if marker in txt else missing).append(f"{rel}::{marker}")
            scans.append({"lane": lane, "packet": packet, "present": present, "missing": missing})
            if expect_archived and lane in LANES and present:
                errors.append(f"archived baseline unexpectedly contains selected marker {lane} {packet}")
    return scans, errors


def main() -> int:
    ap = argparse.ArgumentParser(description="rev0053 current-upstream checkout gate helper")
    ap.add_argument("--source-zip", help="Optional provided source-bundle zip to scan for selected-patch markers")
    ap.add_argument("--source-dir", help="Optional fresh checkout or extracted source bundle to scan for selected-patch markers")
    ap.add_argument("--expect-archived-baseline", action="store_true", help="Fail if archived lane scans already contain selected-patch markers")
    args = ap.parse_args()

    checks: List[Dict[str, object]] = []
    errors: List[str] = []

    gates = rows("data/rev0053_checkout_gate_matrix.csv")
    packets = {r["packet"] for r in gates}
    ok = packets == EXPECTED and len(gates) == 7
    checks.append({"check": "packet gate set", "status": "pass" if ok else "fail", "rows": len(gates)})
    if not ok:
        errors.append("packet set mismatch")

    for rel, expected in [
        ("data/rev0053_source_refresh_contract.csv", 9),
        ("data/rev0053_public_context.csv", 5),
        ("data/rev0053_checkout_gate_refactor.csv", 6),
        ("data/rev0053_strict_promotions.csv", 7),
        ("data/rev0052_filing_field_map.csv", 7),
    ]:
        r = rows(rel)
        ok = len(r) == expected
        checks.append({"check": rel, "status": "pass" if ok else "fail", "rows": len(r), "expected": expected})
        if not ok:
            errors.append(f"{rel} count")

    missing_refs: List[str] = []
    for r in gates:
        for fld in ["field_capsule", "claim_capsule", "source_anchor_capsule", "maintainer_report", "regression_artifact"]:
            for ref in [x for x in r[fld].split(";") if x]:
                if not (ROOT / ref).exists():
                    missing_refs.append(f"{r['packet']}:{fld}:{ref}")
    checks.append({"check": "artifact refs", "status": "pass" if not missing_refs else "fail", "missing": missing_refs[:10]})
    errors.extend(missing_refs)

    for rel in ["handoff/rev0053/MANIFEST.sha256", "handoff/rev0052/MANIFEST.sha256"]:
        e = manifest(rel)
        checks.append({"check": rel, "status": "pass" if not e else "fail", "errors": e[:5]})
        errors.extend(e)

    bad = hygiene()
    checks.append({"check": "package hygiene", "status": "pass" if not bad else "fail", "bad_count": len(bad), "examples": bad[:8]})
    errors.extend(f"hygiene:{x}" for x in bad)

    source_scan_summary = None
    if args.source_zip:
        scans, scan_errors = scan_zip(Path(args.source_zip), args.expect_archived_baseline)
        source_scan_summary = summarize(scans)
        checks.append({"check": "optional source-zip marker scan", "status": "pass" if not scan_errors else "fail", **source_scan_summary})
        errors.extend(scan_errors)
    else:
        checks.append({"check": "optional source-zip marker scan", "status": "skipped"})

    source_dir_summary = None
    if args.source_dir:
        scans, scan_errors = scan_dir(Path(args.source_dir), args.expect_archived_baseline)
        source_dir_summary = summarize(scans)
        checks.append({"check": "optional source-dir marker scan", "status": "pass" if not scan_errors else "fail", **source_dir_summary})
        errors.extend(scan_errors)
    else:
        checks.append({"check": "optional source-dir marker scan", "status": "skipped"})

    out = {
        "revision": "rev0053",
        "status": "pass" if not errors else "fail",
        "checks": checks,
        "source_zip_scan_summary": source_scan_summary,
        "source_dir_scan_summary": source_dir_summary,
        "errors": errors,
    }
    print(json.dumps(out, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
