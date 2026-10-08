from pathlib import Path


def main() -> None:
    root = Path(__file__).resolve().parent
    docs = root / "docs"
    touched = [
        docs / "00-status.md",
        docs / "10-resilio-sync-evaluation.md",
        docs / "11-resilio-borrow-line-and-non-clone-scorecard.md",
        docs / "sources.md",
        docs / "1696-resilio-execution-attainment-completion-and-outcome-proof-fragmentation-evaluation.md",
        docs / "1697-execution-attainment-contract-sheet-page-attempted-completed-propagated-and-verified-effect-scope-interface-spec.md",
        docs / "1698-attainment-review-page-did-the-effect-land-for-the-required-cohort-and-what-residue-remains-interface-spec.md",
        docs / "1699-attainment-proof-page-what-actually-landed-where-and-why-stronger-completion-sentences-stay-blocked-interface-spec.md",
        docs / "1700-attainment-timeline-page-execution-start-local-commit-propagation-and-verification-events-interface-spec.md",
        docs / "1701-attainment-lineage-receipt-page-effect-coverage-verification-basis-and-blocked-stronger-completion-sentences-interface-spec.md",
    ]
    missing = [str(p) for p in touched if not p.exists()]
    if missing:
        raise SystemExit("Missing expected rev0426 files:\n" + "\n".join(missing))
    print("rev0426 content present:")
    for path in touched:
        print("-", path.relative_to(root))


if __name__ == "__main__":
    main()
