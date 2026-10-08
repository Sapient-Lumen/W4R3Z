from pathlib import Path


if __name__ == "__main__":
    root = Path(__file__).resolve().parent
    expected = [
        "docs/1738-resilio-remedy-preservation-hold-and-expiry-shield-fragmentation-evaluation.md",
        "docs/1739-remedy-hold-contract-sheet-page-repair-material-reservation-expiry-shield-and-breach-interface-spec.md",
        "docs/1740-remedy-preservation-review-page-is-the-repair-material-actually-protected-now-interface-spec.md",
        "docs/1741-remedy-hold-proof-page-held-objects-retention-overrides-and-breach-risk-interface-spec.md",
        "docs/1742-remedy-hold-timeline-page-arm-extend-breach-release-and-expiry-events-interface-spec.md",
        "docs/1743-remedy-hold-lineage-receipt-page-preserved-repair-material-coverage-and-blocked-stronger-sentences-interface-spec.md",
    ]
    missing = [p for p in expected if not (root / p).exists()]
    if missing:
        raise SystemExit("Missing expected rev0433 files:\n" + "\n".join(missing))
    print("rev0433 presence check OK")
