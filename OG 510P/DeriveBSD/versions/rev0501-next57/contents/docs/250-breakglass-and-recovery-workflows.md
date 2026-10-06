# Breakglass and recovery workflows (evidence-bearing emergency operations)

DeriveBSD’s security posture dies the day “emergency” becomes synonymous with
“drop to root and do whatever it takes”.

This doc tightens the breakglass lane into a set of **repeatable, reviewable workflows**
that work across:
- host activation failures
- recovery image sessions
- installer / reprovisioning flows

Breakglass is not a permission bit. It is a **time-bounded authority lease** that always emits
**receipts** and can be audited later.

Related docs:
- Breakglass mode and evidence objects: `docs/236-breakglass-and-recovery-mode.md`
- The product-shaped recording/detail/export defaults for those emergency sessions now live in `docs/618-breakglass-recording-detail-and-export-posture-by-profile.md`
- Consent + multiparty approvals: `docs/256-consent-ux-contract.md`, `docs/288-multiparty-approvals-and-separation-of-duties.md`
- Installation/recovery as derived operations: `docs/309-installation-and-recovery-as-derived-operations.md`
- Change sets and apply engine: `docs/219-change-sets-and-apply-engine.md`


## 1) The minimum contract

Breakglass must satisfy four invariants:

1) **Explicit**: no implicit “well, it’s recovery, so anything goes”.
2) **Digest-bound**: approvals grant authority against a specific Plan / action set.
3) **Time-bounded**: every breakglass grant has expiry + revocation.
4) **Receipted**: every use emits a typed receipt and is included in incident/support bundles.


## 2) Evidence objects (existing)

DeriveBSD already defines:

- `breakglass.grant` — the approval/lease object
- `breakglass.receipt` — what was exercised under the grant
- `breakglass.event` — revocations / escalations / audit events

See schemas:
- `spec/breakglass.grant.schema.json`
- `spec/breakglass.receipt.schema.json`
- `spec/breakglass.event.schema.json`


## 3) Workflow patterns to bake in

### A) “Commit-confirmed” risky changes (networking, boot, crypto)

When a change is likely to brick a node (routing, bootchain, disk layout, unseal policy),
prefer a **confirmable transaction**:

1) Apply the change as a change set with a *pending* state.
2) System must confirm success within a deadline (health checks + reachability).
3) If unconfirmed, auto-revert to the previous safe state.

If confirmation is impossible (e.g., console-only), require breakglass.

(See: `docs/218-configuration-transactions-and-receipts.md`.)


### B) Breakglass “repair window” for activation failures

When a host cannot switch generations safely:

1) Operator requests a breakglass grant specifying:
   - target host identity (or cohort)
   - the exact failure class (boot failure, kmod mismatch, hw compat failure)
   - the proposed repair actions as a Plan digest (or change set digest)
   - expiry + required approvals (single vs quorum)
2) Recovery session applies the repair Plan.
3) Emit `breakglass.receipt` that links:
   - and records `ordinary_resumption_posture = fresh-attestation-after-breakglass-created-at-required`, so ordinary attestation-gated lanes need fresh post-breakglass attestation before resuming, with the pinned `attestation.receipt.created_at` strictly later than the exact breakglass receipt `created_at`
   - the grant digest
   - the applied Plan/change set digests
   - the resulting activation/bootenv receipts
   - and `repair_outcome` as the authoritative closeout summary, so session end is not mistaken for repair proof
4) Immediately revoke/expire the grant.

If that repair actually used an interactive shell or recovery console and emitted terminal evidence, the receipt should also carry `evidence.tty_recording_digests` plus `evidence.tty_recording_start_posture = session-open-before-first-prompt`, so detached tooling can find the exact `tty.session.recording` artifact and the strongest early shell actions do not fall outside the reviewed evidence boundary.
OOB approval still works for this workflow, but approval transport is not the same thing as session method. The reviewed breakglass method vocabulary is concrete: remote-presence adapters must project to `console`, `serial`, or `ssh` rather than claiming a generic `oob` access surface. That keeps BMC KVM, SOL, and virtual-media bootstrap steps from collapsing into one blurry authority noun (`docs/706-breakglass-session-methods-stay-concrete-and-oob-adapters-project-into-them.md`). When a reviewed maintenance boot or reset materially led into the emergency session, the receipt should also carry `evidence.bootstrap_receipt_joins[]` plus `bootstrap_join_posture = pre-session-recovery-path-only`, pinned to the exact `boot.override.receipt` / `reset.receipt` digests instead of retelling that earlier recovery path in notes (`docs/707-breakglass-bootstrap-joins-stay-exact-receipt-typed-and-pre-session-only.md`). If more than one such receipt mattered, also carry `bootstrap_join_sequence_posture = earliest-to-latest-pre-session-enabling-only` and list only the enabling receipts in causal order rather than mixing in denied attempts, failed dead ends, or BMC dashboard breadcrumbs (`docs/708-breakglass-bootstrap-joins-stay-enabling-only-and-earliest-to-latest-when-plural.md`). In the common paired one-time-boot case, keep `boot.override.receipt` first and the later `reset.receipt` second, because reset is the actuation step rather than the boot-selection step; equivalently, keep `boot.override.receipt` before the later `reset.receipt` (`docs/709-breakglass-bootstrap-joins-keep-boot-override-before-reset-when-both-participate.md`). Separate adapter launch/runtime detail still stays redacted side evidence: do not widen the baseline receipt with BMC URLs, ports, session ids/tokens, copied console-entry hints, or image locators, and do not smuggle that material back in through `notes` (`docs/710-breakglass-adapter-details-stay-redacted-side-evidence-and-off-baseline-receipt.md`).

Key rule: repairs are “just” **derived operations** executed under a lease. Session end is not repair proof; if work materially happened, `repair_outcome` must say whether it is observation-only, pending confirm, confirmed, rolled back, or failed, and non-observation closeout must carry exact authoritative receipt digests.


### C) Installer / reprovision breakglass (destructive operations)

Disk mutation is the sharpest knife.
So:

- destructive edits (shrink/remove partitions, wipe pools, factory reset) now belong to the explicit **`reset.authorization`** → **`reset.receipt`** lane (see `docs/483-destructive-reprovisioning-and-reset-authority.md`)
- the product-shaped evidence/detail/export defaults for that destructive lane now live in `docs/619-destructive-reprovision-evidence-detail-and-export-posture-by-profile.md`
- `breakglass.grant` remains one possible authority input for that lane, but not the only one
- product shapes that need physical or attended reset signals can require them through the same typed contract instead of hiding them in installer folklore

This keeps “oops, the installer wiped the wrong disk” from becoming folklore.

(See: `docs/310-disk-layout-plans-and-receipts.md`, `docs/483-destructive-reprovisioning-and-reset-authority.md`.)


### D) “Policy override, not policy bypass”

Breakglass should *not* disable policy. It should switch policy into an **override mode** where:

- the override is explicit in the policy decision record
- the scope is narrow (specific component / dataset / capability)
- the override has an expiry
- the override is surfaced loudly in `derive explain`

If a backend can’t express the override cleanly, the safe answer is: don’t support it yet.


## 4) UX goals (what must feel boring)

The safe path must be simpler than the unsafe path.
Bake in these operator affordances early:

- `derive breakglass request …` prints the exact digest-bound object to approve.
- `derive breakglass approve …` produces a signed grant (or imports an OOB approval).
- `derive breakglass status` lists active grants and their expiry.
- `derive breakglass revoke …` emits a revocation event.
- Any `derive apply` run under breakglass prints a prominent banner and emits receipts automatically.


## 5) Failure modes to explicitly design for

- **Network is down**: approvals must work offline / OOB.
- **Time is untrusted**: expiry checks must degrade safely (use LKGT bounds; see `docs/283-trustworthy-time-nts-roughtime-and-lkgt.md`).
- **Keys are unavailable**: breakglass may authorize *limited* “bring-up” steps to restore crypto domains.
- **Monotonic rollback defenses**: breakglass cannot become a permanent downgrade bypass.


## 6) Where this plugs into the archive

- Non-negotiable behavior: breakglass is explicit/timebounded/receipted (`docs/97-non-negotiable-behaviors.md`).
- Incident bundles should automatically include breakglass receipts (`docs/216-incident-snapshots-and-support-bundles.md`).
- official support handoff can now carry `breakglass_receipt_digests` on the typed bundle contract instead of leaving emergency-access proof to rescue-shell folklore, operator memory, or ticket prose (`docs/629-incident-bundles-carry-breakglass-proof-by-digest.md`).
- that support contract now stays authority-first on `breakglass_receipt_digests`; richer adapter/runtime investigation material may travel only as supplementary `includes.extra[]` evidence or external case attachments until a dedicated typed family exists (`docs/711-breakglass-adapter-side-evidence-stays-off-first-class-bundle-contract-until-typed-family-exists.md`).
- supplementary adapter/runtime exports receipt-first on typed redaction/export/transport evidence rather than raw attachment handles or ticket prose (`docs/712-breakglass-supplementary-adapter-side-evidence-stays-receipt-first-when-exported.md`).
- supplementary adapter/runtime exports must also stay authority-anchored: if that richer material travels in a bundle or case handoff, keep at least one exact `breakglass_receipt_digests` join in the same portable story rather than sending orphan receipt chains (`docs/713-breakglass-supplementary-adapter-side-evidence-stays-authority-anchored-when-portably-carried.md`).
- portable supplementary breakglass adapter/runtime evidence must also stay artifactized: do not send live console URLs, copied `ConsoleEntryCommand` values, `WebSocketEndpoint` strings, virtual-media image locators, or session ids/tokens as the archive-facing story (`docs/714-breakglass-supplementary-adapter-side-evidence-stays-artifactized-and-off-live-control-locators.md`).
- supplementary adapter/runtime exports must also stay payload-anchored: carry at least one passive artifact digest or accepted case-object proof in the same portable story rather than a receipt-only chain that proves handling happened but never names the artifact/object handled (`docs/715-breakglass-supplementary-adapter-side-evidence-stays-payload-anchored-when-portably-carried.md`).
- when that payload anchor uses accepted case-object proof, keep it object-exact on the accepted remote attachment/object/message-part identity rather than a parent case/ticket/thread/container id (`docs/716-breakglass-supplementary-accepted-case-object-proof-stays-object-exact-when-portably-carried.md`).
- when that accepted-case-object lane can see a revision/version/generation/ETag-like validator for the same accepted remote object, keep the accepted-case-object lane, keep it validator-pinned too when the adapter can see one instead of collapsing back to object id alone (`docs/717-breakglass-supplementary-accepted-case-object-proof-stays-validator-pinned-when-visible.md`).
- when that same accepted-case-object lane can also see a protection/retention/hold posture for the same accepted remote object, keep the accepted-case-object lane remote-protection-shaped too when visible instead of calling any accepted portal object durable evidence by implication (`docs/718-breakglass-supplementary-accepted-case-object-proof-stays-remote-protection-shaped-when-visible.md`).
- keep that visible protection posture exact to the same accepted object revision/version too; ambient case/container/bucket policy is context only rather than a substitute for object-exact protection proof (`docs/719-breakglass-supplementary-accepted-case-object-proof-keeps-visible-remote-protection-exact-to-the-same-object-revision.md`).
- when that same accepted-case-object lane can also see a redacted/non-secret passive locator for the same accepted remote object revision/version, keep it remote-locator-continuous too instead of falling back to parent case/container browse URLs or portal clicking; live control locators remain forbidden (`docs/720-breakglass-supplementary-accepted-case-object-proof-stays-remote-locator-continuous-when-visible.md`).
- when that same accepted-case-object lane can later metadata-check the same accepted remote object revision/version without re-downloading the body, keep metadata-only reverification too when visible on typed `transport.reverification.receipt`; canonical follow-up keeps `body_downloaded = false` instead of screenshots or body-download folklore (`docs/721-breakglass-supplementary-accepted-case-object-proof-stays-metadata-only-reverifiable-when-visible.md`).
- Risk register should treat “breakglass abuse” as a first-class ops risk (`docs/266-open-questions-and-risk-register.md`).

When that ordinary resumption actually happens, the ordinary receipt should carry the exact breakglass receipt digest through `attestation_verification.relevant_breakglass_receipt_digest`; recovery should not rely on “pick the latest breakglass for this host” folklore or cross-host join folklore. The joined breakglass and attestation receipts must still name the same host. The later ordinary receipt must not predate the pinned `attestation.receipt.created_at`.
Last updated: 2026-03-23r452
