from pathlib import Path

# This helper records the rev0490 tranche additions.
# It is intentionally lightweight because the archive already contains the fully materialized files.

ADDED = [
    'docs/2080-resilio-remedy-hardening-attestation-successor-beneficiary-notice-acknowledgement-and-correction-uptake-fragmentation-evaluation.md',
    'docs/2081-remedy-hardening-attestation-successor-beneficiary-notice-contract-sheet-page-correction-notice-carrier-acknowledgement-requirement-and-uptake-ceiling-interface-spec.md',
    'docs/2082-remedy-hardening-attestation-successor-beneficiary-notice-review-page-did-the-beneficiary-notice-and-acknowledge-this-later-canonical-correction-interface-spec.md',
    'docs/2083-remedy-hardening-attestation-successor-beneficiary-notice-proof-page-notice-trace-acknowledgement-ledger-and-uptake-sentence-ceiling-interface-spec.md',
    'docs/2084-remedy-hardening-attestation-successor-beneficiary-notice-timeline-page-correction-published-delivered-surfaced-seen-acknowledged-reminded-and-expired-events-interface-spec.md',
    'docs/2085-remedy-hardening-attestation-successor-beneficiary-notice-lineage-receipt-page-notice-acknowledgement-summary-and-blocked-stronger-uptake-sentences-interface-spec.md',
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
