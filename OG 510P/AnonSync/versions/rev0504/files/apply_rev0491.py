from pathlib import Path

# This helper records the rev0491 tranche additions.
# It is intentionally lightweight because the archive already contains the fully materialized files.

ADDED = [
    'docs/2086-resilio-remedy-hardening-attestation-successor-beneficiary-adoption-stale-reliance-and-corrected-working-state-fragmentation-evaluation.md',
    'docs/2087-remedy-hardening-attestation-successor-beneficiary-adoption-contract-sheet-page-required-uptake-class-working-pointer-and-stale-reliance-ceiling-interface-spec.md',
    'docs/2088-remedy-hardening-attestation-successor-beneficiary-adoption-review-page-did-the-beneficiary-actually-switch-to-the-corrected-working-state-interface-spec.md',
    'docs/2089-remedy-hardening-attestation-successor-beneficiary-adoption-proof-page-adoption-trace-stale-artifact-ledger-and-uptake-sentence-ceiling-interface-spec.md',
    'docs/2090-remedy-hardening-attestation-successor-beneficiary-adoption-timeline-page-correction-seen-acknowledged-opened-switched-retired-and-relapsed-events-interface-spec.md',
    'docs/2091-remedy-hardening-attestation-successor-beneficiary-adoption-lineage-receipt-page-adoption-summary-stale-reliance-risk-and-blocked-stronger-uptake-sentences-interface-spec.md',
]

UPDATED_PREFIXED = [
    'README.md',
    'docs/00-status.md',
    'docs/10-resilio-sync-evaluation.md',
    'docs/20-product-direction.md',
    'docs/sources.md',
]

if __name__ == '__main__':
    for rel in ADDED + UPDATED_PREFIXED:
        print(rel)
