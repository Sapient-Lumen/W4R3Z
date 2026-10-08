from pathlib import Path

REVISION = "rev0328"
FILES = [
    "docs/1108-resilio-placeholder-materialization-pin-truth-and-source-byte-witness-fragmentation-evaluation.md",
    "docs/1109-materialization-contract-sheet-page-placeholder-hydrated-pinned-and-byte-witness-interface-spec.md",
    "docs/1110-hydration-review-page-single-file-subtree-future-arrivals-and-fetch-ceiling-interface-spec.md",
    "docs/1111-local-residency-review-page-remove-from-device-remove-from-all-and-placeholder-survivor-interface-spec.md",
    "docs/1112-source-byte-witness-watch-page-ghost-file-risk-offline-guarantee-and-materialization-debt-interface-spec.md",
    "docs/1113-materialization-lineage-receipt-page-visible-entry-local-bytes-and-source-witness-boundary-interface-spec.md",
]

if __name__ == "__main__":
    root = Path(__file__).resolve().parent
    print(REVISION)
    for rel in FILES:
        path = root / rel
        print(f"OK\t{rel}\t{path.exists()}")
