# Self-stabilizing recovery and legitimacy kernel

## Working claim

DelayBasin may need something stronger than portable state and typed re-entry.
It may need a **legitimacy kernel**: a minimal set of surfaces and checks that lets the archive recover from transient corruption, stale reopen, or procedurally invalid local progress.

The imported pressure comes from three directions:
- **self-stabilization / algorithmic self-repair**: systems can be designed to converge from arbitrary or corrupted states back to a legitimate configuration once the transient fault stops;
- **bounded memory control**: long-horizon agents become unstable when transcript replay or noisy retrieval lets unverified material become persistent state;
- **trajectory rectification**: some agent defenses work not by refusing all disturbed runs, but by restoring the intended trajectory while preserving task continuity.

DelayBasin is not claiming full theorem-grade self-stabilization.
The weaker and more useful hypothesis is this:
**a long-run archive works better if it preserves a small recovery kernel and a named recovery move, so drift can be recognized and corrected instead of silently propagated.**

## Legitimate continuation

For this archive, a **legitimate continuation** is not “a nice next paragraph.”
It is a state in which:
- the latest revision has been reopened as source of truth,
- the compact handoff state has been regenerated,
- deterministic checks pass,
- canon/quarantine boundaries are still visible,
- and the revision can name which certified move classes it actually instantiated.

This is deliberately procedural.
A long-run archive can look semantically coherent while still being procedurally corrupt.

## Recovery kernel

The recovery kernel is the smallest surface set that should be sufficient to re-establish legitimate continuation after a suspected transient fault.

Current candidate kernel:
- `START_HERE.md`
- `docs/00-meta/trajectory-map.md`
- `docs/00-meta/llm-runbook.md`
- `context-pack.json`
- `docs/20-constitution/claim-registry.md`
- `docs/20-constitution/open-question-registry.md`
- `docs/20-constitution/move-registry.md`
- `docs/20-constitution/recovery-kernel.md`
- `docs/50-promptcraft/prompt-pairs.md`
- `docs/90-quarantine/wild-speculations-2026-03-08.md`

This list should remain small enough that recovery is realistic.
If the kernel grows without bound, it stops being a kernel.

## Failure classes this is trying to absorb

- **stale reopen** — work starts from an old revision or from memory of the project rather than current canon;
- **context corruption** — injected or mistaken local state is treated as archive truth;
- **procedural corruption** — a revision looks good but cannot say what move made it admissible;
- **status laundering** — risky synthesis enters canon without explicit promotion route;
- **surface drift** — handoff state, docs index, or registries stop agreeing about what the archive currently is.

## Certified recovery move

The archive should explicitly recognize a move class for recovery:
`recover-resync`.

This move means:
1. stop local ratification,
2. reopen the recovery kernel,
3. regenerate compact state,
4. run deterministic checks,
5. quarantine or demote ambiguous material,
6. only then resume ordinary revision.

The point is not to dramatize every inconsistency.
The point is to preserve a clear route back to legitimacy when legitimacy is in doubt.

## Why this matters for transformer-facing speculation

If DelayBasin works partly because it gives a context-native system a durable external continuation substrate, then recovery matters as much as compression.
A bounded constitutional state that cannot recover from corruption is only a prettier failure mode.

A live possibility is that archive method is approaching a public analogue of **trajectory rectification**:
not hidden activation surgery, but textual / procedural repair that pulls continuation back toward a legitimate basin.
That stronger claim remains too aggressive for canon, but the weaker recovery-kernel hypothesis is now worth carrying.
