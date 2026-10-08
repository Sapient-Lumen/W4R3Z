# Bundle support metadata

`vhk bundle` now writes an optional `bundle_support_metadata` object into
`vhk_bundle_manifest.json` whenever the bundled directory looks like a readable
VHK project.

The goal is simple: a shared bundle should be able to say more than “these bytes
arrived intact.” It should also be able to say which Linux target lanes the
project currently claims, where those claims came from, whether the bundle
itself contains the proof artifacts that stronger claims depend on, and whether
it carries the public-facing support/install docs that explain those claims.

## Data sources

The support snapshot prefers the editable claim workflow when it exists:

- `docs/VHK_TARGET_CLAIMS.yaml`
- `vhk audit-target-claims`

If no claim file exists yet, the bundle falls back to planner recommendations
from the same strategy surface used by `vhk plan-project`.

## Manifest shape

The embedded `bundle_support_metadata` object currently includes:

- `claim_source` — `claims_file`, `planner_recommendations`, or `unavailable`
- `claims_file_present`
- `claim_summary` and `audit_summary`
- `level_counts` and `status_counts`
- `targets[]` rows with:
  - `target`, `title`, `score`, `fit`
  - `claim_level` and `recommended_level`
  - audit `status`
  - `artifacts_present` and `artifacts_missing`
  - any audit `issues` / `warnings`
- `publish_docs_present`, `publish_docs_missing`, and `publish_pack_present`
- `review_commands`

## CLI review

Use `vhk inspect-bundle <bundle.zip>` to review the embedded snapshot without
unpacking the archive. `--json` prints the raw machine-readable structure.

## Product intent

This does **not** prove that a bundle works on every desktop. It makes the
bundle honest about what the project currently claims, which proofs are present,
and which stronger claims still need evidence.
