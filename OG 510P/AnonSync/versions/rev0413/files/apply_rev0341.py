from pathlib import Path


def main():
    root = Path(__file__).resolve().parent
    docs = root / "docs"
    added = [
        "1186-resilio-byte-plan-certainty-hash-witness-dedup-reuse-and-partial-transfer-fragmentation-evaluation.md",
        "1187-byte-plan-contract-sheet-page-reuse-basis-hash-witness-and-redownload-ceiling-interface-spec.md",
        "1188-hash-and-preseed-review-page-local-byte-candidates-dedup-search-and-archive-dependency-interface-spec.md",
        "1189-reuse-basis-review-page-piece-delta-local-copy-rename-reuse-and-full-redownload-branch-interface-spec.md",
        "1190-partial-transfer-survivor-proof-page-resume-witness-cleanup-boundary-and-leftover-residue-interface-spec.md",
        "1191-byte-plan-lineage-receipt-page-reuse-basis-witness-grade-and-redownload-fallback-interface-spec.md",
    ]
    missing = [name for name in added if not (docs / name).exists()]
    if missing:
        raise SystemExit(f"Missing rev0341 docs: {missing}")
    print("rev0341 content present")


if __name__ == "__main__":
    main()
