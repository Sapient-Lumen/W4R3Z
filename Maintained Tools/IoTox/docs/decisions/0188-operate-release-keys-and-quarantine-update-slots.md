# ADR 0188: Operate release keys and quarantine historical update slots

Status: accepted owner-local construction, 2026-08-27.

## Context

ADR 0187 made retired release keys explicit in update policy v2 but did not create keys, construct a
reviewable rotation, or relieve the eight-slot hot-store ceiling. Silent automatic deletion would
discard rollback evidence, while in-place policy edits would make signer transitions difficult to
review and recover. Both operations must remain local and must not widen peer authority.

## Decision

Add `update-signer-keygen` and `update-signer-show`. Key generation requires an existing owner-
private directory, writes the fixed IoTox Ed25519 identity container with an explicit release-role
byte at mode `0600`, synchronizes it, and commits with `renameat2(RENAME_NOREPLACE)`. It prints only
the public key and refuses an existing destination. Device loading rejects release-role files,
release loading rejects device-role files, and bundle creation requires a release-role signer even
if policy pins a device key.

Add `update-policy-rotate`. It loads one strict current policy and emits a new canonical policy to
stdout without replacing the input. Each transition increments `signer-policy-epoch`; additions must
be new, retirements must be active, the two mutation sets must be unique and disjoint, revoked keys
cannot return, and one active signer must remain. Routine rotation uses an add/overlap epoch followed
by a separately reviewed retirement epoch.

Assign local-control minor 35 operation 83 to `update-gc`. Its one-byte payload is `0` for dry-run or
`1` for recoverable quarantine. The stable-device-signed confirmed revision and live candidate are
protected exactly. Every other canonical mode-`0400` slot is eligible. Quarantine mode first proves
that the bounded 256-entry owner-private recovery directory has capacity, then moves eligible slots
in canonical filename order with no-replace rename to `<slot>.q.<state-generation>`. It synchronizes
both directories after the move set. Startup validates both directories; a crash between moves is a
valid resumable partial result.

Do not add purge, automatic age/space collection, remote retention, or restoration that lowers the
confirmed release sequence.

## Consequences

- A release key can be deliberately created, inspected, overlapped, and retired without an in-place
  secret or policy overwrite.
- Compromise response can add a prepared replacement and retire a distinct compromised key in one
  reviewed epoch, while ordinary rotation can prove the replacement first.
- The eight-slot admission ceiling is operationally recoverable without deleting historical bytes.
- Confirmed and staged/applying/awaiting-health candidates cannot be collected by the retention API.
- A partial quarantine cannot redirect `current`, mutate signed lifecycle state, or make an
  unverified slot installable.
- Quarantine remains finite and can consume disk. Permanent deletion, external custody, and an
  independent rollback witness are administrator or target concerns.
- The opaque slot is still inert. Boot/service execution, health semantics, recovery media, and
  representative power-cut evidence remain the final M7 adapter gate.

## Qualification

Direct tests cover no-clobber role-separated key creation and public inspection, device/release role
confusion refusal, two-epoch rotation, last-signer
refusal, exact local-control numbering, dry-run immutability, protected-slot selection, eight-slot
recovery, Agent-local quarantine, restart after a deliberately partial move, continuation of the
remaining move set, and unsafe quarantine refusal. Full compiler, sanitizer, race, fuzz, static-
analysis, standalone, and Nix validation are retained with rev0043 evidence.
