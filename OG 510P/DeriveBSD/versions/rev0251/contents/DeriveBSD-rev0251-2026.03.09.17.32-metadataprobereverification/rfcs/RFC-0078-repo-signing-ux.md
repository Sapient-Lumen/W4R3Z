# RFC-0078: Repo signing UX lessons (pkg-inspired ergonomics)

- Status: draft
- Author(s):
- Created: 2026-02-23
- Last updated: 2026-02-23

## Summary

Improve the operational ergonomics of signing/trust bootstrapping by learning from FreeBSD pkg repository signing modes.

## Motivation

Strong crypto is pointless if operators avoid it.
FreeBSD pkg’s design is useful because it makes signature mode and trust bootstrap explicit.

## Goals / Non-goals

Goals:
- make signature policy easy to express as data
- support fingerprint-based trust bootstrapping
- keep channel metadata rollback/freeze protections

Non-goals:
- copying pkg formats wholesale

## Proposal

- Extend `trust.policy` to include a `repositories[]` section (as an extension):
  - repo id
  - signature mode (e.g., fingerprints, pubkey)
  - trust roots / fingerprints
  - required attestations

- `derive channel add` installs a repo stanza and pins trust roots.

## Alternatives considered

- “just configure sigstore” everywhere (not always practical)

## Backwards compatibility

Additive; existing trust policy remains valid.

## Security considerations

- protect against rollback/freeze via channel metadata policy

## Open questions

- do we want first-class support for offline signing devices/HSMs
