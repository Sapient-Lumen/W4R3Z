from pathlib import Path

REVISION = "rev0326"
FILES = [
    "docs/1096-resilio-stop-proof-hidden-runtime-and-restart-provenance-fragmentation-evaluation.md",
    "docs/1097-runtime-stop-contract-sheet-page-projection-runtime-boot-reentry-and-platform-class-interface-spec.md",
    "docs/1098-shutdown-drain-review-page-stop-intent-residual-work-and-no-further-publication-proof-interface-spec.md",
    "docs/1099-runtime-stop-proof-page-visible-state-service-state-and-platform-background-ceiling-interface-spec.md",
    "docs/1100-restart-provenance-page-stop-source-reentry-trigger-and-chronology-risk-interface-spec.md",
    "docs/1101-runtime-stop-lineage-receipt-page-stop-scope-proof-rung-and-reentry-posture-interface-spec.md",
]

if __name__ == "__main__":
    root = Path(__file__).resolve().parent
    print(REVISION)
    for rel in FILES:
        path = root / rel
        print(f"OK\t{rel}\t{path.exists()}")
