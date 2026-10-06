# Exec integrity authority and verified-execution boundary

**Tier:** B (Base)  
**Profiles:** A, B, C, D  
**Pillars:** isolation, supply-chain, operability  
**Patterns:** Plan→Apply→Receipt, Registry→Diff→Gate  

DeriveBSD already wanted “no surprise bytes execute,” but the archive had started to say that in two overlapping dialects:
the newer `exec.integrity.*` lane and older `exec-verify-*` objects.

This doc fixes that boundary for v0.

## Accepted boundary

DeriveBSD uses a three-step execution-integrity contract:

1. **`exec.integrity.policy`** — the authoritative reviewed policy object.
2. **`exec.integrity.plan`** — the compiled activation object that binds policy to backend and runtime composition.
3. **`exec.integrity.receipt`** — the authoritative activation result.

Backend observation artifacts still exist, but they are downstream of that contract:

- `exec-verify-snapshot`
- `exec-verify-event`

`exec-verify-policy` and `exec-verify-receipt` are legacy compatibility aliases, not the preferred authored lane.

## Narrow rules

### `exec.integrity.policy` is the authority boundary

Reviewers should answer “what may execute?” from `exec.integrity.policy`, not from a backend fingerprint database dump.

That policy is where DeriveBSD says:

- which scopes are covered
- which sources are allowed (`store-only`, `signed-bundle`, bounded allowlists, breakglass)
- whether quarantined bytes are denied
- which explicit exceptions exist

### `exec.integrity.plan` binds policy to runtime composition

Execution integrity is not abstract.
It must bind to the runtime a component will actually see.

So the compiled plan must carry:

- `runtime_manifest_digest`
- `stratum_stack_digest`
- `mount_view_digest`

That makes these questions answerable from typed evidence:

- which entrypoint tree was active?
- which userland stack owned loader/library resolution?
- which mount view bounded interpreter and library lookup?

### Interpreters and loaders are narrow by design

The operable v0 rule is:

- entrypoint bytes must come from an allowed source
- interpreters must resolve inside the active `mount.view`
- dynamic loader resolution is ABI-anchor-only
- writable/quarantined bytes are denied in enforce mode unless the policy says otherwise

This is intentionally narrower than “try to infer whatever the host would have done.”
DeriveBSD should not let script execution or dynamic loading reopen ambient host fallback.

### `exec.verify.policy.diff` stays, but its input is authoritative policy

The drift surface name stays `exec.verify.policy.diff` for continuity,
but the compared objects are authoritative `exec.integrity.policy` digests.

That keeps review ergonomics stable while moving the archive to one source of truth.

### Backend snapshots/events are observations, not authority

`exec-verify-snapshot` and `exec-verify-event` are still useful:
they answer “what did the backend observe?” and “what violation happened?”

They do **not** replace the authoritative policy / plan / receipt chain.

## Product-shape fit (A–D without forks)

- **A / fleet host:** keep host/service execution integrity enforce-first and diff-gated; relaxations should be maintenance-shaped, time-bounded, and review-heavy.
- **B / workstation:** keep the host/trusted-UI lane narrow; broader or riskier user execution belongs in AppVM or other bounded runtime lanes, not ambient host fallback.
- **C / general OS:** preserve viability by allowing explicit compatibility exceptions and warn-first backends where needed, but keep the official policy object and receipt chain the same.
- **D / appliance factory / regulatory:** keep production/runtime policy sealed, reviewable, and strongly gateable; compatibility or maintenance execution stays in explicit approved lanes.

## Why this is the right narrow decision

This does not promise a perfect anti-bypass story up front.
It does something more valuable for the archive:

- collapses duplicated vocabulary,
- joins execution integrity to runtime composition,
- gives reviewers one stable policy surface,
- and keeps backend evidence useful without letting it become the real product.

## Related docs

- `adrs/ADR-0076-exec-integrity-authority-and-verified-execution-boundary.md`
- `docs/289-exec-integrity-policy-and-verified-execution.md`
- `docs/233-verified-execution-as-evidence.md`
- `docs/442-exec-verify-policy-diff-as-review-surface.md`
- `docs/485-stratum-stack-and-runtime-composition-boundary.md`
- `spec/exec.integrity.policy.schema.json`
- `spec/exec.integrity.plan.schema.json`
- `spec/exec.integrity.receipt.schema.json`
- `spec/exec.verify.policy.diff.schema.json`
- `spec/examples/exec.integrity.policy.json`
- `spec/examples/exec.integrity.plan.json`
- `spec/examples/exec.integrity.receipt.json`
- `spec/examples/exec.verify.policy.diff.json`

Last updated: 2026-03-07r215
