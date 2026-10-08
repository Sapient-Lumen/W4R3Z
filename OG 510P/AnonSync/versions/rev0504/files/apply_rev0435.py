from pathlib import Path


if __name__ == "__main__":
    root = Path(__file__).resolve().parent
    expected = [
        "docs/1750-resilio-remedy-execution-runway-priority-and-source-readiness-fragmentation-evaluation.md",
        "docs/1751-remedy-runway-contract-sheet-page-priority-headroom-source-readiness-and-response-window-interface-spec.md",
        "docs/1752-remedy-runway-review-page-can-this-case-actually-be-cured-now-within-the-promised-window-interface-spec.md",
        "docs/1753-remedy-runway-proof-page-source-presence-capacity-reservation-and-execution-floor-interface-spec.md",
        "docs/1754-remedy-runway-timeline-page-request-queue-preempt-start-stall-and-miss-events-interface-spec.md",
        "docs/1755-remedy-runway-lineage-receipt-page-execution-readiness-runway-coverage-and-blocked-stronger-cure-sentences-interface-spec.md",
    ]
    missing = [p for p in expected if not (root / p).exists()]
    if missing:
        raise SystemExit("Missing expected rev0435 files:\n" + "\n".join(missing))
    print("rev0435 presence check OK")
