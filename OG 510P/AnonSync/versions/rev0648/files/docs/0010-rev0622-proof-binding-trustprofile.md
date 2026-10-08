# Rev0622 proof binding and pinned trust-profile read

## What changed

Rev0622 replaces the local proof-key label check as the only runtime proof condition. Positive HTTP and AsyncAPI fixtures now carry `x-anonsync-proof-binding-sha256`, and the normalizer recomputes that value after selecting the operation contract and verifying JWT-derived identity claims.

The digest is an HMAC-SHA256 over a deliberately narrow local fixture material:

- envelope kind;
- proof key id;
- tenant;
- selected contract file;
- operation id;
- verified `contract_digest_sha256`;
- bearer-token SHA-256;
- HTTP method, path, and canonical body digest; or
- AsyncAPI channel, action, CloudEvents source/id, and canonical payload digest.

A copied proof key id is no longer enough for a positive case. Missing, noncanonical, stale, or mismatched proof-binding digests fail before ledger staging.

## Validator probes

`tools/validate_rev0622_proof_binding_trustprofile.py` verifies all carried-forward rev0621, rev0620, and rev0619 properties and adds proof-binding probes:

1. A positive HTTP fixture with the binding header removed is rejected.
2. A positive HTTP fixture with an all-zero binding digest is rejected.
3. A positive HTTP fixture with a body mutation but stale binding is rejected.
4. A positive AsyncAPI fixture with a payload mutation but stale binding is rejected.
5. The validator also independently recomputes proof bindings for all 378 routable authorized stream fixtures.

The generated audit is `audit/rev0622-proof-binding-audit.json`.

## Restore trust-profile refactor

The runner restore path now calls `read_trust_profile_with_digest_pin`, which reads the configured trust profile once, verifies the caller-supplied SHA-256 pin against those exact bytes, and passes the pinned text to `verify_sqlite_snapshot_manifest_with_trust_profile_text`.

This is a scoped lifecycle/security refactor. It removes the previous runner pattern of hashing a trust-profile path and then making a second parse-time read from the same path. It does not yet provide descriptor-relative open semantics, stable inode checks, streamed snapshot digests, or complete race-free filesystem verification.

The generated restore/capability audit remains `audit/rev0622-cpp-restore-and-capability-audit.json`.

## Remaining ceiling

The HMAC proof binding is local fixture evidence, not production proof-of-possession. The secret is stored in the controls fixture and must not be treated as deployable key custody. The next proof step is a true sender-constrained design: DPoP-style signed proofs or mTLS-bound tokens, proof replay rejection, proof key separation, and operator-owned identity policy.
