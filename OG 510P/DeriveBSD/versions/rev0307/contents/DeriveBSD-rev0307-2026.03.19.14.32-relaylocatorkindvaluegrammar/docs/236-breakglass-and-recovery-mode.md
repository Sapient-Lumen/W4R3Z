# Breakglass + recovery mode (repair without destroying evidence)

Every OS eventually needs a way to recover from:

- broken networking / remote access lockout
- bad update that prevents boot
- broken policy that blocks critical services
- disk / pool trouble

Most systems solve this with a *raw root shell* (single-user, init=/bin/sh, rescue targets).
That works, but it also tends to:

- bypass auditing
- bypass least-privilege
- destroy the “why did this happen?” trail

DeriveBSD’s greenfield advantage: **make recovery a first-class lane** in the evidence spine.

References (examples worth stealing from):
- Junos `commit confirmed` auto-rollback: https://www.juniper.net/documentation/us/en/software/junos/cli/topics/topic-map/junos-configuration-commit.html
- NixOS “specialisations” (alternate boot entries per generation): https://nixos.wiki/wiki/Specialisation
- OpenBSD `bsd.rd` ramdisk kernel (install/upgrade/recovery): https://www.openbsd.org/faq/faq4.html
- systemd rescue/emergency targets: https://www.freedesktop.org/software/systemd/man/systemd.special.html

## DeriveBSD stance

1) Recovery is **a derived artifact**, not an undocumented escape hatch.
2) Breakglass access is **explicit, time-bounded, and receipted**.
3) Recovery tools are **signed, minimal, and revocable**.
4) “Fixes” should still flow through:
   - `change-set` + `change-receipt`, or
   - `config-transaction` + `config-receipt`, or
   - `emergency grafts` (last resort, still auditable)

## A per-generation “Recovery Specialisation”

For every host generation, build an additional boot entry:

- **Recovery Specialisation**
  - boots a minimal userspace
  - mounts root read-only by default
  - avoids auto-starting non-essential bundles
  - provides *only* the tools needed for inspection + repair

This is similar to NixOS specialisations but is treated as part of the *host artifact*.

## Breakglass entry protocol (typed, not tribal)

Introduce a small lane:

- `breakglass-grant` (permission intent / constraints)
- `breakglass-receipt` (what was approved + who approved, plus optional `attestation_verification` when measured posture gated the session)
- `breakglass-event` (entered/exited/extended/denied)

These objects are stored like any other evidence and can be included in an incident bundle.

All breakglass grants are treated as leases: `lease_id` is the canonical cross-lane identifier (with `grant_id` retained as a legacy alias for compatibility).

### Guardrails

- Breakglass sessions are **timeboxed** (default: short)
- Optional **two-person integrity** for sensitive operations
- Entering breakglass can automatically:
  - raise lockdown level (or flip into a “forensics posture”)
  - disable outbound network by default
  - require local console / physical presence (policy-controlled)

## What you can do in recovery mode

Make recovery power explicit and composable:

- inspect: `derive status`, `derive explain`, `derive diff`
- roll back: `derive rollback` to a known-good boot environment
- apply a repair change-set: `derive apply --change-set ...`
- run a bounded debug capsule (policy-gated): `derive debug replay ...`

The key is that the operator can *always* produce a receipt for the fix.

## What you cannot do (by default)

- delete/overwrite evidence logs
- disable the event journal
- install unsigned binaries into the base

If you *must* do something that violates policy, it should require:
- an explicit breakglass grant with justification, or
- a signed “emergency graft” object

## Fleet implications

Breakglass should be survivable in fleets:

- “commit-confirmed” changes (Junos lesson) should be the default for risky config transactions.
- a failed confirmation should auto-rollback to a known-good generation.
- breakglass receipts are useful fleet-wide signals (“why did this host need emergency access?”)

See: `docs/218-configuration-transactions-and-receipts.md`, `docs/231-ab-updates-and-recovery-semantics.md`.

Last updated: 2026-03-07r221
