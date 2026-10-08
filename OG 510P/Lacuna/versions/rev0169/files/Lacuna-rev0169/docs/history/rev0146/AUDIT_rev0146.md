# Audit and refactor — rev0146

## Scope

This pass audited context access, human entry, model entry, path handling, mutation atomicity, and documentation discoverability.

## Finding A-0146-01 — hidden-world disclosure through mixed context scope

**Severity:** high

**Before:** `context_markdown(cube, agent_id=player, world_id=wld_hidden)` selected the named candidate world even though perspective packets were documented as omitting worlds.

**Cause:** filtering and rendering were interleaved. The `world_id` branch ran before the perspective omission branch.

**Repair:** one structured context builder now refuses mixed scope with `unsafe-context-scope`. Markdown and JSON consume the same projection.

**Tests:** direct context refusal and CLI structured-refusal end-to-end test.

## Finding A-0146-02 — no human object above a filesystem path

**Severity:** product-blocking

**Before:** every command required a raw cube path; there was no named campaign, list, or selection.

**Repair:** add no-clobber campaign libraries, strict manifests, exact selector resolution, atomic manifest writes, default participants, and selected-library path resolution.

**Tests:** creation, participant registration, selection, path traversal refusal, nonempty overlay refusal, strict unknown-field refusal, and executable round trip.

## Finding A-0146-03 — LLMs had only low-level change-sets

**Severity:** product-blocking

**Before:** a model could receive Markdown context and separately construct a kernel change-set, but there was no head-bound interaction envelope, narration field, disclosure declaration, or model-friendly ID mechanism.

**Repair:** add turn packet/proposal/commit, sequential aliases, narration-source custody, disclosure preflight, and combined narration/receipt output.

**Tests:** aliases, narration-only turns, stale atomicity, disclosure symmetry, unknown/forward alias refusal, rebuild stability, and executable round trip.

## Finding A-0146-04 — narration could become an uncustodied side channel

**Severity:** medium

**Repair:** every committed turn prepends an utterance source with the exact narration digest and proposal/audience provenance. New disclosed assertions must point to it.

**Remaining risk:** the narration body is not retained, and semantic equivalence is not checked. A host must retain exact bytes for transcript custody.

## Finding A-0146-05 — hidden settlement affected visible unknowns by omission

**Severity:** high

**Before:** perspective context filtered the globally computed unsettled-claim list. A private anchor or hidden cross-world consensus could therefore remove a claim from the player’s lacunae even when no visible record settled it. The forbidden state did not appear directly, but its existence was observable through omission.

**Repair:** perspective-relative unsettled claims are now computed only from claims visible through that perspective and anchors visible to it. Privileged consensus remains entirely outside the calculation.

**Test:** a player-visible report remains unsettled for the player even when another private perspective has anchored the same proposition; the planner view correctly sees the global settlement.

## Refactor summary

- Extracted context construction from Markdown rendering.
- Centralized assertion/question visibility predicates in `Cube`.
- Added atomic JSON replacement utility for non-ledger manifests.
- Added cube-reference resolution so selected libraries work across the CLI.
- Kept the database schema unchanged; all new behavior composes through existing change-set validation.

## Verification performed

- 35 behavioral and end-to-end tests.
- Full projection rebuild after a turn.
- SQLite, foreign-key, invariant, event-chain, and change-receipt verification.
- Python bytecode compilation and AST parsing.
- JSON parse and Draft 2020-12 meta-schema checks for all six schemas.
