# Epic crate release ladders — 2026-03-25

This note answers a practical archive question:

**What should count as a meaningful `0.1`, `0.3`, or `1.0` for a worthy missing crate?**

The answer should be conservative.
Epic crates should not start by pretending to be finished platforms.

## The ladder

### Stage A — `0.1` honest local acceptance
A good `0.1` usually has:
- one repeated downstream question,
- one operator,
- one compact acceptance packet family,
- one local or CI rerun path,
- one human-readable summary,
- and one explicit refusal boundary.

`0.1` is where the crate becomes **real**.
It is not where it becomes universal.

### Stage B — `0.3` team reuse and controlled rechecks
A good `0.3` usually adds:
- schema stability good enough for diffs,
- multiple repeatable scenarios,
- recheck triggers that preserve old answers rather than overwriting them,
- organization-level presets or policy overlays,
- and clearer handoff semantics between two operators.

`0.3` is where the crate becomes **reusable across teams**.

### Stage C — `1.0` stable handoff semantics
A real `1.0` usually means:
- packet semantics are stable,
- supersession rules are explicit,
- acceptance packets can be reviewed by another team without oral tradition,
- and the crate’s support ceiling and refusal boundary are both well understood.

`1.0` is not “has more features”.
It is “another team can trust what the outputs mean”.

## What a worthy crate should provide other people at each stage

### At `0.1`
- one clear answer surface
- one compact machine-readable output family
- one short human summary
- one acceptance boundary

### At `0.3`
- one repeatable operating loop
- one meaningful diff/reopen story
- one small but credible corpus
- one handoff path inside an organization

### At `1.0`
- stable packet semantics
- stable refusal language
- durable handoff between people and teams
- confidence that the crate means the same thing next quarter

## Anti-patterns

Do not call a crate mature because it has:
- many adapters,
- many dashboards,
- many config flags,
- or a broad domain story.

Call it mature when it has:
- stable acceptance semantics,
- recheck discipline,
- durable packet meaning,
- and a refusal boundary users can actually rely on.

## How this applies to the frontier

- **P-0509 + P-0536 + minimal P-0535** can likely reach a strong `0.1` first.
- **P-0472 + P-0484** can likely reach `0.1` quickly and become a strong `0.3` support-envelope layer.
- **P-0486** should target a narrower `0.1` than its appetite suggests.
- **P-0537** and especially **P-0538** should remain more conservative about what counts as `1.0`.

## Archive rule after this pass

Future passes should not say “this is an epic crate contribution” unless they can also say:
- what its `0.1` is,
- what its `0.3` adds,
- what its `1.0` stabilizes,
- and what another team receives at each stage.
