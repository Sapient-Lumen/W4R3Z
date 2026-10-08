from pathlib import Path
ROOT = Path(__file__).resolve().parent
DOCS = ROOT / "docs"
print("rev0228 runtime profile continuity updates baked into archive at", ROOT)
for name in [
    "566-resilio-runtime-profile-locus-storage-lineage-and-surface-reach-fragmentation-evaluation.md",
    "567-runtime-profile-review-page-execution-principal-storage-root-and-surface-reach-interface-spec.md",
    "568-storage-lineage-forecast-page-profile-switch-share-carryover-and-identity-surface-interface-spec.md",
    "569-runtime-switch-review-page-migrate-clean-install-webui-scope-and-observation-loss-interface-spec.md",
    "570-runtime-profile-receipt-page-executing-principal-storage-root-surface-reach-and-followup-interface-spec.md",
]:
    print("-", DOCS / name)
