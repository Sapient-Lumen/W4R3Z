# Decisions — rev0161

## D-161-01 — test the mechanism against three baselines

Use exactly four conditions: forward-only, monolithic prompt retcon, Lacuna serial roles, and Lacuna role-separated contexts. This separates “retrospection helps” from “Lacuna's structure helps” and “manufactured context separation helps.”

## D-161-02 — clone durable state, not prompts

Each condition receives an exact SQLite backup verified against cube ID, head, event count, and semantic snapshot. Prompt equality alone would not preserve hidden epistemic custody.

## D-161-03 — randomize privately, dispatch serially

Commit a private deterministic permutation before accepting results, expose only opaque cell labels in the manifest, and allow one active cell. Serial operation limits accidental preview and makes the next authority unambiguous to less capable coordinators.

## D-161-04 — keep the fixed four conditions in schema v1

A capsule must contain exactly the fixed condition set and order. Arbitrary treatment names would make auditing and report interpretation weaker. A future schema may generalize after the comparison protocol is stable.

## D-161-05 — make invocation records script-bound

Every ordinary and checkpoint attempt names the scripted step it serves. Accepted ordinary calls must equal retained transcript steps. This prevents orphan calls and selective transcript omission.

## D-161-06 — treat context topology as declared but enforce consistency

Context IDs are not provider attestations. Still, cross-cell reuse, role-topology collapse, and duplicate invocation IDs are detectable contradictions and therefore refused.

## D-161-07 — blind only the rating surface

Workers need condition-specific instructions; experiment owners need assignment custody. Raters receive only transcripts under opaque labels. Lacuna claims structured blinding, not semantic anonymity or double blinding.

## D-161-08 — freeze the rater count before execution

The capsule fixes rater count, scale, dimensions, and prompts. Unblinding waits for complete unique ratings. This blocks convenient early stopping inside one retained run.

## D-161-09 — separate evidence classes in the report

Kernel-derived cube facts, host-declared execution measures, and human judgments remain different structures. No automatic combined “winner score” is emitted.

## D-161-10 — use one exact parent/worker authority split across providers

Provider-specific aliases may change, but every worker receives a complete least-context card and no transition authority. Parent-only acceptance, review, commit, recovery, and presentation remain invariant.

## D-161-11 — publish initial sidecars as whole directories

Build owner-only staging beside the final path and rename after complete construction. Reuse the helper for turn, checkpoint, and scenario runs.

## D-161-12 — bind supplied paths to open objects

Any API that accepts both a `Cube` and a path must prove they resolve to the same directory before publishing authority documents.

## D-161-13 — do not pretend one four-cell block answers Gwern

Rev0161 is an instrument. Broad claims require replicated capsules, preserved failures, multiple stories/models/raters, and an analysis plan.
