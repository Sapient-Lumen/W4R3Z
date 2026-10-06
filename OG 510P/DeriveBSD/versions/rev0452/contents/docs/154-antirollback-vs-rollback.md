# Anti-rollback vs instant rollback

DeriveBSD wants two properties that appear to conflict:

- **Instant rollback**: operators can switch to a prior *known-good* generation quickly (ZFS boot environments / snapshots).
- **Anti-rollback**: the system should not accept *malicious downgrade* to vulnerable versions (a common persistence technique).

This document resolves the tension by **scoping anti-rollback** to *automated acceptance* and *unattended boot*, while keeping **manual rollback** possible under explicit, recorded operator intent.

## Threat model

Rollback attacks matter when an attacker can:

1. influence update metadata or content delivery, or
2. access the device in a way that allows booting older content.

Update frameworks address this by making the client remember the **highest version it has accepted** and rejecting older versions thereafter (unless explicitly permitted).

## Resolution: two acceptance modes

### 1) Automatic acceptance (default)

- Applies to: scheduled updates, unattended boot, self-heal, fleet rollout.
- Rule: **reject** any candidate generation whose version/epoch is less than the local **rollback index** (monotonic), unless within an explicitly defined *rollback window*.
- Evidence: `antirollback.check` records the comparison inputs and decision.

This is the strong path aligned with TUF-style rollback defenses and Android-style rollback indices.

### 2) Manual rollback (explicit override)

- Applies to: operator-initiated rollback for incident response.
- Rule: allowed only if a *policy-gated override* is present:
  - `manualRollbackOverride` with (a) reason, (b) target generation id/digest, (c) TTL/expiry, (d) operator identity, (e) approval threshold if required.
- Effect:
  - Boot is allowed even if target generation < rollback index.
  - The rollback index is **not decremented**.
  - A subsequent automatic update will still refuse versions < rollback index.

### Why this works

- Attackers can’t silently downgrade via the automated path.
- Operators can still recover quickly.
- The system remains convergent: after rollback, the next update must be to a **newer** generation.

## Implementation sketch

- Maintain `rollback_index` in one of:
  - TPM NV index (preferred where available)
  - sealed ZFS dataset with monotonic update semantics
  - monotonic counter managed by the bootloader/loader + sealed state

- Boot-time enforcement:
  - if `mode=auto`: enforce `candidate >= stored_index`
  - if `mode=manual`: require valid `manualRollbackOverride` and record evidence

- Update-time enforcement:
  - only advance `stored_index` after *health-gated success*.

## Decision records

The Plan digest MUST bind:

- `rollback_index_policy` (mode rules, rollback window, override thresholds)
- `manualRollbackOverride` (if present)

This ensures that “rollback allowed” is itself explainable and attributable.
