from pathlib import Path

ROOT = Path(__file__).resolve().parent
print("This archive was already materialized as rev0193.")
print("New docs added:")
for name in [
    "docs/391-resilio-placeholder-materialization-eviction-delete-and-archive-replay-evaluation.md",
    "docs/392-fetch-intent-page-materialize-scope-later-arrival-policy-and-replica-source-interface-spec.md",
    "docs/393-local-eviction-page-placeholder-reversion-detach-scope-and-last-full-copy-floor-interface-spec.md",
    "docs/394-delete-consequence-page-local-vs-global-delete-authority-and-retained-byte-boundary-interface-spec.md",
    "docs/395-restore-review-page-archive-candidate-chronology-authority-and-replay-risk-interface-spec.md",
]:
    print(" -", name)
