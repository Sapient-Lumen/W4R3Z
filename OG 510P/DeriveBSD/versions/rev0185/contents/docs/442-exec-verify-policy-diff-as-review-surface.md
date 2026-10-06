# Verified execution policy diff as a review surface

**Tier:** B (Base)
**Profiles:** A, B, C, D
**Pillars:** isolation, supply-chain, operability
**Patterns:** Plan→Apply→Receipt, Registry→Diff→Gate, Bundles

DeriveBSD already treats “verified execution” (NetBSD Veriexec / FreeBSD MAC/veriexec style) as a **typed posture**:
- policy: `exec-verify-policy`
- activation receipt: `exec-verify-receipt`
- enforcement snapshot/events: `exec-verify-snapshot`, `exec-verify-event`

Prior art anchors (why this exists):
- NetBSD Veriexec guide chapter: https://www.netbsd.org/docs/guide/en/chap-veriexec.html
- FreeBSD MAC/veriexec review trail: https://reviews.freebsd.org/D8554

The remaining operator pain point is review ergonomics:
**when verified-exec posture drifts, reviewers need a compact, stable surface that is gateable by policy**.

This doc introduces `exec.verify.policy.diff` as that surface.

## The artifact

- Schema: `spec/exec.verify.policy.diff.schema.json`
- Example: `spec/examples/exec.verify.policy.diff.json`

An `exec.verify.policy.diff` compares two `exec-verify-policy` objects (by digest) and summarizes:
- enforcement mode drift (`disabled` / `audit` / `enforce`)
- fingerprint database binding drift (which derived closure fingerprint set is loaded)
- explicit exception drift (paths allowlisted outside the derived fingerprint set)

The diff is deterministic-by-default: the only inputs are the two policy objects (plus optional policy metadata used to annotate/generate risk flags).

## Where it shows up

### Drift bundles (review funnel)

If a host/service enables verified-exec and the policy changes between generations, attach:
- the old `exec-verify-policy` digest
- the new `exec-verify-policy` digest
- an `exec.verify.policy.diff` (preferred)

This keeps “runtime integrity posture” reviewable without forcing every profile to adopt verified-exec.

### Incident/support bundles

When verified-exec is enabled, incident bundles should include:
- the latest `exec-verify-snapshot`
- any `exec-verify-event` violations in the bundle time window
- and (optionally) the `exec.verify.policy.diff` if “policy drift” is part of the incident story

This makes “why did an exec/load get denied?” answerable without spelunking raw logs.

## Typical gates

Verified-exec policy diffs are posture drift surfaces.
Typical gate posture is profile-aware:

- **Relaxation is high leverage:** `enforce→audit` or `audit→disabled` should require explicit approval and a declared time-bounded recovery window.
- **Disabling is often unacceptable in strict profiles:** treat `disabled` as a breakglass-style exception (or block it entirely).
- **New exceptions should be rare:** exception additions should require a linked decision record and a follow-up plan to remove them.

If an interop story needs “disable verified exec”, it must be implemented as a **killable adapter lane** (Adapter→Shadow→Replace), never as a permanent global requirement.

## Risk flags

`exec.verify.policy.diff` may emit canonical `risk_flags` (reason codes for UI + policy). Starter set:

- `exec-verify-disabled`
- `exec-verify-relaxed`
- `exec-verify-exception-added`

See: `docs/435-risk-flags-registry-and-gate-vocabulary.md`.

## Related docs

- Verified execution as evidence: `docs/233-verified-execution-as-evidence.md`
- Runtime verified execution (direction): `docs/103-runtime-verified-execution.md`
- Canonical diff registry: `docs/430-diff-surface-registry.md`
- Drift bundles: `docs/395-drift-bundles-and-review-summaries.md`

Last updated: 2026-02-28r162
