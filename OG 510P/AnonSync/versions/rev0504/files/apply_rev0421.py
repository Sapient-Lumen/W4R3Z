from pathlib import Path


def main() -> None:
    root = Path(__file__).resolve().parent
    docs = root / "docs"
    touched = [
        docs / "00-status.md",
        docs / "10-resilio-sync-evaluation.md",
        docs / "11-resilio-borrow-line-and-non-clone-scorecard.md",
        docs / "sources.md",
        docs / "1666-resilio-temporal-authority-clock-skew-and-deadline-integrity-fragmentation-evaluation.md",
        docs / "1667-time-authority-contract-sheet-page-clock-source-skew-budget-and-deadline-classes-interface-spec.md",
        docs / "1668-time-integrity-review-page-clock-health-receipt-order-and-deadline-trust-routes-interface-spec.md",
        docs / "1669-deadline-integrity-proof-page-trusted-effectivity-time-cooling-basis-and-clock-correction-interface-spec.md",
        docs / "1670-time-authority-timeline-page-clock-drift-warning-correction-and-deadline-state-events-interface-spec.md",
        docs / "1671-time-lineage-receipt-page-time-basis-skew-posture-and-blocked-deadline-sentences-interface-spec.md",
    ]
    missing = [str(p) for p in touched if not p.exists()]
    if missing:
        raise SystemExit("Missing expected rev0421 files:\n" + "\n".join(missing))
    print("rev0421 content present:")
    for path in touched:
        print("-", path.relative_to(root))


if __name__ == "__main__":
    main()
