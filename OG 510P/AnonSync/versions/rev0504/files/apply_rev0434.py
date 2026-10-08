from pathlib import Path


if __name__ == "__main__":
    root = Path(__file__).resolve().parent
    expected = [
        "docs/1744-resilio-remedy-hold-enforcement-custodian-obligation-and-breach-detectability-fragmentation-evaluation.md",
        "docs/1745-remedy-hold-enforcement-contract-sheet-page-custodian-acknowledgment-sensor-coverage-and-cleanup-suppression-interface-spec.md",
        "docs/1746-remedy-hold-enforcement-review-page-is-this-preservation-hold-actually-binding-where-it-needs-to-be-interface-spec.md",
        "docs/1747-remedy-hold-enforcement-proof-page-custodian-attestations-control-lanes-and-undetected-breach-floor-interface-spec.md",
        "docs/1748-remedy-hold-enforcement-timeline-page-request-acknowledge-audit-breach-and-release-events-interface-spec.md",
        "docs/1749-remedy-hold-enforcement-lineage-receipt-page-enforcement-coverage-breach-detectability-and-blocked-stronger-sentences-interface-spec.md",
    ]
    missing = [p for p in expected if not (root / p).exists()]
    if missing:
        raise SystemExit("Missing expected rev0434 files:\n" + "\n".join(missing))
    print("rev0434 presence check OK")
