# ADR-0076: Exec integrity authority and verified-execution boundary

Date: 2026-03-07
Status: Accepted

## Context

DeriveBSD already had two partially overlapping ways to talk about runtime execution integrity:

- the newer `exec.integrity.policy` / `exec.integrity.plan` / `exec.integrity.receipt` lane,
- and older `exec-verify-*` policy / receipt / snapshot / event objects plus `exec.verify.policy.diff`.

That overlap was turning one important security property into archive entropy:

- reviewers could not tell which object was authoritative,
- drift surfaces were attached to backend-shaped objects instead of the human-reviewed policy,
- change sets still referred to `apply-exec-verify`,
- and the runtime-composition work in `adrs/ADR-0075-stratum-stack-and-runtime-composition-boundary.md`
  still was not explicitly joined to execution-integrity planning.

The archive also had one open implementation question that was too central to leave folklore-shaped:
what exactly happens for interpreters, dynamic loaders, and writable/quarantined bytes when execution integrity is enabled?

Without a crisp boundary, DeriveBSD risks ending up in the common failure mode:
verified execution exists on paper, but operators relax it, bypass it, or treat it as a backend-specific hardening toy rather than a first-class review surface.

## Decision

DeriveBSD will treat execution integrity as a **small typed contract**, not a loose family of backend artifacts.

The accepted v0 boundary is:

1. `exec.integrity.policy` is the authoritative desired policy object.
   It is the review surface for “what sources may execute, in which scopes, with which exceptions?”

2. `exec.integrity.plan` is the compiled activation object.
   It binds the policy digest to:
   - the selected backend,
   - the activation target,
   - and the runtime-composition join points:
     `runtime_manifest_digest`, `stratum_stack_digest`, and `mount_view_digest`.

3. `exec.integrity.receipt` is the authoritative activation result.
   It records what policy/plan/runtime composition/backend were actually active at the activation boundary.

4. `exec-verify-snapshot` and `exec-verify-event` remain valid, but only as **backend observation artifacts**.
   They are not the authority boundary for policy intent.

5. `exec-verify-policy` and `exec-verify-receipt` are legacy compatibility aliases.
   They are not the preferred authored or reviewed artifacts for new work.

6. `exec.verify.policy.diff` remains the canonical drift-surface name for now,
   but it diffs authoritative `exec.integrity.policy` objects rather than backend-shaped legacy aliases.

7. Change sets should apply execution-integrity policy through `apply-exec-integrity`, not `apply-exec-verify`.

8. Interpreter / loader resolution is intentionally narrow:
   - the executable entrypoint must come from an allowed source,
   - interpreters must resolve inside the active `mount.view`,
   - dynamic loader resolution is ABI-anchor-only,
   - and writable/quarantined bytes are denied in enforce mode unless an explicit policy exception says otherwise.

## Consequences

### Positive

- There is now one answer to “which object owns execution-integrity intent?”
- Runtime-composition work and execution-integrity work are joined by shared digests.
- Drift review moves back to the human-reviewed policy instead of backend-specific fingerprints.
- The archive gets a narrow, operable answer for scripts / loaders / writable bytes.
- A/D can keep strong defaults without creating a workstation/general-OS fork.

### Negative / trade-offs

- Older `exec-verify-*` policy/receipt objects become explicitly second-class.
- The archive has one more contract checker to keep wired.
- Backend implementations still need practical details for manifest loading, counters, and violation telemetry.

## Non-goals

This ADR does **not** decide:

- the final kernel/userspace implementation strategy for every backend,
- whether future backends beyond `mac_veriexec` / `broker` should exist,
- full JIT / in-memory code policy,
- or the final UI wording for every execution-denied event.

Those remain follow-on implementation work.

## Why this shape

This is a deliberately narrow coherence move:

- one authoritative policy,
- one compiled plan,
- one activation receipt,
- backend observations kept separate,
- runtime composition bound by digest,
- and one clear rule for interpreters/loaders/writable bytes.

That is enough to make “no unverified execution” worth implementing,
without turning the archive into a sprawling verified-exec research notebook.
