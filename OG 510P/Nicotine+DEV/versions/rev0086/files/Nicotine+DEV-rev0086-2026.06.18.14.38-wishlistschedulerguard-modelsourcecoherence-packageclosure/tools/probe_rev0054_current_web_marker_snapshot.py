#!/usr/bin/env python3
from __future__ import annotations
import csv, json, hashlib, argparse
from pathlib import Path
from typing import List, Dict

ROOT = Path(__file__).resolve().parents[1]
REV = "rev0054"
EXPECTED_PACKETS = {
    "U-123", "PB-01", "SEARCH-RESP-01A", "SEARCH-RESP-01B-BUDDY", "SEARCH-RESP-01C-ROOM",
    "SEARCH-RESP-PARSE-BUDGET-A", "SEARCH-RESP-PARSE-BUDGET-B"
}
BAD = {"__pycache__", ".pytest_cache", "source-trees", "git-full", ".git"}

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
    bad=[]
    for p in ROOT.rglob("*"):
        parts=p.relative_to(ROOT).parts
        if any(part in BAD for part in parts):
            bad.append(str(p.relative_to(ROOT)))
    return bad

def main() -> int:
    ap=argparse.ArgumentParser(description="rev0054 current-web marker snapshot gate helper")
    ap.parse_args()
    checks=[]; errors=[]

    snap=rows("data/rev0054_current_web_marker_snapshot.csv")
    packets={r["packet"] for r in snap}
    branches={r["web_branch"] for r in snap}
    total_present=sum(int(r["selected_markers_present"]) for r in snap)
    total_missing=sum(int(r["selected_markers_missing"]) for r in snap)
    total_markers=sum(int(r["selected_markers_total"]) for r in snap)
    ok=len(snap)==14 and packets==EXPECTED_PACKETS and branches=={"master","3.3.x"} and total_present==2 and total_missing==34 and total_markers==36
    checks.append({"check":"rev0054 web marker snapshot shape","status":"pass" if ok else "fail","rows":len(snap),"packets":sorted(packets),"branches":sorted(branches),"present":total_present,"missing":total_missing,"total":total_markers})
    if not ok: errors.append("web marker snapshot shape")

    for rel, expected in [
        ("data/rev0054_current_public_context.csv", 7),
        ("data/rev0054_web_marker_refactor.csv", 6),
        ("data/rev0054_ranked_audit_queue.csv", 5),
        ("data/rev0054_strict_promotions.csv", 7),
        ("data/rev0054_revision_metadata.csv", 10),
        ("data/rev0053_checkout_gate_matrix.csv", 7),
        ("data/rev0052_filing_field_map.csv", 7),
    ]:
        r=rows(rel)
        ok=len(r)==expected
        checks.append({"check":rel,"status":"pass" if ok else "fail","rows":len(r),"expected":expected})
        if not ok: errors.append(f"{rel} count")

    pre=ROOT/"evidence/rev0054-inherited-rev0053-gate-rerun.json"
    if pre.exists():
        data=json.loads(pre.read_text(encoding="utf-8"))
        ok=data.get("status")=="pass"
        checks.append({"check":"inherited rev0053 helper rerun","status":"pass" if ok else "fail"})
        if not ok: errors.append("inherited helper status")
    else:
        checks.append({"check":"inherited rev0053 helper rerun","status":"fail","error":"missing"})
        errors.append("missing inherited helper")

    for rel in ["handoff/rev0054/MANIFEST.sha256", "handoff/rev0053/MANIFEST.sha256", "handoff/rev0052/MANIFEST.sha256"]:
        e=manifest(rel)
        checks.append({"check":rel,"status":"pass" if not e else "fail","errors":e[:5]})
        errors.extend(e)

    bad=hygiene()
    checks.append({"check":"package hygiene","status":"pass" if not bad else "fail","bad_count":len(bad),"examples":bad[:8]})
    errors.extend(f"hygiene:{x}" for x in bad)

    out={"revision":REV,"status":"pass" if not errors else "fail","checks":checks,"errors":errors}
    print(json.dumps(out, indent=2))
    return 0 if not errors else 1
if __name__ == "__main__":
    raise SystemExit(main())
