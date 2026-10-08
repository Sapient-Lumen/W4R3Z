from pathlib import Path


def main() -> None:
    root = Path(__file__).resolve().parent
    docs = root / "docs"
    touched = [
        docs / "00-status.md",
        docs / "10-resilio-sync-evaluation.md",
        docs / "11-resilio-borrow-line-and-non-clone-scorecard.md",
        docs / "sources.md",
        docs / "1630-resilio-restoration-creditor-waterfall-partial-relief-and-probation-fragmentation-evaluation.md",
        docs / "1631-restoration-waterfall-contract-sheet-page-creditor-order-partial-relief-and-probation-window-interface-spec.md",
        docs / "1632-creditor-waterfall-review-page-reserve-first-neighbor-first-pro-rata-and-waiver-routes-interface-spec.md",
        docs / "1633-partial-restoration-proof-page-tier-cleared-remaining-debt-and-future-burst-probation-interface-spec.md",
        docs / "1634-restoration-waterfall-timeline-page-partial-relief-missed-slices-probation-and-release-events-interface-spec.md",
        docs / "1635-restoration-waterfall-lineage-receipt-page-creditor-order-partial-relief-and-blocked-clean-restoration-sentences-interface-spec.md",
    ]
    missing = [str(p) for p in touched if not p.exists()]
    if missing:
        raise SystemExit("Missing expected rev0415 files:\n" + "\n".join(missing))
    print("rev0415 content present:")
    for path in touched:
        print("-", path.relative_to(root))


if __name__ == "__main__":
    main()
