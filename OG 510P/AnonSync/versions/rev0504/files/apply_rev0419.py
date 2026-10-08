from pathlib import Path


def main() -> None:
    root = Path(__file__).resolve().parent
    docs = root / "docs"
    touched = [
        docs / "00-status.md",
        docs / "10-resilio-sync-evaluation.md",
        docs / "11-resilio-borrow-line-and-non-clone-scorecard.md",
        docs / "sources.md",
        docs / "1654-resilio-action-matrix-threshold-and-irreversible-act-fragmentation-evaluation.md",
        docs / "1655-action-authority-matrix-contract-sheet-page-typed-acts-thresholds-and-reversibility-interface-spec.md",
        docs / "1656-action-matrix-review-page-receive-waive-lift-reopen-and-delegate-routes-interface-spec.md",
        docs / "1657-action-sufficiency-proof-page-protective-vs-irreversible-acts-and-earned-scope-interface-spec.md",
        docs / "1658-action-matrix-timeline-page-threshold-change-cooling-window-and-executed-act-events-interface-spec.md",
        docs / "1659-action-authority-lineage-receipt-page-typed-acts-earned-scope-and-blocked-stronger-actions-interface-spec.md",
    ]
    missing = [str(p) for p in touched if not p.exists()]
    if missing:
        raise SystemExit("Missing expected rev0419 files:\n" + "\n".join(missing))
    print("rev0419 content present:")
    for path in touched:
        print("-", path.relative_to(root))


if __name__ == "__main__":
    main()
