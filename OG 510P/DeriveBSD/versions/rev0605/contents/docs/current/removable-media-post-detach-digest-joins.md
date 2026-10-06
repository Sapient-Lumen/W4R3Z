# Current removable-media post-detach digest joins

r521 separates historical placeholder fixture digests from computed joins.

## Canonical computation

The state-machine manifest uses `json-canonical-sha256-sort-keys-no-whitespace`: JSON is serialized with sorted keys and compact separators, then SHA-256 is computed over the UTF-8 bytes.

## Rule

New r521 joins in `spec/examples/removable.media.local.post_detach.state_machine.manifest.json` must match the actual canonical digest of each listed positive example. Existing older `sha256:1919...`, `sha256:2a2a...`, and similar fields remain legacy fixture fields unless a checker explicitly computes and binds them.

## Why this matters

A broker receipt with a new receipt id, timestamp, sequence, and digest should validate against the production schema. A golden example should still remain exact. r521 therefore adds a fixture schema for the exact r520 example while making the production r520 schema accept runtime-shaped values.


r529 adds `removable.media.local.post_detach.export.bundle.deletion.receipt` so export cleanup is a terminal, CAS-ledgered transition rather than a flag on access.

Last updated: 2026-05-30r521
