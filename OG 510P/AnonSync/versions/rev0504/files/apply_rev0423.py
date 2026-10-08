from pathlib import Path


def main() -> None:
    root = Path(__file__).resolve().parent
    docs = root / "docs"
    touched = [
        docs / "00-status.md",
        docs / "10-resilio-sync-evaluation.md",
        docs / "11-resilio-borrow-line-and-non-clone-scorecard.md",
        docs / "sources.md",
        docs / "1678-resilio-publication-recall-correction-and-reliance-residue-fragmentation-evaluation.md",
        docs / "1679-publication-recall-contract-sheet-page-reach-retraction-scope-and-reliance-residue-interface-spec.md",
        docs / "1680-publication-recall-review-page-correct-withdraw-reach-and-preserve-audit-residue-interface-spec.md",
        docs / "1681-publication-recall-proof-page-who-was-reached-what-withdrew-and-what-reliance-survives-interface-spec.md",
        docs / "1682-publication-recall-timeline-page-issue-correction-retraction-reach-and-residue-events-interface-spec.md",
        docs / "1683-publication-recall-lineage-receipt-page-reach-residue-and-blocked-erasure-sentences-interface-spec.md",
    ]
    missing = [str(p) for p in touched if not p.exists()]
    if missing:
        raise SystemExit("Missing expected rev0423 files:\n" + "\n".join(missing))
    print("rev0423 content present:")
    for path in touched:
        print("-", path.relative_to(root))


if __name__ == "__main__":
    main()
