# Freshness event replay, credit-cap, and generated compression refactor audit

Revision: `rev0351`  
Bundle: `Theory-of-Everything-rev0351-2026.06.10.04.35-freshness-event-replay-creditcap-compression-refactor.zip`

## Purpose

This pass targets the next real risk after rev0350 completed note-key extinction: the archive had typed `source_role_events`, but frontier freshness custody still mostly verified row-level `source_refs`. A public record could therefore remain present on a denominator row while the event that made it safe to read as denominator pressure, route-local handoff, exclusion, or metadata-wrapper custody was removed or weakened.

The second risk was waste: generated audit surfaces were beginning to preserve every passing row even when most rows were empty/pass scaffolding. That made restart surfaces harder to read and increased the chance that a human would miss a real failure.

## Changes made

- Extended `FRONTIER-SOURCE-FRESHNESS-ASSERTIONS.json` to schema version `1.5` with `typed_event_replay_policy` on the high-risk source-role freshness assertions.
- Hardened `tools/frontier_source_freshness.py` so those assertions check covering `source_role_events`, expected dispositions, and source-custody credit caps in addition to row-level `source_refs`.
- Added missing event coverage exposed by the new replay check on classical-GR, dark-sector, QM/QFT, QCD, Lorentz/CPT, electroweak/flavor/neutrino, and equivalence/fifth-force source-role rows.
- Normalized ambiguous non-S0 `source_role_event` credit caps on denominator, forecast-runway, operational-status, and metadata-wrapper events to `S0` while preserving the old row-context cap in `row_context_credit_cap_before_rev0351` and `credit_cap_scope`.
- Added lint that rejects non-S0 source-custody event caps unless the event is a historical normalization record.
- Expanded `tools/source_role_negative_replay_tests.py` so compact negative tests now include credit-cap drift and freshness-event replay mutation.
- Compressed `docs/30-program/route-state-summary.generated.md` by removing the all-family route matrix from the restart path and adding lint to prevent regrowth.
- Compressed `docs/30-program/graviton-counting-source-role-audit.generated.md` by suppressing hundreds of empty/pass route rows while keeping the full executable scan.

## Substantive result

The archive no longer merely says that a frontier source is present or absent on a row. For the highest-risk public-source assertions, it now checks whether the row has the typed event that explains why the source is safe:

- denominator rows must retain the source as denominator pressure or route-local handoff only;
- metadata-wrapper rows must forbid the source as direct wrapper support;
- excluded refs must remain excluded from acquired-source rows;
- source-custody events cannot carry spendable route credit.

The generated restart path is also thinner. The route-state summary now points to machine ledgers for exact family-handle detail instead of reproducing the whole matrix, and the graviton-counting audit displays only rows with source custody content, failures, or required core-row status.

## Audit counts

- Freshness assertions with typed event replay: `8`.
- Typed source-role event rows replayed by freshness audit: `320`.
- Typed event replay failures after repair: `0`.
- Missing event coverages added in this pass: `16`.
- Source-custody event caps normalized to `S0`: `31`.
- Total `source_role_events` after repair: `575`.
- Route-state generated summary size after compression: `111` lines.
- Graviton-counting source-role generated audit size after compression: `43` lines.
- Negative replay cases: `7`.

## No-promotion boundary

No route score, route authority state, promotion ceiling, evidence-unit source credit, empirical-delta effect, forecast realization state, decision-experiment outcome, or observed-sector recovery state was improved. This revision changes replay enforcement, source-custody cap semantics, and generated-surface compression only.

## Next risks

The next risky work is now narrower:

1. extend typed event replay only where a freshness assertion already has real `source_role_events`, not by inventing a new registry layer;
2. factor the repeated lint/freshness/negative-test helper logic into a small shared helper without hiding family-local policy;
3. compress any remaining generated audits that still show failure-free empty rows;
4. audit prose that may still read `credit_cap` on a source-role event as route authority rather than source-custody authority.
