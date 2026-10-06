# Verified execution as evidence (veriexec / MAC/veriexec) (optional)

DeriveBSD’s “immutable intent” is strongest when it is **enforceable**.

This lane turns verified execution into a **receipted, auditable posture**:
- a signed policy says what should be executable/loadable
- activation loads/locks enforcement
- runtime emits violations as typed events

## Prior art

- NetBSD Veriexec: in-kernel file integrity subsystem that verifies specified files before they are executed or read.
- FreeBSD MAC/veriexec: verified execution implemented as a MAC policy.

(Links in `docs/32-curated-references.md`.)

## DeriveBSD stance

- Optional in v1, but the archive should define the shape now.
- Derived from existing evidence:
  - closure manifest / closure proof
  - deployment object / generation digest
  - policy decision record (why any exception exists)

## Evidence objects

When enabled, DeriveBSD treats enforcement as evidence:

- `exec-verify-policy`: desired enforcement mode + fingerprint database digest
- `exec-verify-receipt`: result of loading/activating policy
- `exec-verify-snapshot`: current enforcement state (mode, loaded db digest, counters)
- `exec-verify-event`: typed events for violations and state transitions

Schemas:
- `spec/exec.verify.policy.schema.json`
- `spec/exec.verify.receipt.schema.json`
- `spec/exec.verify.snapshot.schema.json`
- `spec/exec.verify.event.schema.json`

## Integration points

### 1) Activation + generations

- The policy is part of the generation’s apply plan.
- Activation loads the fingerprint DB and emits a receipt.
- Rolling back to an older BE also rolls back to the matching exec-verify policy.

### 2) Lockdown levels

If lockdown is raised (see `docs/230-lockdown-levels-and-securelevel.md`):
- lowering exec-verify enforcement is disallowed except in explicitly-receipted recovery modes.

### 3) Service jails and control plane compartments

- The host can enforce verified-exec globally for the base.
- Service compartments can opt into stricter enforcement (deny unknown libs, deny unexpected reads).

## Operational escape hatches (must be explicit)

Verified-exec mechanisms are only usable if recovery is planned:

- Provide a **forensics/recovery profile** (monotonic, receipted) that can be activated only with explicit authority.
- Any exception is a policy decision record input and must show up in blast-radius diffs.

## Related docs

- Mile-high direction: `docs/103-runtime-verified-execution.md`
- MAC/veriexec research notes: `docs/53-verified-exec-mac-veriexec.md`
- Change sets apply engine: `docs/219-change-sets-and-apply-engine.md`
- Evidence spine: `docs/229-evidence-spine-overview.md`

Last updated: 2026-02-25
