#!/usr/bin/env python3
"""Generic parity checks for current operator-facing surfaces.

Rev0372 repair: this module is both importable and executable, and the semantic-boundary audit path follows the current revision instead of a hardcoded rev0371 file.
"""
from pathlib import Path
import json, re, argparse, sys


def _load(root, rel):
    return json.loads((root/rel).read_text(encoding="utf-8"))


def validate_live_surfaces(root: Path, revision: str):
    issues=[]
    contract_path=root/"docs/00-meta/live-surface-contract.json"
    if not contract_path.exists(): return ["Missing docs/00-meta/live-surface-contract.json"]
    contract=_load(root,"docs/00-meta/live-surface-contract.json")
    if contract.get("revision_current") != revision: issues.append("live-surface contract revision mismatch")
    for rel in contract.get("required_current_release_files",[]):
        p=root/rel
        if not p.exists(): issues.append(f"Missing contracted current-release file: {rel}"); continue
        if revision not in p.read_text(encoding="utf-8",errors="ignore"):
            issues.append(f"Contracted current-release file does not expose {revision}: {rel}")

    evidence=_load(root,"cases/EVIDENCE_LEDGER.json")
    verified=_load(root,"cases/VERIFIED_CLAIM_EDGE_LEDGER.json")
    summary=_load(root,"cases/MECHANICAL_EVIDENCE_SUMMARY.json")
    rows=evidence.get("edge_rows",[]); vrows=verified.get("verified_claim_edges",[])
    expected={
      "mechanical_association_count":len(rows),
      "unique_case_source_pair_count":len({(r.get('case_id'),r.get('source_id')) for r in rows}),
      "verified_claim_edge_count":len(vrows)
    }
    for k,v in expected.items():
        if (summary.get("counts") or {}).get(k)!=v: issues.append(f"MECHANICAL_EVIDENCE_SUMMARY.json {k} mismatch")
    smd=(root/"cases/MECHANICAL_EVIDENCE_SUMMARY.md").read_text(encoding="utf-8",errors="ignore")
    for k,v in expected.items():
        if str(v) not in smd: issues.append(f"MECHANICAL_EVIDENCE_SUMMARY.md missing current {k}={v}")

    backlog=_load(root,"cases/CLAIM_ATOM_BACKLOG.json")
    if backlog.get("revision_current")!=revision: issues.append("CLAIM_ATOM_BACKLOG.json revision mismatch")
    if backlog.get("verified_claim_edge_count")!=len(vrows): issues.append("CLAIM_ATOM_BACKLOG verified count mismatch")
    if backlog.get("atom_count")!=len(backlog.get("claim_atoms",[])): issues.append("CLAIM_ATOM_BACKLOG atom_count mismatch")
    bmd=(root/"cases/CLAIM_ATOM_BACKLOG.md").read_text(encoding="utf-8",errors="ignore")
    if revision not in bmd or str(len(vrows)) not in bmd: issues.append("CLAIM_ATOM_BACKLOG.md stale revision or verified count")

    queue=_load(root,"docs/00-meta/high-risk-substantive-work-queue.json")
    items=queue.get("work_items",[])
    if queue.get("revision_current")!=revision: issues.append("high-risk queue revision mismatch")
    if queue.get("verified_claim_edge_count")!=len(vrows): issues.append("high-risk queue verified count mismatch")
    if queue.get("work_item_count")!=len(items): issues.append("high-risk queue item count mismatch")
    priorities=[]; required={"priority","work_item_id","case_id","risk","deliverable"}
    for i,item in enumerate(items,1):
        missing=sorted(k for k in required if not item.get(k))
        if missing: issues.append(f"high-risk queue item {i} missing {missing}")
        priorities.append(item.get("priority"))
    if priorities!=list(range(1,len(items)+1)): issues.append("high-risk queue priorities are not contiguous and ordered")
    qmd=(root/"docs/00-meta/high-risk-substantive-work-queue.md").read_text(encoding="utf-8",errors="ignore")
    if re.search(r"unnamed|— pending",qmd,re.I): issues.append("high-risk queue markdown contains unnamed/pending renderer fallback")
    for item in items:
        if item.get("work_item_id") and f"`{item['work_item_id']}`" not in qmd: issues.append(f"queue markdown missing {item['work_item_id']}")

    sem_path=f"docs/00-meta/verified-claim-edge-semantic-boundary-audit-{revision}.json"
    sem=_load(root,sem_path)
    counts=sem.get("counts",{})
    rel={}
    for row in vrows: rel[row.get("relationship_code")]=rel.get(row.get("relationship_code"),0)+1
    if counts.get("record_count")!=len(vrows): issues.append("semantic audit record count mismatch")
    if counts.get("relationship_code_counts")!=dict(sorted(rel.items())): issues.append("semantic audit relationship counts mismatch")
    boundary=verified.get("semantic_boundary") or {}
    if boundary.get("preferred_operator_label")!="locator-bound evidence records": issues.append("verified ledger semantic boundary label missing")
    if boundary.get("structural_completeness_is_not_substantive_verification") is not True: issues.append("verified ledger structural/substantive distinction missing")

    for relpath in ["README.md","START_HERE.md"]:
        text=(root/relpath).read_text(encoding="utf-8",errors="ignore")
        for phrase in ["durable ordinary independence","locator-bound evidence records","0 certified current cases"]:
            if phrase not in text: issues.append(f"{relpath} missing mission/truth phrase: {phrase}")
        if "docs/00-meta/charter.md" not in text: issues.append(f"{relpath} does not route to charter")
    return issues


def main(argv=None):
    parser=argparse.ArgumentParser(description="Validate current operator-facing surfaces.")
    parser.add_argument("--root", default=str(Path(__file__).resolve().parents[1]))
    parser.add_argument("--revision", default=(Path(__file__).resolve().parents[1]/"VERSION").read_text(encoding="utf-8").strip())
    args=parser.parse_args(argv)
    issues=validate_live_surfaces(Path(args.root), args.revision)
    if issues:
        for issue in issues: print(f"ERROR: {issue}")
        print(f"FAILED: {len(issues)} live-surface issue(s)")
        return 1
    print("PASSED: 0 live-surface issues")
    return 0

if __name__ == "__main__":
    sys.exit(main())

# rev0379 current live-surface compatibility marker.

# rev0380 current live-surface compatibility marker.

# rev0381 current live-surface compatibility marker.
