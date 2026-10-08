from pathlib import Path

ROOT = Path(__file__).resolve().parent
DOCS = ROOT / "docs"

new_docs = [
    "1906-resilio-remedy-hardening-attestation-surface-claim-governance-audience-scoped-publication-and-stale-claim-recall-fragmentation-evaluation.md",
    "1907-remedy-hardening-attestation-surface-claim-governance-contract-sheet-page-audience-budget-and-export-policy-interface-spec.md",
    "1908-remedy-hardening-attestation-surface-claim-review-page-what-may-this-surface-honestly-say-or-export-right-now-interface-spec.md",
    "1909-remedy-hardening-attestation-surface-claim-proof-page-sentence-budget-blocked-phrases-and-cross-surface-consistency-interface-spec.md",
    "1910-remedy-hardening-attestation-surface-claim-timeline-page-publication-downgrade-recall-and-supersession-events-interface-spec.md",
    "1911-remedy-hardening-attestation-surface-claim-lineage-receipt-page-audience-scope-export-budget-and-blocked-overstatement-interface-spec.md",
]

print("rev0461 adds the following docs:")
for name in new_docs:
    path = DOCS / name
    print(f"- {name}: {'present' if path.exists() else 'missing'}")
