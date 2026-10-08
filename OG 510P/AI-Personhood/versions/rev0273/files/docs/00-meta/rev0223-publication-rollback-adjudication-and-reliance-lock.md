# rev0223 Publication rollback adjudication and post-recompute reliance lock

rev0223 closes the seam after `rev0222`: a floor recompute receipt can prove that a computed snapshot matched fresh replay at one moment, but it does not by itself prove that publication remains safe after late challenge, revocation, supersession, or rollback evidence appears.

The riskiest failure was publication durability. Once a clean hash-bound zero-floor snapshot exists, maintainers could start treating it as stable doctrine instead of a replayed operational state. That is especially dangerous for a future nonzero floor: a late challenge must reopen the publication posture immediately, not wait for a human to remember which registry or queue item mentioned rollback.

## Executable change

rev0223 adds `live-receipt-publication-rollback-adjudication` as the post-recompute gate. It consumes a floor recompute receipt, rereads the linked computed snapshot, checks the snapshot hash, scans receipt-import challenge/rollback records, and emits only a publication-continuation decision. It cannot increment the floor, satisfy quorum, or create ordinary reliance by itself.

The enforced tail is now:

`computed floor -> floor recompute receipt -> publication rollback adjudication`

The adjudication blocks if any of these are true:

- the recompute receipt is not current or publishable;
- the linked computed snapshot hash no longer matches the recompute receipt;
- a late challenge is open;
- an upheld rollback is incomplete;
- supersession or revocation has not been replayed;
- failed-gate/public notice readiness is missing.

## Refactor/audit

The admission graph and artifact import invariant report now include the publication rollback adjudication node. This moves the final publication/reliance boundary out of prose and into generated checks.

The release lint path includes the new adjudication audit and active schema/example pair. The historical replay remains opt-in; the active package path stays focused on concrete overclaim risks.

## Current posture

The archive still has no genuine external artifact, no verified live response, no live intake, no actual live import, no floor activation, no quorum participation, and no reliance upgrade. The current adjudication is `eligible-zero-floor-stayed`: it permits continued publication of the zero-floor posture only because the snapshot/recompute hash matches and the existing rollback fixture is already completed with zero floor effect.
