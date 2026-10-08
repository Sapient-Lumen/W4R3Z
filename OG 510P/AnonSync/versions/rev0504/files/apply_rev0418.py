from pathlib import Path


def main() -> None:
    root = Path(__file__).resolve().parent
    docs = root / "docs"
    touched = [
        docs / "00-status.md",
        docs / "10-resilio-sync-evaluation.md",
        docs / "11-resilio-borrow-line-and-non-clone-scorecard.md",
        docs / "sources.md",
        docs / "1648-resilio-creditor-quorum-succession-and-conflict-authority-fragmentation-evaluation.md",
        docs / "1649-creditor-coalition-contract-sheet-page-required-signers-quorum-and-succession-rules-interface-spec.md",
        docs / "1650-creditor-coalition-review-page-verify-countersign-split-authority-and-conflict-freeze-routes-interface-spec.md",
        docs / "1651-closure-sufficiency-proof-page-sole-signer-vs-quorum-and-final-release-eligibility-interface-spec.md",
        docs / "1652-creditor-coalition-timeline-page-appointment-countersign-conflict-succession-and-reopen-events-interface-spec.md",
        docs / "1653-creditor-coalition-lineage-receipt-page-signer-set-quorum-rule-and-blocked-finality-sentences-interface-spec.md",
    ]
    missing = [str(p) for p in touched if not p.exists()]
    if missing:
        raise SystemExit("Missing expected rev0418 files:\n" + "\n".join(missing))
    print("rev0418 content present:")
    for path in touched:
        print("-", path.relative_to(root))


if __name__ == "__main__":
    main()
