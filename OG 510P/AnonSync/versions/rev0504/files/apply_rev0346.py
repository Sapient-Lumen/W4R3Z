from pathlib import Path

ROOT = Path(__file__).resolve().parent
DOCS = ROOT / "docs"

NEW_FILES = [
    "1216-resilio-subject-scope-ignore-divergence-namespace-role-and-unsupported-name-fragmentation-evaluation.md",
    "1217-subject-scope-contract-sheet-page-visibility-indexing-counting-and-namespace-role-interface-spec.md",
    "1218-ignore-divergence-review-page-peer-local-rules-retroactivity-and-size-mismatch-interface-spec.md",
    "1219-namespace-role-review-page-hidden-service-artifacts-streams-and-temp-residue-interface-spec.md",
    "1220-scope-proof-page-visible-indexed-counted-replicated-and-exclusion-basis-interface-spec.md",
    "1221-subject-scope-lineage-receipt-page-peer-scope-namespace-role-and-exclusion-basis-interface-spec.md",
]

if __name__ == "__main__":
    missing = [name for name in NEW_FILES if not (DOCS / name).exists()]
    if missing:
        raise SystemExit(f"Missing rev0346 docs: {missing}")
    print("rev0346 docs present and ready")
