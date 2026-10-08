# Public trace handoff archive gate — REV0113

Status: `fail`  
Verdict: `handoff_archive_blocked_manifest_or_replay_mismatch`  
Promotion allowed: `false`

Validates a portable public-trace handoff directory/archive by checking relative subject paths, SHA-256 digests, the handoff subject-set hash, extracted self-contained verifier toolpack identity, and a full selector-entry receipt replay. It is an archive-portability gate, not promotion evidence.

## Manifest

- handoff manifest: `PUBLIC_TRACE_HANDOFF_MANIFEST.json`
- handoff dir: `.`
- toolpack contract: `public_trace_handoff_toolpack_v1`

## Blockers

- `replay_skipped_due_to_manifest_or_digest_errors`

## Errors

- `handoff subject digest mismatch: public_trace_selector_receipt_replay_gate`
- `handoff_subject_set_sha256 does not match actual extracted files/tools`
- `toolpack_subject_set_sha256 does not match actual extracted tool files`
- `handoff tool subject public_trace_selector_receipt_replay_gate hash does not match extracted handoff toolpack file`
- `strict handoff archive gate requested but verified handoff is absent`
