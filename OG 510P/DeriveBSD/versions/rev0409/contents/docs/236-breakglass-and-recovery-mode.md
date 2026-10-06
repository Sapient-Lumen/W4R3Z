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
- `breakglass-receipt` (what was approved + who approved, plus optional `attestation_verification` when measured posture gated the session; decisive uses pin the exact requirement/receipt/policy tuple **plus** `attestation_receipt_verdict`, `degraded` only applies when the consumed requirement already allowed degraded posture rather than via a hidden verifier waiver, and unlike ordinary issue/delivery lanes breakglass may explicitly record `decision = rejected` because `rejected`→`fail` stays visible on the explicit emergency lane; it now also carries `ordinary_resumption_posture = fresh-attestation-after-breakglass-created-at-required`, so ordinary attestation-gated lanes resume only on a fresh `attestation.receipt` issued after the breakglass receipt `created_at`, and that later ordinary receipt must not predate the fresh attestation receipt it claims to consume)
- `breakglass-event` (entered/exited/extended/denied)

These objects are stored like any other evidence and can be included in an incident bundle. Official support handoff can now carry `breakglass_receipt_digests` when emergency access participated, which keeps typed authority proof separate from any richer terminal/console trails (`docs/629-incident-bundles-carry-breakglass-proof-by-digest.md`).
The product-shaped recording/detail/export defaults for emergency sessions now live in `docs/618-breakglass-recording-detail-and-export-posture-by-profile.md`.

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

The reciprocal ordinary lane is now exact and same-host bound too: when a later ordinary secret or workload identity receipt is explaining fresh post-breakglass posture, it should carry `attestation_verification.relevant_breakglass_receipt_digest` so the exact governing breakglass session stays portable instead of being rediscovered from latest-session folklore or cross-host join folklore. The joined breakglass receipt must describe the same host as the pinned attestation receipt. The post-breakglass chain is time-ordered too: the fresh attestation must be strictly later than the breakglass receipt `created_at`, and the later ordinary receipt must not predate the fresh attestation receipt it claims to consume.
Last updated: 2026-03-21r382
