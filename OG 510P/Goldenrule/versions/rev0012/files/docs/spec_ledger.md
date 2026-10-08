# Spec Ledger Rollup

This file is generated from `specs/spec_ledger.yaml`.

| id | type | status | owner | target_resolution | summary |
|---|---|---|---|---|---|
| SG-001 | gap | open | @root | 2026-04-01 | Formal contract between Rust engine outputs and analytic memory-one certificates is underspecified. |
| SQ-001 | question | open | @root | 2026-03-20 | Should certify accept only stationary solutions that satisfy both payoff and symmetry invariants? |
| SA-001 | assumption | open | @root | 2026-04-01 | Until SG-001 resolves, certification uses fail-closed validation and deterministic matrix solving. |
| SG-002 | gap | open | @root | 2026-04-10 | Formal solver portfolio and escalation criteria for claim classes are underspecified. |
| SQ-002 | question | open | @root | 2026-03-24 | Which claims require cross-solver agreement (Z3+cvc5) versus probabilistic model-checking evidence? |
| SA-002 | assumption | open | @root | 2026-04-10 | Until SG-002 resolves, treat solver checks as advisory in `gate` and required for release-critical claims only in strict posture. |
| SG-003 | gap | open | @root | 2026-04-15 | The engine-level contract for endogenous rematching and world-aware strategy canonicalization is underspecified. |
| SQ-003 | question | open | @root | 2026-03-27 | Which states should count as behaviorally equivalent in rematch-enabled worlds once opponent support, noise, and outside-option rules are included? |
| SA-003 | assumption | open | @root | 2026-04-15 | Until SG-003 resolves, treat fixed-dyad exit results as diagnostic and report rematch-world discoveries in canonicalized families rather than raw genotype counts when possible. |
| SQ-004 | question | open | @root | 2026-03-27 | When should rematch-world canonicalization caches be invalidated and recomputed as suspicious starters, noise, or outside-option semantics change reachability? |
| SQ-005 | question | open | @root | 2026-03-27 | Does the current proxy's initial-D-support invalidation gate survive once noise and endogenous rematching alter early-state reachability? |
| SA-004 | assumption | open | @root | 2026-04-15 | Until SG-003 resolves, reuse the current rematch-proxy canonicalization cache only when newly admitted entrants have C-only initial support under the current deterministic no-noise semantics. |
| SQ-006 | question | open | @root | 2026-03-27 | How should rematch-world canonicalization caches key on tremble/implementation-error semantics and actor-side error models? |
| SA-005 | assumption | open | @root | 2026-04-15 | Until SQ-006 resolves, any nonzero action-tremble semantics invalidate the zero-noise rematch canonicalization cache and require recomputation under the active noise model. |
| SQ-007 | question | open | @root | 2026-03-27 | What is the minimal sufficient rematch-world canonicalization cache key under each active noise topology and entrant-support regime? |
| SA-006 | assumption | open | @root | 2026-04-15 | Until SQ-007 resolves, key rematch-proxy canonicalization by active noise topology first; then use the coarsest entrant-support class validated by the current regime map (none: conservative full recompute after initial-D invalidation, focal tremble: initial-D class, opponent/bilateral tremble: no entrant key). |
| SQ-008 | question | open | @root | 2026-03-27 | What is the minimal exact reachability-unroll bound required for rematch-world canonicalization under each active world/noise semantics? |
| SA-007 | assumption | open | @root | 2026-04-15 | Until SQ-008 resolves, use the current proxy's verified support-level exact horizons `{none:3, opponent_tremble:2, focal_tremble:2, bilateral_tremble:1}` instead of the inherited `h=50` bound, and invalidate them whenever memory depth, rematch timing, or noise semantics change. |
| SQ-009 | question | open | @root | 2026-03-27 | Should rematch-world declarations expose a canonicalization planner manifest (minimal cache key plus exact horizon) instead of relying on ad hoc report code? |
| SA-008 | assumption | open | @root | 2026-04-15 | Until SG-003 resolves, treat the current proxy cache-plan JSON as a scratch compile-time planner and regenerate it whenever entrant support, tremble semantics, outside-option timing, or memory depth changes. |
| SQ-010 | question | open | @root | 2026-03-27 | Should zero-noise rematch-world planner metadata expose an ordered rule classifier instead of a flat support-signature lookup table? |
| SA-009 | assumption | open | @root | 2026-04-15 | Until SG-003 resolves, prefer the current zero-noise ordered wildcard classifier over a raw 243-entry support-signature dispatch table when vendoring scratch planner metadata, and regenerate it whenever world semantics change. |
| SQ-011 | question | open | @root | 2026-03-27 | Should interim zero-noise planner metadata be schema-validated and contract-tested as an ordered rule list before any engine embedding? |
| SA-010 | assumption | open | @root | 2026-04-15 | Until SG-003 resolves, treat the current zero-noise ordered wildcard classifier as valid only when both its schema and rule-contract checks pass against the regenerated proxy regime map. |
