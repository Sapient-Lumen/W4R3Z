#!/usr/bin/env python3
"""Audit semantic boundaries in the historical VERIFIED_CLAIM_EDGE ledger.

The tool distinguishes structural completeness from independent verification.
It does not automatically reclassify records; heuristic candidate lists require human review.
"""
from pathlib import Path
import argparse, collections, json, re, sys

ROOT = Path(__file__).resolve().parents[1]
LOC_RE = re.compile(r"\b(synthesis|combined|derived cross-source|taken together|gate\s*\d|rev\d{4})\b", re.I)
CLAIM_RE = re.compile(r"\b(archive|cube|needs?|requires?|should|must|acceptance test|certification boundary)\b", re.I)
REQUIRED = ["verified_claim_edge_id","case_id","bounded_claim","relationship_code","source_ids","exact_locator","does_not_prove","contrary_or_qualifying_evidence_needed","reversal_rule","verification_status"]


def build_audit():
    ledger = json.loads((ROOT/"cases/VERIFIED_CLAIM_EDGE_LEDGER.json").read_text(encoding="utf-8"))
    rows = ledger.get("verified_claim_edges", [])
    receipt = json.loads((ROOT/"REVISION-RECEIPT.json").read_text(encoding="utf-8"))
    missing=[]
    for row in rows:
        for key in REQUIRED:
            if not row.get(key): missing.append({"record_id":row.get("verified_claim_edge_id"),"field":key})
    rel=collections.Counter(r.get("relationship_code") for r in rows)
    review_keys=sorted({k for r in rows for k in r if "review" in k.lower()})
    synthesis=[r.get("verified_claim_edge_id") for r in rows if LOC_RE.search(str(r.get("exact_locator", "")))]
    normative=[r.get("verified_claim_edge_id") for r in rows if CLAIM_RE.search(str(r.get("bounded_claim", "")))]
    return {
      "revision_current": receipt["revision"],
      "generated_at": receipt["generated_at"],
      "status": "semantic_risk_audit_not_independent_verification",
      "preferred_operator_label": "locator-bound evidence records",
      "historical_ledger_filename_retained": "cases/VERIFIED_CLAIM_EDGE_LEDGER.json",
      "counts": {
        "record_count": len(rows),
        "case_count": len({r.get("case_id") for r in rows}),
        "relationship_code_counts": dict(sorted(rel.items())),
        "contradict_record_count": rel.get("contradicts", 0),
        "single_source_record_count": sum(1 for r in rows if len(r.get("source_ids") or []) == 1),
        "multi_source_record_count": sum(1 for r in rows if len(r.get("source_ids") or []) > 1),
        "missing_source_url_record_count": sum(1 for r in rows if not r.get("source_url")),
        "missing_extraction_type_record_count": sum(1 for r in rows if not r.get("extraction_type")),
        "structurally_missing_required_field_count": len(missing),
        "review_metadata_key_count": len(review_keys),
        "independently_reviewed_record_count": 0,
        "synthesis_locator_review_candidate_count": len(synthesis),
        "archive_or_normative_claim_review_candidate_count": len(normative)
      },
      "review_metadata_keys_found": review_keys,
      "synthesis_locator_review_candidate_ids": synthesis,
      "archive_or_normative_claim_review_candidate_ids": normative,
      "structurally_missing_required_fields": missing,
      "interpretation": [
        "Nonempty fields establish structural completeness only.",
        "Heuristic candidate lists are triage signals and require human adjudication.",
        "Multi-source synthesis and archive-authored normative inference should not be labeled as direct source observation.",
        "Zero contradict records and zero independent review metadata are material confirmation-risk signals."
      ]
    }


def write_outputs(audit):
    j=ROOT/"docs/00-meta/verified-claim-edge-semantic-boundary-audit-rev0371.json"
    m=ROOT/"docs/00-meta/verified-claim-edge-semantic-boundary-audit-rev0371.md"
    j.write_text(json.dumps(audit,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    c=audit["counts"]
    lines=[
      "---",f"revision_current: {audit['revision_current']}",f"generated_at: {audit['generated_at']}",
      "title: Verified-claim-edge semantic boundary audit","status: semantic_risk_audit_not_independent_verification","---","",
      "# Semantic boundary audit", "",
      "The historical filename is retained for compatibility. The preferred operator term is **locator-bound evidence records**.","",
      f"- records: **{c['record_count']}** across **{c['case_count']}** cases",
      f"- relationship codes: `{json.dumps(c['relationship_code_counts'], sort_keys=True)}`",
      f"- contradict records: **{c['contradict_record_count']}**",
      f"- independently reviewed records: **{c['independently_reviewed_record_count']}**",
      f"- multi-source records: **{c['multi_source_record_count']}**",
      f"- synthesis-locator review candidates: **{c['synthesis_locator_review_candidate_count']}**",
      f"- archive/normative-claim review candidates: **{c['archive_or_normative_claim_review_candidate_count']}**",
      f"- missing source_url: **{c['missing_source_url_record_count']}**; missing extraction_type: **{c['missing_extraction_type_record_count']}**", "",
      "A structurally complete row is not automatically a substantively verified claim. Candidate lists are heuristic triage and require human review.","",
      "## Synthesis-locator candidates", ""
    ]
    lines += [f"- `{x}`" for x in audit["synthesis_locator_review_candidate_ids"]]
    lines += ["", "## Archive/normative-claim candidates", ""]
    lines += [f"- `{x}`" for x in audit["archive_or_normative_claim_review_candidate_ids"]]
    m.write_text("\n".join(lines)+"\n",encoding="utf-8")


def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--write",action="store_true"); args=ap.parse_args()
    audit=build_audit()
    if args.write: write_outputs(audit)
    print(json.dumps(audit["counts"],sort_keys=True))
    if audit["counts"]["structurally_missing_required_field_count"]: sys.exit(1)

if __name__=="__main__": main()
