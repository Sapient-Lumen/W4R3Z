# ADR-0298: Breakglass bootstrap joins stay enabling-only and earliest-to-latest when plural

- Status: Accepted
- Date: 2026-03-23

## Context

`ADR-0297` already fixed the first half of the bootstrap story: breakglass may join exact upstream `boot.override.receipt` / `reset.receipt` objects instead of smearing pre-session recovery history into notes, BMC breadcrumbs, or generic `oob` folklore.

But one quiet loophole remained.
Once `bootstrap_receipt_joins[]` exists, it is tempting to treat it like a scrapbook:

- include denied boot attempts because they were “part of the incident”,
- include failed or superseded recovery experiments because they happened before the shell opened,
- or list real enabling steps in arbitrary UI order instead of causal order.

That would reintroduce archaeology into the exact join surface we just paid to create.
Support and policy tooling should be able to read a breakglass receipt and understand the actual enabling pre-session path without reconstructing which entries mattered.

## Decision

1. `breakglass.receipt.evidence.bootstrap_receipt_joins[]` stays an **enabling** surface, not a timeline scrapbook.
   Joined receipts must have materially enabled the actual emergency session.

2. denied attempts, failed dead ends, superseded experiments, and adapter-only breadcrumbs do **not** belong in `bootstrap_receipt_joins[]`.
   They may exist elsewhere as diagnostics, but they are not part of the canonical enabling join story.

3. When more than one bootstrap receipt is joined, the list is in **earliest-to-latest causal order** according to the joined receipts' own timing fields.

4. `breakglass.receipt.evidence.bootstrap_join_sequence_posture = earliest-to-latest-pre-session-enabling-only` makes that portable ordering/selection rule explicit.

## Consequences

Good:

- detached tooling gets one boring causal sequence for “what actually enabled entry”,
- support/export stops mixing successful recovery-path truth with failed exploratory steps,
- and the exact bootstrap join surface stays implementation-shaped instead of turning back into incident prose.

Costs:

- nearby docs and the canonical example need one more explicit posture field,
- and richer diagnostic timelines remain follow-on work rather than piggybacking on the authoritative join array.

## Follow-on

Still open as implementation detail:

- exact rendering of denied/failed pre-session experiments in incident/support views,
- whether later richer incident artifacts deserve a separate typed bootstrap timeline,
- adapter-specific provenance/redaction for BMC / remote-console stacks,
- and paired one-time-boot actuation semantics, which `ADR-0299` narrows further for the common `boot.override.receipt` + `reset.receipt` case.
