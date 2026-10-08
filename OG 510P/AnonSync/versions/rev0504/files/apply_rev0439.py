from pathlib import Path


if __name__ == "__main__":
    root = Path(__file__).resolve().parent
    expected = [
        "docs/1774-resilio-remedy-convergence-offline-return-and-late-joiner-fragmentation-evaluation.md",
        "docs/1775-remedy-convergence-contract-sheet-page-required-cohort-convergence-returner-risk-and-late-joiner-quarantine-interface-spec.md",
        "docs/1776-remedy-convergence-review-page-did-the-authoritative-repair-actually-converge-across-present-returning-and-newly-admitted-cohorts-interface-spec.md",
        "docs/1777-remedy-convergence-proof-page-present-cohort-adoption-returner-exposure-and-quarantine-validity-interface-spec.md",
        "docs/1778-remedy-convergence-timeline-page-cutover-catch-up-rejoin-auto-connect-and-collapse-events-interface-spec.md",
        "docs/1779-remedy-convergence-lineage-receipt-page-cohort-convergence-returner-safety-and-blocked-stronger-cure-sentences-interface-spec.md",
    ]
    missing = [p for p in expected if not (root / p).exists()]
    if missing:
        raise SystemExit("Missing expected rev0439 files:\n" + "\n".join(missing))
    print("rev0439 presence check OK")
