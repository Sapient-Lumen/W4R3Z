from pathlib import Path


if __name__ == "__main__":
    root = Path(__file__).resolve().parent
    expected = [
        "docs/1762-resilio-remedy-landing-target-binding-and-duplicate-path-fragmentation-evaluation.md",
        "docs/1763-remedy-landing-contract-sheet-page-target-binding-sidepath-risk-and-operative-adoption-interface-spec.md",
        "docs/1764-remedy-landing-review-page-did-the-right-repair-land-in-the-right-place-for-the-right-object-interface-spec.md",
        "docs/1765-remedy-landing-proof-page-target-binding-evidence-duplicate-path-risk-and-adoption-floor-interface-spec.md",
        "docs/1766-remedy-landing-timeline-page-start-write-rename-rebind-sidepath-and-adoption-events-interface-spec.md",
        "docs/1767-remedy-landing-lineage-receipt-page-target-binding-landing-scope-and-blocked-stronger-cure-sentences-interface-spec.md",
    ]
    missing = [p for p in expected if not (root / p).exists()]
    if missing:
        raise SystemExit("Missing expected rev0437 files:\n" + "\n".join(missing))
    print("rev0437 presence check OK")
