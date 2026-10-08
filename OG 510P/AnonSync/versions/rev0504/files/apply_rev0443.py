from pathlib import Path

ROOT = Path(__file__).resolve().parent
DOCS = ROOT / "docs"

NEW_DOCS = [
    "1798-resilio-remedy-watch-uncertainty-failsafe-and-confidence-decay-fragmentation-evaluation.md",
    "1799-remedy-watch-uncertainty-contract-sheet-page-confidence-decay-failsafe-and-refence-floor-interface-spec.md",
    "1800-remedy-watch-uncertainty-review-page-is-ordinary-life-still-safe-if-the-guard-goes-uncertain-interface-spec.md",
    "1801-remedy-watch-uncertainty-proof-page-coverage-loss-freshness-decay-and-failsafe-evidence-interface-spec.md",
    "1802-remedy-watch-uncertainty-timeline-page-healthy-decay-uncertain-trip-and-failsafe-events-interface-spec.md",
    "1803-remedy-watch-uncertainty-lineage-receipt-page-confidence-decay-failsafe-posture-and-blocked-ordinary-sentences-interface-spec.md",
]

if __name__ == "__main__":
    missing = [name for name in NEW_DOCS if not (DOCS / name).exists()]
    if missing:
        raise SystemExit(f"Missing rev0443 docs: {missing}")
    print("rev0443 files present")
