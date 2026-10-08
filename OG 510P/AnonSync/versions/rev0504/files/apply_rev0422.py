from pathlib import Path


def main() -> None:
    root = Path(__file__).resolve().parent
    docs = root / "docs"
    touched = [
        docs / "00-status.md",
        docs / "10-resilio-sync-evaluation.md",
        docs / "11-resilio-borrow-line-and-non-clone-scorecard.md",
        docs / "sources.md",
        docs / "1672-resilio-publication-audience-redaction-and-reliance-grade-fragmentation-evaluation.md",
        docs / "1673-publication-contract-sheet-page-audience-scope-redaction-grade-and-reliance-class-interface-spec.md",
        docs / "1674-publication-review-page-who-sees-what-why-and-whether-they-may-rely-interface-spec.md",
        docs / "1675-reliance-proof-page-published-view-redaction-lineage-and-decision-grade-status-interface-spec.md",
        docs / "1676-publication-timeline-page-proposal-notice-publication-redaction-and-retraction-events-interface-spec.md",
        docs / "1677-publication-lineage-receipt-page-viewer-scope-redaction-basis-and-blocked-reliance-sentences-interface-spec.md",
    ]
    missing = [str(p) for p in touched if not p.exists()]
    if missing:
        raise SystemExit("Missing expected rev0422 files:\n" + "\n".join(missing))
    print("rev0422 content present:")
    for path in touched:
        print("-", path.relative_to(root))


if __name__ == "__main__":
    main()
