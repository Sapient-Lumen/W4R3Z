# ADR-0210: Restore plans and receipts stay quarantine-first and promotion-shaped

- Status: Accepted
- Date: 2026-03-21

## Context

The archive already decided that backup/recovery posture is profile-shaped (`docs/464-backup-and-restore-posture-by-profile.md`), that backup runs are typed derived operations (`docs/316-backups-and-restores-as-derived-operations.md`), and that restore drills produce `restore.drill.receipt` evidence (`docs/317-restore-drills-and-continuous-recovery-testing.md`).

But the archive drifted in one expensive place:

- `spec/restore.plan.schema.json` and `spec/restore.receipt.schema.json` already exist,
- the artifact index already lists `restore.plan` and `restore.receipt`,
- while one of the core backup/restore docs still says those artifacts are not standardized yet.

That split-brain state is dangerous because restore is where product shapes quietly fall back to folklore:

- fleet hosts drift toward direct overwrite from whatever replica arrived first,
- workstations drift toward ad-hoc import/clone/recover helpers with no typed replacement boundary,
- general-purpose installs inherit whichever compatibility recovery tool happened to run,
- and factory/regulatory restore paths lose the distinction between rehearsal and production replacement.

The archive needs one official answer for whether restore is a speculative future lane or a real typed lane worth implementing now.

## Decision

1. `restore.plan` and `restore.receipt` are official archive artifacts now.
   They are no longer future placeholders.

2. Ordinary restore remains **quarantine-first**.
   The normal restore targets are `quarantine-namespace`, `microvm-drill`, or `readonly-mount`.
   Those targets prove bytes, keys, procedure, and health before any live replacement claim.

3. `replacement-target` is a stronger, explicit promotion lane, not the baseline restore shape.
   When `restore.plan.target.mode = replacement-target`, the plan must also carry a typed `replacement_precondition` describing how that stronger step was justified.

4. `replacement_precondition` is intentionally small and exact:
   - `mode = quarantine-verified` requires `prior_restore_receipt_digest`
   - `mode = breakglass-approved` requires `authority_receipt_digest`

5. `restore.receipt` must echo the replacement posture in detached evidence form.
   A replacement-target receipt should remain explainable away from the original plan by carrying `replacement_precondition_mode` plus the joined prior restore or authority digest in `evidence`.

6. No new `product.profiles.defaults` key is introduced.
   This ADR fixes the shared restore operation boundary that existing profile defaults compile through.

## Consequences

- The archive now consistently teaches that restore is a typed lane worth implementing, not a future note.
- Restore drills remain important, but they supplement restore apply instead of substituting for it.
- Replacement restores stay auditable and harder to smuggle in as “just recovery tooling.”
- Workstations keep a humane visible recovery story, fleets/factories keep promotion-grade restore proof, and general OS keeps explicit compatibility adapters without redefining the managed lane.

## What this does not decide

This ADR does **not** decide:

- the final restore UI or portal surfaces,
- the concrete restore backend engines,
- detailed health-check taxonomies,
- retention/export defaults for restore evidence,
- or restore-target quarantine implementation details.

It only fixes the official restore artifact boundary and the rule that live replacement must be promotion-shaped rather than silently implied.
