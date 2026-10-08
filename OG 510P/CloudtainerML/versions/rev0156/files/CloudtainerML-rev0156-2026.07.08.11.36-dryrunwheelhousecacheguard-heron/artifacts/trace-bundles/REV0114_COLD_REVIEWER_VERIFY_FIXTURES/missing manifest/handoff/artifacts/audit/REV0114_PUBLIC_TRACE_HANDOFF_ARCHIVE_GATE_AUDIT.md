# Public trace handoff archive gate — REV0114

Status: `pass_with_blockers`  
Verdict: `handoff_archive_replay_verified_not_promotion`  
Promotion allowed: `false`

Validates a portable public-trace handoff directory/archive by checking relative subject paths, SHA-256 digests, the handoff subject-set hash, extracted self-contained verifier toolpack identity, cold-reviewer wrapper identity, and a full selector-entry receipt replay. It is an archive-portability gate, not promotion evidence.

## Manifest

- handoff manifest: `PUBLIC_TRACE_HANDOFF_MANIFEST.json`
- handoff dir: `.`
- toolpack contract: `public_trace_handoff_toolpack_v1`

## Blockers

- `named_hardware_timing_still_required_for_promotion`

## Errors

- none
