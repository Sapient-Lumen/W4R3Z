from pathlib import Path

ROOT = Path(__file__).resolve().parent
DOCS = ROOT / "docs"

NEW_FILES = [
    "1204-resilio-change-witness-lock-blockade-watcher-exhaustion-and-mtime-write-downgrade-fragmentation-evaluation.md",
    "1205-change-witness-contract-sheet-page-live-event-rescan-discovery-quiescence-hold-and-timestamp-authority-interface-spec.md",
    "1206-writer-pressure-review-page-delay-profile-lock-blockade-recheck-cadence-and-safe-publish-threshold-interface-spec.md",
    "1207-observation-proof-page-watcher-health-rescan-debt-manual-touch-and-change-seen-confidence-interface-spec.md",
    "1208-timestamp-authority-downgrade-review-page-disk-mtime-write-failure-database-truth-and-row-honesty-interface-spec.md",
    "1209-change-witness-lineage-receipt-page-detection-basis-hold-block-class-and-timestamp-authority-interface-spec.md",
]

if __name__ == "__main__":
    missing = [name for name in NEW_FILES if not (DOCS / name).exists()]
    if missing:
        raise SystemExit(f"Missing rev0344 docs: {missing}")
    print("rev0344 docs present and ready")
