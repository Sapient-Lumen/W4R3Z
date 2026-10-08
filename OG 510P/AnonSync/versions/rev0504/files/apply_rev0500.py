from pathlib import Path

NEW_DOCS = [
    "docs/2140-resilio-remedy-hardening-attestation-outsider-recurrence-safe-clean-state-and-recontamination-watch-fragmentation-evaluation.md",
    "docs/2141-remedy-hardening-attestation-recurrence-watch-contract-sheet-page-watch-horizon-recontamination-channels-and-recurrence-safe-ceiling-interface-spec.md",
    "docs/2142-remedy-hardening-attestation-recurrence-watch-review-page-after-clean-state-can-stale-reliance-re-enter-before-the-watch-horizon-closes-interface-spec.md",
    "docs/2143-remedy-hardening-attestation-recurrence-watch-proof-page-reopen-channel-ledger-detection-posture-and-recurrence-safe-sentence-ceiling-interface-spec.md",
    "docs/2144-remedy-hardening-attestation-recurrence-watch-timeline-page-clean-verified-offline-return-archive-restore-rescan-detect-and-horizon-close-events-interface-spec.md",
    "docs/2145-remedy-hardening-attestation-recurrence-watch-lineage-receipt-page-watch-horizon-summary-recontamination-posture-and-blocked-stronger-sentences-interface-spec.md",
]

if __name__ == "__main__":
    missing = [p for p in NEW_DOCS if not Path(p).exists()]
    if missing:
        raise SystemExit(f"Missing rev0500 docs: {missing}")
    print("rev0500 docs present")
