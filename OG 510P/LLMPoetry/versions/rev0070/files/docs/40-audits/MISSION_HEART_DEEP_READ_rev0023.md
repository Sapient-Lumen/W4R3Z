# Mission heart deep read — rev0023

Timestamp: `2026-06-14T17:16:00-04:00`  
Turn: `15`  
Scope: deep read of `rev0022`, online research pulse `RP-0015`, archive-health repair, and speculative correction plan.

## Heart of the mission

The heart is not to make an AI poem pass as human. The heart is to build a disclosure-honest, resumable, machine-native poetic workshop where machine procedure is not hidden provenance but part of the literary act.

The project is strongest when it asks: **what can a poem become when branching, receipts, selectors, source traces, state transitions, and disclosure are necessary to reading rather than excuses around weak lines?**

## What is missing

1. A reader-facing state object. P0001 has closed/open/traversal/patched states, but the reader still has to inspect markdown and JSON by hand.
2. External material pressure. P0001 keeps recycling its own codework fog: pinhole, voltage, motors, coded air, parity, glyph, syntax, spool.
3. External/disclosed reader judgment. LLM cold review is useful triage, not evidence.
4. Schema/path-reference validation beyond bespoke validators.
5. Durable source capture only when source-dependent poems actually need it.

## What went wrong enough to repair now

### 1. Lineage drift survived rev0022 validation

`REVISION_LINEAGE.json` listed `rev0022` as current in one lineage array, but its top-level `current_revision`, `current_artifact`, and `updated_at` still pointed to `rev0021`. That is a reentry hazard because future operators may trust the compact top-level fields first.

Correction: synchronized `lineage`, `entries`, and `revisions`; set top-level current fields to `rev0023`; added `tools/check_revision_lineage_freshness.py`; wired it into `make validate` and `make doctor`.

### 2. Open-question aliases became a stale second queue

`registries/open_questions.json` had a canonical `open_questions` array and a legacy `questions` array. The legacy array still contained stale tasks like cold-reviewing D007/D008/D009-era states, including `OQ-0021` as live even though D010 was already reviewed.

Correction: made `open_questions` canonical, made `questions` mirror only live records, resolved or merged stale questions, and added `tools/check_open_questions_canonical.py`.

### 3. Source health did not cover the source registry

`registries/source_registry.json` had 108 source records while `registries/source_health.json` covered only 49. The cube had a source-health surface without total coverage.

Correction: added explicit health records for every registered source. Freshly checked rev0023 pulse sources are marked `checked_rev0023`; older uncovered sources are honestly marked `registered_not_rechecked` rather than falsely refreshed. Added `tools/check_source_health_coverage.py`.

### 4. `make validate` did not actually run the surface-freshness import

`tools/llmpoetry_validate.py` imported `check_surface_freshness` but did not execute it. That made the phrase “wired into validate” too optimistic.

Correction: `make validate` now runs surface freshness plus revision-lineage, open-question, and source-health subchecks directly.

## What should change next

Do not write D011. Build one accessible reader-facing state object for D010. It should show closed, open, traversal, and patched states as one readable object, with each transition linked to the receipt that authorizes it. If that object is dull, freeze P0001 as a laboratory failure and fork P0002 with an external object, archive, measurement, place, data source, or interface constraint.

## Speculation

P0001 may be most valuable as a controlled failure: it shows how quickly procedural verification can become a trellis with no fruit. That is not wasted if the next poem family lets the world pressure the form. The likely breakthrough is not more internal machinery; it is a narrower machine act plus a more resistant material source, exposed in a reader-facing object.
