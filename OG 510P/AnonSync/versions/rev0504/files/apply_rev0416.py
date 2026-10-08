from pathlib import Path


def main() -> None:
    root = Path(__file__).resolve().parent
    docs = root / "docs"
    touched = [
        docs / "00-status.md",
        docs / "10-resilio-sync-evaluation.md",
        docs / "11-resilio-borrow-line-and-non-clone-scorecard.md",
        docs / "sources.md",
        docs / "1636-resilio-creditor-attribution-evidence-horizon-and-dispute-reopening-fragmentation-evaluation.md",
        docs / "1637-creditor-claim-contract-sheet-page-attribution-basis-evidence-horizon-and-dispute-window-interface-spec.md",
        docs / "1638-creditor-dispute-review-page-verify-split-freeze-and-escalate-routes-interface-spec.md",
        docs / "1639-creditor-attribution-proof-page-verified-creditor-set-evidence-sufficiency-and-release-freeze-interface-spec.md",
        docs / "1640-creditor-dispute-timeline-page-claim-open-evidence-age-challenge-ruling-and-reopen-events-interface-spec.md",
        docs / "1641-creditor-attribution-lineage-receipt-page-creditor-basis-evidence-window-and-blocked-release-sentences-interface-spec.md",
    ]
    missing = [str(p) for p in touched if not p.exists()]
    if missing:
        raise SystemExit("Missing expected rev0416 files:\n" + "\n".join(missing))
    print("rev0416 content present:")
    for path in touched:
        print("-", path.relative_to(root))


if __name__ == "__main__":
    main()
