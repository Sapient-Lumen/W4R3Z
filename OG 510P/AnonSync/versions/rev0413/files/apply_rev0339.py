from pathlib import Path

ROOT = Path(__file__).resolve().parent
print("rev0339 content is already materialized in", ROOT)
for name in [
    "docs/1174-resilio-overlapping-subject-topology-nested-share-shadow-seeding-and-selective-sync-ceiling-fragmentation-evaluation.md",
    "docs/1175-overlapping-subject-contract-sheet-page-parent-child-topology-seed-lane-and-index-cost-interface-spec.md",
    "docs/1176-nested-share-topology-review-page-parent-child-rights-shadow-propagation-and-seed-gap-interface-spec.md",
    "docs/1177-overlap-admission-review-page-selective-sync-ceiling-home-root-conflict-and-existing-id-boundary-interface-spec.md",
    "docs/1178-overlapping-subject-proof-page-shared-subtree-dual-indexing-and-propagation-residue-interface-spec.md",
    "docs/1179-overlapping-subject-lineage-receipt-page-parent-child-claim-class-seed-gap-and-blocked-stronger-sentences-interface-spec.md",
]:
    p = ROOT / name
    print(name, "exists" if p.exists() else "missing")
