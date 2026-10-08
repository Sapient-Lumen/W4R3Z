#!/usr/bin/env python3
"""Generate Track A minimum-viable-release checklist.

Inputs:
  - artifacts/proof_obligations/proof-obligations.csv
  - artifacts/claims/claim-evidence-matrix.csv
  - artifacts/hazards/hazard-register.csv

Output:
  - docs/track-a/MVR_CHECKLIST.md
"""

from __future__ import annotations

from pathlib import Path
import csv
import re

ROOT = Path(__file__).resolve().parents[1]

PO_CSV = ROOT / "artifacts" / "proof_obligations" / "proof-obligations.csv"
CLAIMS_CSV = ROOT / "artifacts" / "claims" / "claim-evidence-matrix.csv"
HAZARDS_CSV = ROOT / "artifacts" / "hazards" / "hazard-register.csv"

OUT_MD = ROOT / "docs" / "track-a" / "MVR_CHECKLIST.md"

def split_ids(s: str) -> list[str]:
    if not s:
        return []
    return [x.strip() for x in re.split(r"[;,]", s) if x.strip()]

def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))

def main() -> int:
    po_rows = read_csv(PO_CSV)
    claim_rows = read_csv(CLAIMS_CSV)
    hazard_rows = read_csv(HAZARDS_CSV)

    # Build mappings
    po_to_claims: dict[str, list[str]] = {}
    po_to_evidence: dict[str, set[str]] = {}
    for row in claim_rows:
        track = row.get("Track", "")
        if not track.startswith("A"):
            continue
        claim_id = row.get("ClaimID", "").strip()
        for po in split_ids(row.get("ProofObligations", "")):
            po_to_claims.setdefault(po, []).append(claim_id)
            for tok in (row.get("EvidenceArtifacts", "") or "").split(";"):
                t = tok.strip()
                if t:
                    po_to_evidence.setdefault(po, set()).add(t)

    po_to_hazards: dict[str, list[str]] = {}
    for row in hazard_rows:
        track = row.get("Track", "")
        if not track.startswith("A"):
            continue
        hz_id = row.get("HazardID", "").strip()
        for po in split_ids(row.get("LinkedProofObligations", "")):
            po_to_hazards.setdefault(po, []).append(hz_id)

    # Choose POs that gate Track A:
    gating = []
    for row in po_rows:
        po_id = row.get("ProofObligationID", "").strip()
        track = row.get("Track", "").strip()
        if track not in ("A (Deployable core)", "Shared"):
            continue
        if po_id in po_to_claims or po_id in po_to_hazards or po_id.startswith("PO-00"):
            gating.append(row)

    # Sort by numeric id
    def po_key(r):
        m = re.search(r"(\d+)$", r.get("ProofObligationID", ""))
        return int(m.group(1)) if m else 999999
    gating.sort(key=po_key)

    lines = []
    lines.append("# Track A — Minimum viable release checklist")
    lines.append("")
    lines.append("> **Generated file.** Source of truth inputs:")
    lines.append("> - `artifacts/proof_obligations/proof-obligations.csv`")
    lines.append("> - `artifacts/claims/claim-evidence-matrix.csv`")
    lines.append("> - `artifacts/hazards/hazard-register.csv`")
    lines.append("")
    lines.append("This checklist defines the **smallest set of proof obligations (POs)** that a Track A release must satisfy.")
    lines.append("If any item is 'no', the release is not claimable.")
    lines.append("")
    lines.append("See also: `docs/159-proof-obligations-ledger.md` and `docs/164-proof-obligations-registry.md`.")
    lines.append("")
    lines.append("## Gate conditions (POs)")
    lines.append("")
    for row in gating:
        po_id = row.get("ProofObligationID","").strip()
        title = row.get("Title","").strip()
        stmt = row.get("Statement","").strip()
        lines.append(f"### ☐ {po_id} — {title}")
        if stmt:
            lines.append(f"- **Must be provable:** {stmt}")
        claims = po_to_claims.get(po_id, [])
        hazards = po_to_hazards.get(po_id, [])
        if claims:
            lines.append(f"- **Linked claims:** " + ", ".join(sorted(set(claims))))
        if hazards:
            lines.append(f"- **Linked hazards:** " + ", ".join(sorted(set(hazards))))
        ev = sorted(po_to_evidence.get(po_id, set()))
        if ev:
            lines.append("- **Evidence artifacts (from linked claims):**")
            for tok in ev:
                lines.append(f"  - `{tok}`")
        lines.append("")

    lines.append("## Release notes template")
    lines.append("")
    lines.append("When cutting a release, include:")
    lines.append("- Scope/track statement (Track A claims only)")
    lines.append("- Evidence bundle contract version(s)")
    lines.append("- Tooling versions and verifier bundle hash")
    lines.append("- Any known gaps and the hazards they map to")
    lines.append("")

    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
