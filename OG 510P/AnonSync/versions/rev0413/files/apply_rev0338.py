from pathlib import Path

ROOT = Path(__file__).resolve().parent
DOCS = ROOT / "docs"

NEW_FILES = [
    "1168-resilio-transport-profile-protocol-overlap-cipher-overlap-and-bind-residue-fragmentation-evaluation.md",
    "1169-transport-profile-contract-sheet-page-route-class-protocol-set-cipher-set-and-bind-authority-interface-spec.md",
    "1170-protocol-overlap-review-page-direct-relay-lan-tracker-and-no-common-lane-interface-spec.md",
    "1171-bind-witness-review-page-interface-pinning-fallback-switch-and-use-only-cutoff-interface-spec.md",
    "1172-transport-hardening-review-page-lan-encryption-cipher-overlap-and-performance-side-effect-interface-spec.md",
    "1173-transport-profile-lineage-receipt-page-protocol-cipher-bind-witness-and-blocked-stronger-sentences-interface-spec.md",
]

if __name__ == "__main__":
    missing = [name for name in NEW_FILES if not (DOCS / name).exists()]
    if missing:
        raise SystemExit(f"Missing expected rev0338 files: {missing}")
    print("rev0338 files present")
