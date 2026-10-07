# Datacube Transfer Ledger

This is the compact record of what ideas from other datacubes were reviewed, what was adopted here, and what was deliberately not adopted.
Use it to avoid re-arguing the same transfer questions every turn.

## Adopted patterns

- **EvidenceVault-rev0484** -> machine-readable queue/public/decision boundary; first applied in `rev0426`; anchors: `release_queue/QUEUE_INDEX.json`, `published/PUBLIC_SURFACE.json`, `release_queue/DECISION_INDEX.json`, `release_queue/LATEST_DECISION.json`
- **Goldenrule-rev0323** -> citation-head register plus explicit warnings; first applied in `rev0426`; anchors: `published/CITATION_HEADS.md`, `published/citation_heads.json`
- **DelayBasin-rev0093** -> archive index, bundle manifest, context-pack discipline, rebuild entrypoint; first applied in `rev0427`; anchors: `ARCHIVE_INDEX.md`, `ARCHIVE_INDEX.json`, `RELEASE_MANIFEST.json`, `CONTEXT_PACK.json`, `Makefile`, `publishing/rebuild_archive_surfaces.py`
- **Hyperepo-rev0242** -> short reentry packet and handoff discipline; first applied in `rev0429`; anchors: `START_HERE.md`, `CONTEXT_PACK.json`, `publishing/CONTROL_SURFACES.md`
- **pyCausalWeave-rev0075** -> pruning policy, revision receipt, posture checks; first applied in `rev0426`; anchors: `REVISION_RECEIPT.json`, `PRUNING_POLICY.md`, `PRUNED_TRANSIENT.paths`, `publishing/check_transient_surface.py`, `Makefile`
- **The-Election-Stack-rev0524** -> lifecycle-gate framing, feedback-transfer ledgering; first applied in `rev0431`; anchors: `publishing/LIFECYCLE_GATES.md`, `publishing/lifecycle_gates.json`, `reports/lifecycle_gate_status.json`, `DATACUBE_TRANSFER_LEDGER.md`, `DATACUBE_TRANSFER_LEDGER.json`
- **Radical-Governance-rev0416 and GlassTTY-rev0123** -> control-surface / doctrine crosswalks; first applied in `rev0427`; anchors: `publishing/CONTROL_SURFACES.md`, `publishing/control_surfaces.json`, `publishing/LIFECYCLE_GATES.md`
- **TriKEM-rev0260** -> fail-closed bundle thinking; first applied in `rev0428`; anchors: `publishing/check_archive_coherence.py`, `publishing/check_manifest_coverage.py`, `MANIFEST.sha256`, `reports/archive_surface_coherence.json`
- **Goldenrule-rev0323 / DeriveBSD-rev0323 / Overseer-rev0147** -> explicit structural contracts via JSON Schema, compact invariant registry for truths that should survive refactors; first applied in `rev0432`; anchors: `schemas/`, `publishing/check_surface_schemas.py`, `reports/surface_schema_validation.json`, `publishing/ARCHIVE_INVARIANTS.md`, `publishing/archive_invariants.json`, `publishing/check_archive_invariants.py`, `reports/archive_invariants.json`
- **DelayBasin-rev0093 / SlopOS-rev0545** -> context-pack budget discipline; first applied in `rev0432`; anchors: `publishing/check_context_pack_budget.py`, `reports/context_pack_budget.json`, `CONTEXT_PACK.json`
- **TriKEM-rev0260 / The-Election-Stack-rev0524 / GlassTTY-rev0123 / DelayBasin-rev0093** -> exact compared-bundle provenance, grouped assurance-artifact catalog; first applied in `rev0433`; anchors: `TRANSFER_SOURCES.md`, `TRANSFER_SOURCES.json`, `TRANSFER_INPUTS.sha256`, `reports/transfer_source_receipt.json`, `ASSURANCE_ARTIFACTS.md`, `ASSURANCE_ARTIFACTS.json`
- **EvidenceVault-rev0484 / DelayBasin-rev0093 / Hyperepo-rev0242** -> generated human queue/decision ledgers from compact machine state; first applied in `rev0434`; anchors: `publishing/render_queue_surfaces.py`, `release_queue/STATUS.md`, `release_queue/QUEUE.md`, `release_queue/LATEST_DECISION.md`, `publishing/check_archive_coherence.py`

- **pyCausalWeave-rev0075 / DelayBasin-rev0093** -> archive budget discipline, release-hygiene guard against shipped review-render clutter; first applied in `rev0435`; anchors: `publishing/ARCHIVE_BUDGET.md`, `publishing/archive_budget_policy.json`, `publishing/check_archive_budget.py`, `reports/archive_budget.json`, `publishing/check_transient_surface.py`, `PRUNING_POLICY.md`

## Not adopted

- **EvidenceVault-rev0484** -> heavier executed-publication ledger / snapshot registry; reason: This archive still has zero post-policy Anonymity releases, so the weight is premature.
- **The-Election-Stack-rev0524** -> very large feedback-to-doc trace tables; reason: Valuable there, but too heavy for this archive's narrower publication-governance problem.
- **SlopOS-rev0545 / Micromax-rev0401** -> broader software-project contributor/build surfaces; reason: The primary archive is not trying to become a conventional software project.
- **Parables-rev0249** -> scratchpad-first root layout; reason: This archive benefits more from conservative operator guidance than from visible free-form scratchpads.

## Open questions

- Whether a future first post-policy Anonymity publication should trigger adoption of a heavier executed-publication ledger.
- Whether the current rebuild script should eventually grow into a full package-construction script, or remain intentionally limited to surface regeneration and verification.
- Whether any future first release should pin the schema set more formally with schema versioning policy beyond the current file-level contracts.
