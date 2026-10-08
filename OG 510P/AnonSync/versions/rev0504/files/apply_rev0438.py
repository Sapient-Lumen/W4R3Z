from pathlib import Path


if __name__ == "__main__":
    root = Path(__file__).resolve().parent
    expected = [
        "docs/1768-resilio-remedy-cutover-authoritative-switch-and-conflict-rebound-fragmentation-evaluation.md",
        "docs/1769-remedy-cutover-contract-sheet-page-authoritative-switch-writer-freeze-and-conflict-fence-interface-spec.md",
        "docs/1770-remedy-cutover-review-page-did-the-cure-become-the-authoritative-live-state-without-old-writer-rebound-interface-spec.md",
        "docs/1771-remedy-cutover-proof-page-live-writer-fence-conflict-risk-and-switch-validity-interface-spec.md",
        "docs/1772-remedy-cutover-timeline-page-land-freeze-switch-conflict-and-rebound-events-interface-spec.md",
        "docs/1773-remedy-cutover-lineage-receipt-page-authoritative-switch-live-writer-state-and-blocked-stronger-cure-sentences-interface-spec.md",
    ]
    missing = [p for p in expected if not (root / p).exists()]
    if missing:
        raise SystemExit("Missing expected rev0438 files:\n" + "\n".join(missing))
    print("rev0438 presence check OK")
