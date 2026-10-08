# Rev0621 signed snapshot-manifest revision binding

## What changed

Rev0621 closes the remaining rev0619 snapshot-manifest metadata seam. The restore trust profile may still carry `allowed_manifest_revisions`, but that allowlist is now applied to `payload.manifest_revision_id`, which is included in the manifest signing input. The manifest also carries `payload.parent_revision`, and the verifier requires the outer `revision_id` and `parent_revision` fields to match those signed payload fields.

This means an operator or attacker can no longer keep a valid signature, edit only the manifest's outer revision label, update a trust-profile allowlist and digest pin, and have restore accept the snapshot under the new label. That used to work because the allowlist consumed unsigned metadata.

## Validator probes

`tools/validate_rev0621_signed_manifest_revision_binding.py` verifies all carried-forward rev0620 properties and adds four restore probes:

1. Outer `revision_id` tampering is rejected with an outer/payload binding failure.
2. Signed `payload.manifest_revision_id` tampering is rejected by the signing-input digest check.
3. Outer `parent_revision` tampering is rejected with an outer/payload binding failure.
4. A trust-profile `allowed_manifest_revisions` mismatch is checked against the signed payload revision.

The generated audit is `audit/rev0621-signed-manifest-revision-binding-audit.json`.

## SQLite lifecycle refactor

The restore and snapshot paths now share explicit SQLite open/close helpers:

- failed opens close the SQLite handle best-effort before throwing;
- successful snapshot and restore destination closes are checked;
- exceptional cleanup uses `sqlite3_close_v2` best-effort to avoid losing handles when statements are still unwinding.

This is intentionally small. It reduces resource-management ambiguity without redesigning the restore protocol in the same revision as the manifest fix.

## Remaining ceiling

Rev0621 does not solve request proof-of-possession, one signed operator-root configuration, durable external effect idempotency, production key custody, or external tamper evidence. The next highest-risk change is still to replace the `x-anonsync-proof-kid == cnf.kid` label check with request-bound proof verification and a proof replay cache.
