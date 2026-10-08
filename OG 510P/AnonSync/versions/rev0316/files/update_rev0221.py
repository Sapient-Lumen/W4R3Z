from pathlib import Path

ROOT = Path(__file__).resolve().parent
DOCS = ROOT / "docs"

print("rev0221 partial quiescence updates already baked into archive at", ROOT)
print("New files:")
for name in [
    "531-resilio-pause-quiescence-ambiguity-and-partial-stop-truth-evaluation.md",
    "532-quiescence-review-page-phase-stop-residual-activity-and-safe-alternative-interface-spec.md",
    "533-residual-activity-matrix-page-transfer-detect-delete-and-readiness-lanes-interface-spec.md",
    "534-pause-language-substitution-page-freeze-stop-and-quiesce-claim-rewrite-interface-spec.md",
    "535-quiescence-receipt-page-requested-stop-effective-scope-and-residual-flow-interface-spec.md",
]:
    print("-", DOCS / name)
