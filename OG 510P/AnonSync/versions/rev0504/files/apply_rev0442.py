from pathlib import Path

ROOT = Path(__file__).resolve().parent
DOCS = ROOT / "docs"

NEW_DOCS = [
    "1792-resilio-remedy-watch-health-drill-freshness-and-response-budget-fragmentation-evaluation.md",
    "1793-remedy-watch-health-contract-sheet-page-probe-freshness-drill-coverage-and-response-budget-interface-spec.md",
    "1794-remedy-watch-health-review-page-is-this-post-discharge-guard-still-credible-right-now-interface-spec.md",
    "1795-remedy-watch-health-proof-page-probe-results-drill-evidence-and-response-budget-floor-interface-spec.md",
    "1796-remedy-watch-health-timeline-page-arming-probe-drill-degrade-trip-and-refence-events-interface-spec.md",
    "1797-remedy-watch-health-lineage-receipt-page-guard-health-drill-freshness-and-blocked-ordinary-sentences-interface-spec.md",
]

if __name__ == "__main__":
    missing = [name for name in NEW_DOCS if not (DOCS / name).exists()]
    if missing:
        raise SystemExit(f"Missing rev0442 docs: {missing}")
    print("rev0442 files present")
