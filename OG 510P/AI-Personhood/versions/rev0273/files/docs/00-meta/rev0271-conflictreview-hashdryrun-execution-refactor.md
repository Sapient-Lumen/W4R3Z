# rev0271 — conflict review and hash dry-run execution refactor

rev0271 keeps the archive on the first-contact execution path. It does not add doctrine. It reduces the remaining risk by doing two things that can honestly be completed inside the public release tree:

- shorten the RAIC/AIID contact body from 238 words to 195 words while keeping the collaboration/routing, non-incident, no-custody, no-waiver, and no-floor guards;
- add audited public-language conflict/coercion review and a current public-tree hash recompute dry run.

## Why this was the riskiest next work

After rev0253, the unresolved blockers were mostly human or private-vault dependent. Another broad registry pass could not create human signature, sender account authority, off-release vault roots, actual transport proof, delivery status, or inbound reply. The remaining public-tree risk was different: a future operator could still send an overlong or pressure-shaped message, or could discover body/attachment hash drift only at the last moment.

rev0271 therefore burns down the public-language conflict/coercion portion of the conflict blocker and turns hash parity into a runnable dry-run report:

- `examples/external-contact-conflict-coercion-review-rev0271-aiid.json`
- `schemas/external-contact-conflict-coercion-review.schema.json`
- `tools/audit_external_contact_conflict_coercion_review.py`
- `examples/external-contact-hash-recompute-dry-run-rev0271-aiid.json`
- `schemas/external-contact-hash-recompute-dry-run.schema.json`
- `tools/audit_external_contact_hash_recompute_dry_run.py`

## What changed operationally

The send-readiness gate now records three satisfied public-tree blockers: route fit, transport-capture planning, and public-language conflict/coercion review. It remains blocked because five conditions still require future human or private material:

1. human signature;
2. sender authority;
3. send-time public locator recheck;
4. private vault roots;
5. send-time body/payload hash recompute.

The new hash dry run deliberately does not satisfy the send-time recompute blocker. It proves only that the current public tree is internally coherent before the operator reaches the final send branch. If the body, `.eml`, manifest, one-page note, JSON packet, or attachment set changes, it must be rerun. It must also be rerun immediately before any actual send and bound in the human signature.

## Audit/refactor result

The refactor removes a practical drift hazard: rev0253 had strong hashes, but the operator still had to infer which current hashes should be checked together before send. rev0271 gives that bundle its own audited object. The conflict/coercion review also prevents the shortened message from becoming coercive by omission: it must preserve receive/route/decline options and reject adverse-inference, waiver, custody, intake, import, recognition, and live-floor inferences.

## Hard reliance limits

No organization was contacted. No message was sent. No transport proof, delivery status, DSN, Message-ID, response clock, inbound artifact, raw retention permission, custody, intake, import, status recognition, waiver, adverse inference, or live-floor effect exists.

A conflict/coercion review is not human legal clearance, sender authority, or send authorization. A hash dry run is not send-time recompute, transport proof, custody, intake, import, recognition, or floor evidence.
