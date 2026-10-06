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
   - the grant digest
   - the applied Plan/change set digests
   - the resulting activation/bootenv receipts
4) Immediately revoke/expire the grant.

Key rule: repairs are “just” **derived operations** executed under a lease.


### C) Installer / reprovision breakglass (destructive operations)

Disk mutation is the sharpest knife.
So:

- destructive edits (shrink/remove partitions, wipe pools, factory reset) must require
  either:
  - an explicit *factory reset marker* (physical presence signal), and/or
  - a breakglass grant bound to the `disk.layout.plan`.

This keeps “oops, the installer wiped the wrong disk” from becoming folklore.

(See: `docs/310-disk-layout-plans-and-receipts.md`.)


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
- Risk register should treat “breakglass abuse” as a first-class ops risk (`docs/266-open-questions-and-risk-register.md`).

Last updated: 2026-02-26
