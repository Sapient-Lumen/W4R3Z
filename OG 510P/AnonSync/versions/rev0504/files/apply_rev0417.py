from pathlib import Path


def main() -> None:
    root = Path(__file__).resolve().parent
    docs = root / "docs"
    touched = [
        docs / "00-status.md",
        docs / "10-resilio-sync-evaluation.md",
        docs / "11-resilio-borrow-line-and-non-clone-scorecard.md",
        docs / "sources.md",
        docs / "1642-resilio-creditor-representation-delegation-and-release-authority-fragmentation-evaluation.md",
        docs / "1643-creditor-authority-contract-sheet-page-principal-representative-scope-and-expiry-interface-spec.md",
        docs / "1644-creditor-representation-review-page-verify-delegate-split-scope-and-freeze-routes-interface-spec.md",
        docs / "1645-settlement-authority-proof-page-valid-releasor-waiver-scope-and-reopen-risk-interface-spec.md",
        docs / "1646-creditor-authority-timeline-page-delegation-acceptance-expiry-revocation-and-release-events-interface-spec.md",
        docs / "1647-creditor-authority-lineage-receipt-page-principal-representative-scope-and-blocked-release-sentences-interface-spec.md",
    ]
    missing = [str(p) for p in touched if not p.exists()]
    if missing:
        raise SystemExit("Missing expected rev0417 files:\n" + "\n".join(missing))
    print("rev0417 content present:")
    for path in touched:
        print("-", path.relative_to(root))


if __name__ == "__main__":
    main()
