# Restore plans and receipts stay quarantine-first and promotion-shaped

**Tier:** B (Cross-cutting product-shape decision)  
**Profiles:** A, B, C, D  
**Pillars:** operability, isolation, reproducibility  
**Patterns:** Plan→Apply→Receipt, Quarantine→Promote  

DeriveBSD already decided three important things:

- backup/recovery posture is profile-shaped,
- backups are typed derived operations,
- and restore drills are explicit evidence rather than vague “we tested recovery once” claims.

This doc decides the narrower but more implementation-shaping question:
**what is the official restore apply boundary now that `restore.plan` and `restore.receipt` already exist?**

This is intentionally **not** a new product-profile key.
It is the shared restore contract that the existing `backup_restore`, `installation_recovery`, `destructive_reprovision`, and `evidence` posture surfaces compile through.

See also:
- ADR: `adrs/ADR-0210-restore-plans-and-receipts-stay-quarantine-first-and-promotion-shaped.md`
- backup/restore posture: `docs/464-backup-and-restore-posture-by-profile.md`
- backup lane: `docs/316-backups-and-restores-as-derived-operations.md`
- restore drills: `docs/317-restore-drills-and-continuous-recovery-testing.md`
- install/recovery lane: `docs/309-installation-and-recovery-as-derived-operations.md`
- destructive reset authority: `docs/483-destructive-reprovisioning-and-reset-authority.md`

## Why this needs a hard decision

The archive already had a latent contradiction:

- `restore.plan` and `restore.receipt` schemas/examples were present,
- the artifact index already treated them as real,
- but one of the core restore docs still described them as future work.

That kind of drift is exactly how recovery lanes become folklore again.
If restore stays half-real, implementations will make the expensive choice implicitly:

- direct-overwrite restore becomes normal on fleet hosts because the replica exists,
- workstation “recovery” becomes clone/import/repair tooling with no typed replacement boundary,
- general-purpose installs inherit whichever classic restore helper happened to run,
- and factory/regulatory recovery loses the distinction between rehearsal and production replacement.

A coherent archive needs one boring answer: **restore is a typed lane now, and live replacement is stronger than ordinary restore rehearsal.**

## Accepted baseline

Across all profiles:

- `restore.plan` and `restore.receipt` are official archive artifacts now,
- ordinary restore is **quarantine-first**,
- the normal targets are `quarantine-namespace`, `microvm-drill`, or `readonly-mount`,
- `replacement-target` is a stronger explicit promotion lane, not the baseline restore shape,
- restore drills remain real but are **supplemental** evidence via `restore.drill.receipt`,
- and replacement restore must stay explainable away from the original plan through a typed replacement precondition.

That keeps restore from collapsing into either invisible direct overwrite or endless drill theater.

## Official artifact boundary

### `restore.plan`

`restore.plan` is now the authoritative restore intent object.
It binds:

- the backup evidence being restored (`backup_receipt_digest`),
- the chosen target mode,
- optional check expectations,
- and, for live replacement, the exact stronger precondition that justified it.

When `target.mode = replacement-target`, the plan must carry `replacement_precondition`:

- `mode = quarantine-verified` with `prior_restore_receipt_digest`, or
- `mode = breakglass-approved` with `authority_receipt_digest`.

### `restore.receipt`

`restore.receipt` is now the authoritative restore result object.
It records:

- the plan digest that was actually applied,
- the observed target mode,
- whether the restore mounted and passed checks,
- and the detached evidence needed to explain a stronger replacement apply.

When the restore actually targets a live replacement, the receipt should remain self-describing enough for support bundles and audits to answer **why live replacement was allowed at all** without reopening operator folklore.

### `restore.drill.receipt`

`restore.drill.receipt` remains important, but it is not the same thing as `restore.receipt`.
It proves rehearsal quality, not arbitrary replacement authority.
In the normal path, a quarantine/microVM restore produces `restore.receipt`, and any richer rehearsal/testing can additionally emit `restore.drill.receipt`.

## Product-shape meaning

### A) Secure fleet host

Default meaning: restore stays quarantine-first, and live replacement is maintenance/promotion-shaped.

- Replaceable fleet hosts should prove recovery in quarantine first.
- A live replacement apply should usually point back to a prior verified restore receipt.
- Emergency direct replacement remains breakglass territory, not ordinary replication folklore.

### B) Secure workstation

Default meaning: restore stays visible and bounded before it becomes device- or user-state replacement.

- A workstation restore should not quietly become whole-device clone folklore.
- The trusted path is to restore into a quarantine namespace / rehearsal target first, verify the result, then make any replacement step explicit.
- Breakglass replacement remains available for genuine emergencies, but it is not the baseline recovery UX.

### C) General-purpose OS

Default meaning: compatibility remains possible, but the Derive-managed lane is still quarantine-first and typed.

- Classic restore tooling may exist as adapters.
- The managed restore lane remains worth implementing because it keeps evidence, checks, and replacement authority explicit.
- Compatibility helpers should not redefine the official restore story.

### D) Appliance factory / regulatory

Default meaning: restore rehearsal and production replacement remain distinct proof steps.

- D needs production replacement to be auditable and reviewable.
- Quarantine verification and explicit replacement authorization keep “we restored it” from meaning either a drill or a live production cutover depending on who speaks.
- This is especially valuable for offline or regulated maintenance lanes where promotion proof matters as much as the bytes.

## Cross-profile invariants

Regardless of profile:

- restore binds back to `backup.receipt` rather than ambient snapshot/path lore,
- restore rehearsal and live replacement remain distinct typed steps,
- direct replacement must not be smuggled in through “recovery convenience” tooling,
- `replacement-target` remains stronger than `microvm-drill`, `quarantine-namespace`, or `readonly-mount`,
- and no new product-profile key is added just to describe this boundary.

## What remains open

This doc does **not** freeze:

- final restore frontend UX,
- exact quarantine dataset / microVM mechanics,
- detailed health-check vocabularies,
- restore evidence export/retention posture,
- or backend-specific adapter choices.

Those are real later decisions.
What is worth locking now is that restore is already a real typed lane, and live replacement must stay promotion-shaped instead of silently implied.

Official support handoff join: `docs/626-incident-bundles-carry-restore-apply-proof-by-digest.md`.
Official support handoff can now carry `restore_receipt_digests` rather than backend-specific restore-job logs when recovery matters.

Last updated: 2026-03-21r356
