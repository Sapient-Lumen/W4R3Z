from pathlib import Path

ROOT = Path(__file__).resolve().parent
DOCS = ROOT / "docs"

NEW_FILES = [
    "1198-resilio-modification-time-authority-offline-winner-time-skew-gate-and-archive-republish-fragmentation-evaluation.md",
    "1199-mutation-chronology-contract-sheet-page-online-order-offline-winner-and-time-basis-interface-spec.md",
    "1200-concurrent-edit-review-page-online-sequence-offline-return-delay-mitigation-and-loser-placement-interface-spec.md",
    "1201-time-authority-proof-page-clock-zone-gmt-window-and-mtime-certainty-interface-spec.md",
    "1202-older-byte-republish-review-page-archive-restore-runtime-witness-and-touch-remediation-interface-spec.md",
    "1203-mutation-chronology-lineage-receipt-page-winner-basis-time-certainty-and-loser-survivor-interface-spec.md",
]

if __name__ == "__main__":
    missing = [name for name in NEW_FILES if not (DOCS / name).exists()]
    if missing:
        raise SystemExit(f"Missing rev0343 docs: {missing}")
    print("rev0343 docs present and ready")
