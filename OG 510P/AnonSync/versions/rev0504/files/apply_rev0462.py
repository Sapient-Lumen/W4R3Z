from pathlib import Path

ROOT = Path(__file__).resolve().parent
DOCS = ROOT / "docs"

new_docs = [
    "1912-resilio-remedy-hardening-attestation-subscriber-invalidation-freshness-leases-and-tombstone-recall-fragmentation-evaluation.md",
    "1913-remedy-hardening-attestation-subscriber-invalidation-contract-sheet-page-freshness-lease-and-tombstone-policy-interface-spec.md",
    "1914-remedy-hardening-attestation-subscriber-invalidation-review-page-which-subscribers-or-caches-might-still-serve-stale-truth-interface-spec.md",
    "1915-remedy-hardening-attestation-subscriber-invalidation-proof-page-version-token-lease-matrix-and-stale-serve-blockers-interface-spec.md",
    "1916-remedy-hardening-attestation-subscriber-invalidation-timeline-page-version-issue-revalidate-expiry-and-tombstone-events-interface-spec.md",
    "1917-remedy-hardening-attestation-subscriber-invalidation-lineage-receipt-page-freshness-scope-and-blocked-machine-overstatement-interface-spec.md",
]

print("rev0462 adds the following docs:")
for name in new_docs:
    path = DOCS / name
    print(f"- {name}: {'present' if path.exists() else 'missing'}")
