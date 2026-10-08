# Assurance Case Workbench fixtures

This fixture family exists to make **P-0503 Assurance Case Workbench Kit** concrete.

The goal is **not** to build a complete certification workflow.
The goal is to prove that a Rust-native crate can:

- import evidence from sibling tools,
- link evidence to explicit claims and assumptions,
- preserve freshness / provenance / trust metadata,
- mark claims as satisfied / partial / assumed / stale / manual-review / blocked,
- emit one compact human review pack,
- and export standards-shaped views without losing status semantics.

## Implemented scenario family

1. `mixed_campaign_and_conformance_import` — one top-level release claim imports a verification campaign bundle, a conformance bundle, and a manual review note.
2. `stale_verification_campaign_blocks_top_claim` — evidence remains parseable but goes stale after a toolchain/profile change and blocks the top-level claim.
3. `assumption_blocks_release_claim` — unresolved deployment or environment assumptions must show up in both the assumption ledger and the review gate.
4. `import_policy_rejects_stale_low_trust_campaign` — parsing succeeds, but visible policy rejects the import and blocks the pack.
5. `gsn_export_projection_preserves_status_but_not_local_review_fields` — standards-shaped export remains useful while honestly declaring losses.
6. `sacm_projection_redacts_local_file_paths_but_keeps_claim_lineage` — share-safe export preserves lineage while explaining redactions and loss.

## Still-important follow-on scenarios

1. `mixed_evidence_pack` — coverage, lint profile, unsafe-audit, conformance, and spec-reference evidence coexist.
2. `claim_library_upgrade_changes_argument_basis` — a pack stays structurally valid while the claim-pattern basis changes enough to require review.
3. `supplier_handoff_bundle_requires_dual_export_profiles` — internal and external review packs differ without corrupting the internal graph.

## Minimal pack for 0.1

- `assurance-profile.toml`
- `claim-graph.json`
- `evidence-index.json`
- `claim-status.report.json`
- `assurance-diff.report.json`
- `review-pack-manifest.json`

## Design rules

- Prefer **conservative status semantics** over pretty diagrams.
- Preserve whether support came from automated evidence, manual review, or assumption.
- Treat imported receipts as untrusted input with provenance and freshness attached.
- Keep standards-shaped export secondary to the internal diffable claim graph.
- Let `blocked` mean “top-level claim cannot honestly be treated as green”, not merely “some import failed to parse”.
