# Hardware compatibility gates + safe upgrades (avoid bricking remote hosts)

The most painful “atomic upgrade” failures are not package conflicts — they’re hardware regressions:

- new kernel drops a NIC driver and the box never comes back
- storage controller needs a module/firmware floor and boot fails
- GPU stack changes and the console is gone

Traditional OSes handle this with a mix of superstition and out-of-band tooling.
DeriveBSD can treat it as a first-class, typed **gate** that integrates with generations, rollbacks, and receipts.

## Goal

Before switching a host to a new generation, we should be able to answer:

> “Given this host’s hardware, will the target generation boot and provide the minimum required services?”

…and if the answer is “probably not”, we should fail fast **before** flipping the pointer.

## Evidence object: `hw.compat.report`

A compatibility report is emitted during a preflight check and can be used as a gate in change sets.

Schema: `spec/hw.compat.report.schema.json`

Inputs (typical):
- `hw.inventory.receipt` digest (what hardware is present now)
- optional `hw.support.matrix` digest (what hardware classes are declared supported for this release/generation/reset bundle, how far those claims were qualified, which typed qualification receipt backs them, which `hw.support.qualification.profile` defined the required checks, which `release_train` those claims were published for, and when that qualification stops counting as fresh via `fresh_until`)
- `fw.inventory.receipt` digest (firmware posture, if emitted)
- target generation digest + closure proof (what we’re about to run)
- planned module set (`kmod.load.plan`) and firmware plans (if any)
- policy decisions (what we’re allowed to do)

Outputs:
- `status`: `ok` | `warn` | `fail`
- structured findings with reason codes (missing driver, policy denied, needs reboot, etc.)
- optional `support_matrix` join state (`matched`, `conditional`, `miss`, `not-used`) when bundled support/admission catalogs participate
- matrix-entry `qualification` summary (`stage`, `verified_roles`, `evidence_floor`, `regression_policy`, `profile_digest`, `receipt_digest`) when support promotion posture matters
- receipt freshness state (`fresh_until`, `reverify_on`) when a matched support claim needs an actual freshness answer instead of “recently tested” prose
- receipt publication state (`decision.status`, `status_effective_at`) when a matched support claim has been replaced or withdrawn rather than merely aged out
- target-scope answer (`target_binding`, `matched_target_binding`, `target_scope_state`) when a matched support claim may no longer apply to the report target
- recommended gating action (`allow`, `deny`, `require-breakglass`, etc.)

## What we check (v0)

### Boot-critical path

- storage controller driver/module present
- rootfs transport supported (ZFS module posture, lazy-rootfs adapters if used)
- required boot artifacts referenced by `boot.manifest` (if secure/measured boot lane is enabled)
- when `hw.support.matrix` is used, boot-critical devices should match a supported or explicitly-conditional entry rather than free-text support folklore
- positive support entries should carry a typed `qualification` summary so “supported” / “conditional” / `canary-only` mean something reviewable on the release train
- that summary should point at `qualification.receipt_digest` so the support claim remains bundleable and does not depend on ticket portals or lab folklore
- it should also point at `qualification.profile_digest` so the receipt is anchored to a typed qualification standard rather than a lab-specific playlist
- that typed standard should now also define freshness (`max_age_days_by_stage`, `reverify_on`), and the receipt should carry the concrete `fresh_until` bound it derived from that profile
- positive matrix entries should only point at an `accepted` receipt; if the backing receipt becomes `superseded` or `revoked`, the next published matrix should update the digest or downgrade/remove the support claim
- `boot-storage` claims should be backed by `qualification.evidence_floor` including `boot`, `generation-switch`, and, for B/D boot-floor posture, `rollback-or-recovery`
- the receipt behind that summary should record `check_results[]` keyed to the profile `check_id`s rather than leaving the actual pass set implicit

### Network reachability floor

For remotely managed fleets, “don’t brick networking” is table stakes:

- at least one primary NIC binding exists and is allowed by policy
- required firmware payloads are in the closure (or a firmware plan is staged)
- support-matrix misses for required `primary-network` roles can become `support-matrix-miss` or stricter gate outcomes in A/D lanes

### Trusted UI floor (especially for B)

For workstations, “it booted” is not enough if the user loses trusted display/input or has no recovery path:

- display/input/storage floor expectations may be declared in `hw.support.matrix` roles such as `trusted-display`, `trusted-input`, and `boot-storage`
- if the target only has conditional support for those roles, the report should emit `trusted-ui-floor-risk`
- entries that claim those roles should carry `qualification.evidence_floor` including `trusted-ui-basic` so the support matrix says what was actually rechecked
- if warnings depend on a recovery path that has not been recently verified, the report should emit `recovery-path-missing` instead of pretending consent alone makes the switch safe
- if a matched support claim is backed by a receipt whose `fresh_until` has elapsed (or whose `reverify_on` trigger landed), the report should emit `qualification-stale` instead of treating the claim as freshly revalidated support
- if that matched receipt has `decision.status = superseded`, the report should emit `qualification-superseded` and point at the replacement digest rather than pretending ordinary staleness is the whole story
- if that matched receipt has `decision.status = revoked`, the report should emit `qualification-revoked` and stop treating the old proof as current positive support evidence
- if the matched support proof only applies to another `release_train` or boot-manifest lineage, the report should emit `qualification-target-mismatch` and surface `matched_target_binding` / `target_scope_state` instead of pretending ordinary staleness is the whole story
- for B/D trusted-UI or boot-floor claims, support promotion should normally include `rollback-or-recovery` in the qualification floor rather than treating recovery as implied

### Device policy coherence

- device grants + devfs rulesets match the hardware classes discovered
- no new high-risk devices become accessible by default (HID, USB storage, camera/mic)

### Kernel mutation coherence

- planned modules match bindings observed in inventory
- runtime module loads are not required for “basic boot” unless explicitly allowed

## Profile-shaped default

When preflight used a support matrix, `hw.compat.report.support_matrix` may also surface `matched_qualification_receipt_digests` so the gate explanation can point at the exact evidence object backing the matched support claim. Those receipts now in turn point at `qualification.profile_digest`, carry `fresh_until` plus `reverify_on`, carry `qualification.target_binding`, and carry publication-state data through `decision.status` / `status_effective_at`, giving the gate durable answers for what standard the support claim was qualified against, whether that qualification is still fresh enough to count, whether the proof was later replaced or withdrawn, and whether that proof still applies to this target at all.

The archive now fixes the product-default strength of this lane in `docs/479-hardware-compatibility-posture-by-profile.md`:

- **A** treats `hw.compat.report` as a blocking preflight for boot-critical and remote-management-floor failures, with cohorting by hardware class summaries and explicit breakglass for overrides.
- **B** treats boot/display/input/storage floor failures as blocking by default; warnings must be trusted-UI-visible and paired with a verified recovery path before user consent can proceed.
- **C** keeps compatibility preflight preferred and receipted, while preserving an explicit local override for broad-compatibility and lab workflows.
- **D** treats compatibility as admission-first support policy: approved hardware classes/support matrices travel with production bundles and reset media instead of relying on live best-effort probing.

This keeps `hw.compat.report` from drifting into either empty ceremony or one-size-fits-all rigidity.

## Integration points

### Change sets

A standard host switch can include:

1) generate/refresh `hw.inventory.receipt`
2) run `hw.compat.check` → emit `hw.compat.report`
3) block the switch if `status=fail` (unless policy grants breakglass)

The report digest is included in the `change.receipt` so postmortems can answer: “we knew this was risky”.

### Rollout cohorts

Rollouts can cohort on hardware class summaries from the inventory receipt:

- “Intel i219 NIC class”
- “Broadcom bnxt class”
- “NVMe controller family X”

This makes canaries meaningful without building a bespoke fleet database.

### Boot assessment

If the host boots but fails health checks, boot-try counters can auto-rollback.
The compatibility report then becomes a strong signal for why the rollback happened.

See: `docs/112-health-gated-updates.md`, `docs/69-host-generations-bectl.md`, and curated references on boot assessment.

## Open questions

- What is the minimal “remote management floor” for different deployment classes (headless server vs workstation)?
- How do we represent “driver present but known-bad” (CVE’d firmware, broken module version) as a policy decision?
- What is the smallest useful diff/review surface for `hw.support.matrix` changes across release trains?

Support-matrix joins now also treat published support caveats as first-class input: non-fully-supported entries publish typed `conditions[]`, reports may surface `matched_condition_ids`, and `hw.compat.report` may emit `support-condition-triggered` when one of those published caveats/prerequisites participated in the outcome. They now also treat support target scope as first-class input: positive claims publish `target_binding`, reports may surface `matched_target_binding` plus `target_scope_state`, and `hw.compat.report` may emit `qualification-target-mismatch` when older proof does not cover the current `release_train` or boot-manifest lineage.

See risk register items 43 and 49.

Last updated: 2026-03-17r264

Support-matrix joins now also treat published support caveats as first-class input: non-fully-supported entries publish typed `conditions[]`, reports may surface `matched_condition_ids`, and `hw.compat.report` may emit `support-condition-triggered` when one of those published caveats/prerequisites participated in the outcome.
