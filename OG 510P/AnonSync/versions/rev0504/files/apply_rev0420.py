from pathlib import Path


def main() -> None:
    root = Path(__file__).resolve().parent
    docs = root / "docs"
    touched = [
        docs / "00-status.md",
        docs / "10-resilio-sync-evaluation.md",
        docs / "11-resilio-borrow-line-and-non-clone-scorecard.md",
        docs / "sources.md",
        docs / "1660-resilio-action-effectivity-notice-and-supersession-fragmentation-evaluation.md",
        docs / "1661-action-enactment-contract-sheet-page-proposed-executed-noticed-and-effective-states-interface-spec.md",
        docs / "1662-enactment-review-page-draft-notice-cooling-effectivity-and-supersession-routes-interface-spec.md",
        docs / "1663-action-effectivity-proof-page-notice-completion-effective-time-and-surviving-subtruths-interface-spec.md",
        docs / "1664-action-effectivity-timeline-page-proposal-execution-notice-cooling-and-supersession-events-interface-spec.md",
        docs / "1665-action-effectivity-lineage-receipt-page-effective-state-notice-cohort-and-supersession-boundary-interface-spec.md",
    ]
    missing = [str(p) for p in touched if not p.exists()]
    if missing:
        raise SystemExit("Missing expected rev0420 files:\n" + "\n".join(missing))
    print("rev0420 content present:")
    for path in touched:
        print("-", path.relative_to(root))


if __name__ == "__main__":
    main()
