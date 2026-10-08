from pathlib import Path


if __name__ == "__main__":
    root = Path(__file__).resolve().parent
    expected = [
        "docs/1756-resilio-remedy-flight-protection-preemption-and-interruptibility-fragmentation-evaluation.md",
        "docs/1757-remedy-flight-protection-contract-sheet-page-preemption-interruption-budget-and-finish-guarantee-interface-spec.md",
        "docs/1758-remedy-flight-protection-review-page-if-we-start-now-how-likely-is-this-cure-to-finish-cleanly-interface-spec.md",
        "docs/1759-remedy-flight-protection-proof-page-in-flight-guards-preemption-events-and-abort-floor-interface-spec.md",
        "docs/1760-remedy-flight-protection-timeline-page-start-suspend-resume-preempt-stall-and-abort-events-interface-spec.md",
        "docs/1761-remedy-flight-protection-lineage-receipt-page-finish-protection-interruption-budget-and-blocked-stronger-cure-sentences-interface-spec.md",
    ]
    missing = [p for p in expected if not (root / p).exists()]
    if missing:
        raise SystemExit("Missing expected rev0436 files:\n" + "\n".join(missing))
    print("rev0436 presence check OK")
