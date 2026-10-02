# ADR 0293: Add explicit signed peer invitations

- Status: accepted and implemented
- Date: 2026-09-02

## Context

ADR 0292 made established peers usable by human name, but initial introduction still required copying
a raw Tox address with no stable-IoTox-identity binding. Treating a signed introduction as an
authority grant would collapse the project's central friendship/authority boundary. Persisting an
unreviewed inbox or silently accepting a suggested alias/capability would add ambient state and replay
effects.

## Decision

Freeze one exact 320-byte `IOTXINV1` artifact. The stable device identity signs its exact live Tox
address, issue and expiry times, 32-byte random nonce, optional canonical alias, and a bitset limited
to the authority-v3 capability vocabulary. Lifetimes are 60 seconds through 30 days. Signature and
artifact identifiers use separate `peer-invitation-v1` and `peer-invitation-record-v1` domains.

Add live `peer-invitation-create`, offline `peer-invitation-inspect`, dry pinned
`peer-invitation-import`, and explicit `peer-invitation-accept`. Create verifies before a private
no-clobber write. Inspect labels an unpinned self-signature as unestablished trust. Import requires
the expected inviter and valid time but mutates nothing. Accept repeats those checks, sends an
ordinary Tox request to the signed address, and optionally uses the existing collision-refusing alias
operation. Exact retry is idempotent while valid.

Advance local control to v1.51 operation 114 only for Agent-side artifact creation. Inspect/import
remain file-local; acceptance deliberately composes the already frozen peer-list, friend-request, and
alias-set operations. No peer wire or Ratox framing changes.

## Consequences

An operator can move one reviewable introduction artifact instead of separately trusting a loose
address and name. The recipient still must pin the inviter through an independent channel. Requested
capabilities remain intent only; acceptance creates no ledger record, Ratox profile binding, or sync
policy and always reports `authority-granted=0`.

The ceremony has no persistent inbox and no independent clock/rollback witness. Exact replay cannot
retarget the signed key and same-pair friendship/alias effects are idempotent, but a rolled-back clock
can extend transport-level acceptance. This is acceptable only because friendship grants no IoTox
authority. Stronger rollback resistance remains workstream 8.

Two owned tests freeze codecs, bounds, canonical shape, domains, signature, pin, expiry, skew, and
tamper refusal. The one-binary lifecycle creates and independently inspects/imports an artifact, tests
wrong-pin and no-clobber refusal, then uses a distinct Agent identity to create friendship and the
suggested alias twice while proving the second acceptance is unchanged and authority stays empty.
