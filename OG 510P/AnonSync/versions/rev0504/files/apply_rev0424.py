from pathlib import Path


def main() -> None:
    root = Path(__file__).resolve().parent
    docs = root / "docs"
    touched = [
        docs / "00-status.md",
        docs / "10-resilio-sync-evaluation.md",
        docs / "11-resilio-borrow-line-and-non-clone-scorecard.md",
        docs / "sources.md",
        docs / "1684-resilio-acknowledgment-assent-and-reader-identity-fragmentation-evaluation.md",
        docs / "1685-acknowledgment-contract-sheet-page-notice-open-ack-and-assent-scope-interface-spec.md",
        docs / "1686-acknowledgment-review-page-notified-opened-acknowledged-and-bound-routes-interface-spec.md",
        docs / "1687-acknowledgment-proof-page-who-opened-acknowledged-and-assented-in-what-capacity-interface-spec.md",
        docs / "1688-acknowledgment-timeline-page-notice-open-ack-assent-and-revocation-events-interface-spec.md",
        docs / "1689-acknowledgment-lineage-receipt-page-reader-capacity-assent-grade-and-blocked-consent-sentences-interface-spec.md",
    ]
    missing = [str(p) for p in touched if not p.exists()]
    if missing:
        raise SystemExit("Missing expected rev0424 files:\n" + "\n".join(missing))
    print("rev0424 content present:")
    for path in touched:
        print("-", path.relative_to(root))


if __name__ == "__main__":
    main()
