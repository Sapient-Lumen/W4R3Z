# Verified execution as evidence (backend state + violations)

**Tier:** B (Base)  
**Profiles:** A, B, C, D  
**Pillars:** isolation, operability  
**Patterns:** Plan→Apply→Receipt  

DeriveBSD’s “immutable intent” is strongest when it is **enforceable**.

This lane keeps backend-facing verified-execution state and violations as **receipted, auditable observations**.
The authority boundary is now explicit:

- authoritative policy: `exec.integrity.policy`
- authoritative plan: `exec.integrity.plan`
- authoritative activation result: `exec.integrity.receipt`

This doc is about the **backend observation artifacts** that remain useful after activation:

- `exec-verify-snapshot`
- `exec-verify-event`

Legacy alias objects (`exec-verify-policy`, `exec-verify-receipt`) remain only for compatibility with older archive material and are not the preferred new lane.

## Prior art

- NetBSD Veriexec is a kernel file-integrity subsystem that verifies configured files before execution or read. References: https://www.netbsd.org/docs/guide/en/chap-veriexec.html , https://man.netbsd.org/veriexec.4 , https://man.netbsd.org/veriexec.8
- FreeBSD MAC/veriexec implements verified execution as a MAC policy and has a verifying loader path. References: https://reviews.freebsd.org/D8554 , https://reviews.freebsd.org/D16575

## DeriveBSD stance

- optional in v1, but the archive should define the shape now
- backend observations are derived from authoritative policy/plan/receipt objects
- snapshots/events should help answer:
  - what state did the backend think it was in?
  - which digest set was loaded?
  - what violation or transition actually occurred?

## Evidence objects

### Authoritative objects

- `exec.integrity.policy`
- `exec.integrity.plan`
- `exec.integrity.receipt`

### Backend observation objects

- `exec-verify-snapshot`
- `exec-verify-event`

### Drift surface

- `exec.verify.policy.diff`

Even though the diff kind name is historic, it compares authoritative `exec.integrity.policy` objects.

## Integration points

### 1) Activation + generations

- the authoritative policy is part of the generation’s apply plan
- change sets should use `apply-exec-integrity`
- activation emits `exec.integrity.receipt`
- backend snapshot/event streams can be bundled later for operations and incident review

### 2) Lockdown levels

If lockdown is raised (see `docs/230-lockdown-levels-and-securelevel.md`):

- lowering execution-integrity posture should be disallowed except in explicitly receipted recovery modes

### 3) Service jails, AppVMs, and control-plane compartments

- the host can enforce execution integrity globally for the base
- bounded runtime lanes can opt into stricter enforcement
- backend events must still be explainable against the authoritative runtime composition digests carried by the plan/receipt chain

## Operational escape hatches (must be explicit)

Verified execution is only usable if recovery is planned:

- provide a monotonic, receipted recovery profile
- treat exceptions as policy drift, not folklore
- keep backend-state evidence separate from policy intent so operators can see whether the problem was “we changed policy” or “the backend is unhealthy”

## Related docs

- `docs/289-exec-integrity-policy-and-verified-execution.md`
- `docs/442-exec-verify-policy-diff-as-review-surface.md`
- `docs/486-exec-integrity-authority-and-verified-execution-boundary.md`

Last updated: 2026-03-07r215
