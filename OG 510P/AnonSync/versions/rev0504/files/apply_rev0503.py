from pathlib import Path

ROOT = Path(__file__).resolve().parent
DOCS = ROOT / "docs"

NEW_DOCS = [
    "2158-resilio-remedy-hardening-attestation-durable-audience-closure-and-late-survivor-rediscovery-truth-fragmentation-evaluation.md",
    "2159-remedy-hardening-attestation-durable-closure-contract-sheet-page-rediscovery-surfaces-latent-survivors-and-invalidator-budget-interface-spec.md",
    "2160-remedy-hardening-attestation-durable-closure-review-page-if-stale-material-resurfaces-later-does-the-closure-claim-survive-or-reopen-interface-spec.md",
    "2161-remedy-hardening-attestation-durable-closure-proof-page-rediscovery-invalidators-reopen-triggers-and-durable-sentence-ceiling-interface-spec.md",
    "2162-remedy-hardening-attestation-durable-closure-timeline-page-close-latent-survivor-reappear-reopen-renarrow-and-redurable-events-interface-spec.md",
    "2163-remedy-hardening-attestation-durable-closure-lineage-receipt-page-rediscovery-safe-closure-verdict-reopen-budget-and-blocked-stronger-sentences-interface-spec.md",
]

if __name__ == "__main__":
    missing = [name for name in NEW_DOCS if not (DOCS / name).exists()]
    if missing:
        raise SystemExit(f"Missing rev0503 docs: {missing}")
    print("rev0503 docs present")
