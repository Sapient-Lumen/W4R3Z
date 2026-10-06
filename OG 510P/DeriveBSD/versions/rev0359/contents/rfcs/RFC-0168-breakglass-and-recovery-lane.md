# RFC-0168: Breakglass and recovery lane

- Status: draft
- Author(s):
- Created: 2026-02-25
- Last updated: 2026-02-25

## Summary

Introduce a **recovery lane** for DeriveBSD that enables repairs without bypassing the evidence spine.

- Per-generation **Recovery Specialisation** (minimal boot entry)
- Typed breakglass objects:
  - `breakglass-grant`
  - `breakglass-receipt`
  - `breakglass-event`

## Motivation

Recovery exists whether we design it or not.
If it’s an undocumented root shell, we get:

- policy bypass
- missing audit trails
- inability to answer “who did what, why?”

We want the safety posture of:
- Junos “commit confirmed” auto-rollback for risky changes
- NixOS “specialisations” for alternate boot entries
- OpenBSD `bsd.rd` for a minimal recovery environment

References:
- Junos commit confirmed: https://www.juniper.net/documentation/us/en/software/junos/cli/topics/topic-map/junos-configuration-commit.html
- NixOS specialisation: https://nixos.wiki/wiki/Specialisation
- OpenBSD `bsd.rd`: https://www.openbsd.org/faq/faq4.html

## Goals

- Make breakglass entry explicit, time-bounded, and queryable.
- Preserve evidence (event journal + receipts) even during recovery.
- Provide a sane fleet story: lockout recovery without a pager-only ritual.

## Non-goals

- Preventing a physical attacker with full control of the machine.
- Eliminating the need for a privileged shell *entirely*.

## Proposal

### 1) Recovery Specialisation per generation

Build a recovery boot entry alongside each generation:

- minimal userspace
- root mounted read-only by default
- only essential bundles
- tools for `derive status/diff/explain/rollback/apply`

### 2) Breakglass as evidence

Add new evidence objects (schemas under `spec/`):

- `breakglass-grant`: preauthorization + constraints
- `breakglass-receipt`: approved session details
- `breakglass-event`: entered/exited/extended/denied

The structured event journal carries the event envelope; the breakglass objects are referenced by digest.

### 3) Guardrails

Default constraints:

- short expiry
- optional two-person approvals
- network disabled unless explicitly granted
- automatic elevation of lockdown posture (or “forensics mode”)

### 4) Integration points

- `incident.bundle` MAY include recent breakglass receipts (metadata only) for postmortems.
- config transactions for risky changes SHOULD prefer commit-confirmed semantics.

## Backwards compatibility

- Entirely additive. No existing artifacts change semantics.

## Security considerations

- Breakglass is sensitive authority; grants should require signatures and strong authentication.
- Breakglass should not allow deleting or rewriting evidence.

## Open questions

- Do we require a hardware-backed breakglass key (TPM-sealed token / FIDO2) by default?
- How should breakglass interact with verified execution (if enabled)?

See: `docs/236-breakglass-and-recovery-mode.md`, `docs/102-emergency-grafts.md`, `docs/218-configuration-transactions-and-receipts.md`.
