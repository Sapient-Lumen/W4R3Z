from pathlib import Path

ROOT = Path(__file__).resolve().parent
DOCS = ROOT / "docs"

print("rev0218 posture change cascade updates already baked into archive at", ROOT)
print("New files:")
for name in [
    "516-resilio-seat-posture-mutation-ambiguity-live-edit-rebind-and-cascade-evaluation.md",
    "517-seat-posture-change-review-page-live-edit-rebind-remove-reshare-and-cascade-interface-spec.md",
    "518-posture-transition-forecast-page-rights-byte-effects-and-manual-step-visibility-interface-spec.md",
    "519-posture-cascade-graph-page-direct-descendants-auto-narrowing-and-rebind-gaps-interface-spec.md",
    "520-seat-posture-change-receipt-page-requested-delta-effective-result-and-followup-work-interface-spec.md",
]:
    print("-", DOCS / name)
