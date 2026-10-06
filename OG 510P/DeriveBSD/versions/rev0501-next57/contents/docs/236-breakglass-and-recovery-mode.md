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

These objects are stored like any other evidence and can be included in an incident bundle. Official support handoff can now carry `breakglass_receipt_digests` when emergency access participated, which keeps typed authority proof separate from any richer terminal/console trails (`docs/629-incident-bundles-carry-breakglass-proof-by-digest.md`). Official support handoff stays authority-first too: `official support handoff stays authority-first` is the rule, and  richer breakglass adapter/runtime investigation material may ride only as supplementary `incident.bundle.includes.extra[]` evidence or explicit case attachments until a dedicated typed family exists (`docs/711-breakglass-adapter-side-evidence-stays-off-first-class-bundle-contract-until-typed-family-exists.md`). If that supplementary material travels, keep the portable story receipt-first on typed redaction/export/transport receipts rather than raw case attachment ids or portal handles (`docs/712-breakglass-supplementary-adapter-side-evidence-stays-receipt-first-when-exported.md`). Do not let that supplementary receipt chain travel alone: keep at least one exact `breakglass_receipt_digests` join in the same portable story so later review is anchored to typed emergency authority (`docs/713-breakglass-supplementary-adapter-side-evidence-stays-authority-anchored-when-portably-carried.md`). Even then, keep the portable story artifactized rather than live-locator-shaped: do not carry console URLs, copied `ConsoleEntryCommand` values, `WebSocketEndpoint` strings, image locators, or session ids/tokens as supplementary breakglass truth (`docs/714-breakglass-supplementary-adapter-side-evidence-stays-artifactized-and-off-live-control-locators.md`). Keep that same portable story payload-anchored instead of receipt-only: carry at least one passive artifact digest or accepted case-object proof so later review does not need portal archaeology to rediscover what artifact the handling receipts described (`docs/715-breakglass-supplementary-adapter-side-evidence-stays-payload-anchored-when-portably-carried.md`). If the payload anchor uses accepted case-object proof, keep it object-exact too: name the exact accepted remote attachment/object/message-part rather than only the parent case/ticket/thread/container id (`docs/716-breakglass-supplementary-accepted-case-object-proof-stays-object-exact-when-portably-carried.md`). If that accepted-case-object lane can also see a revision/version/generation/ETag-like validator for the same accepted remote object, keep it validator-pinned too when visible instead of letting the portable story slide back into object-latest portal semantics (`docs/717-breakglass-supplementary-accepted-case-object-proof-stays-validator-pinned-when-visible.md`). If that same accepted-case-object lane can also see a protection/retention/hold posture for the same accepted remote object, keep it remote-protection-shaped too when visible instead of quietly treating any accepted portal object as durable evidence by implication (`docs/718-breakglass-supplementary-accepted-case-object-proof-stays-remote-protection-shaped-when-visible.md`). Keep that visible posture exact to the same accepted object revision/version too; ambient case/container/bucket policy is context only rather than a substitute for object-exact protection proof (`docs/719-breakglass-supplementary-accepted-case-object-proof-keeps-visible-remote-protection-exact-to-the-same-object-revision.md`). If that same accepted-case-object lane can also see a redacted/non-secret passive locator for the same accepted remote object revision/version, keep it remote-locator-continuous too instead of falling back to parent case/container browse URLs or portal clicking; live control locators remain forbidden (`docs/720-breakglass-supplementary-accepted-case-object-proof-stays-remote-locator-continuous-when-visible.md`). If that same accepted-case-object lane can later metadata-check the same accepted remote object revision/version without re-downloading the body, keep metadata-only reverification too when visible on typed `transport.reverification.receipt` with `reverification.body_downloaded = false` instead of screenshots or body-download folklore (`docs/721-breakglass-supplementary-accepted-case-object-proof-stays-metadata-only-reverifiable-when-visible.md`).
The product-shaped recording/detail/export defaults for emergency sessions now live in `docs/618-breakglass-recording-detail-and-export-posture-by-profile.md`, and the first reviewed interactive shell/console lane now joins exact terminal evidence back through `breakglass.receipt.evidence.tty_recording_digests` with `tty_recording_start_posture = session-open-before-first-prompt` instead of rescue-shell folklore about starting capture later.
Breakglass session methods stay concrete too: `console`, `serial`, and `ssh` are the reviewed access surfaces. OOB approval still exists, but it is not a session method. BMC KVM/HTML5 console projects to `console`, Serial-over-LAN projects to `serial`, and virtual-media boot is bootstrap plumbing until it yields an actual breakglass session or a separate install/reset lane (`docs/706-breakglass-session-methods-stay-concrete-and-oob-adapters-project-into-them.md`). If a reviewed maintenance boot or reset materially enabled that session, `breakglass.receipt.evidence.bootstrap_receipt_joins` now points at the exact `boot.override.receipt` / `reset.receipt` digest with `bootstrap_join_posture = pre-session-recovery-path-only`. When plural, that array is also constrained by `bootstrap_join_sequence_posture = earliest-to-latest-pre-session-enabling-only`, so support does not have to reconstruct the real recovery path from denied attempts, ticket prose, or BMC breadcrumbs (`docs/707-breakglass-bootstrap-joins-stay-exact-receipt-typed-and-pre-session-only.md`, `docs/708-breakglass-bootstrap-joins-stay-enabling-only-and-earliest-to-latest-when-plural.md`). In the common one-time maintenance-boot path where both receipts participate, `boot.override.receipt` comes before the later `reset.receipt` that actuated it (`docs/709-breakglass-bootstrap-joins-keep-boot-override-before-reset-when-both-participate.md`). Richer adapter launch/runtime detail such as remote console URLs, ports, session ids/tokens, copied `ConsoleEntryCommand` hints, or image locators stays redacted side evidence and out of the baseline breakglass receipt (`docs/710-breakglass-adapter-details-stay-redacted-side-evidence-and-off-baseline-receipt.md`).

All breakglass grants are treated as leases: `lease_id` is the canonical cross-lane identifier (with `grant_id` retained as a legacy alias for compatibility). Breakglass closeout is also typed now: `breakglass.receipt.repair_outcome` distinguishes `observation-only`, `repair-pending-confirmation`, `repair-confirmed`, `repair-rolled-back`, and `repair-failed`, and any non-observation closeout must join the exact authoritative repair receipt digests instead of hiding “recovery completed” in notes.

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
- a failed confirmation should auto-rollback to a known-good generation. The breakglass receipt should say `repair-pending-confirmation`, `repair-confirmed`, `repair-rolled-back`, or `repair-failed` explicitly rather than treating shell exit as repair proof.
- breakglass receipts are useful fleet-wide signals (“why did this host need emergency access?”)

See: `docs/218-configuration-transactions-and-receipts.md`, `docs/231-ab-updates-and-recovery-semantics.md`.

The reciprocal ordinary lane is now exact and same-host bound too: when a later ordinary secret or workload identity receipt is explaining fresh post-breakglass posture, it should carry `attestation_verification.relevant_breakglass_receipt_digest` so the exact governing breakglass session stays portable instead of being rediscovered from latest-session folklore or cross-host join folklore. The joined breakglass receipt must describe the same host as the pinned attestation receipt. The post-breakglass chain is time-ordered too: the fresh attestation must be strictly later than the breakglass receipt `created_at`, and the later ordinary receipt must not predate the fresh attestation receipt it claims to consume.
Last updated: 2026-03-23r452
