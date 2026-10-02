# ADR 0292: Add durable human peer aliases

- Status: accepted and implemented
- Date: 2026-09-01

## Context

IoTox's established-peer commands accept process-local friend numbers or 64-hex Tox public keys.
Numbers are unstable and keys are not names a human should memorize. Adding a loose client-side map
would create inconsistent behavior across sync, command, journals, and Ratox; implicit case folding,
prefixes, or alias replacement could retarget a high-authority operation.

## Decision

Add one stable-device-signed, owner-private `peer-alias-store-v1`, bounded to 256 one-to-one mappings
from canonical 1..63-byte lowercase ASCII names to exact 32-byte Tox public keys. Mutations are
generation-bound and crash-atomic. `peer-alias-set` requires the key to be a current friend and is
idempotent only for the exact same pair. Name/key collisions refuse. Rename is an explicit atomic
operation; removal is explicit and retry-idempotent.

Freeze the selector grammar as explicit `friend:`, `key:`, or `alias:` followed by compatibility bare
uint32, 64-hex, or canonical alias forms. Alias grammar prevents lexical collision. Main-CLI peer
resolution and terminal open/resume/list/close use the same parser and Agent resolution operation.
Literal friend-request/add inputs remain keys because no new alias exists before friendship.

Transport peer removal retains the alias. This prevents silent name takeover; a retained alias can
address historical key records but live operations fail until the exact key is again a friend.
Rebinding is two explicit remove/set mutations.

Advance local control to v1.50 operations 109--113 for list, set, rename, remove, and resolve. Alias
resolution returns only the exact key. These same-user operations do not mutate the authority ledger,
do not add friendship, and do not change peer/Ratox/sync framing.

## Consequences

An ordinary command can use `workstation` without weakening public-key binding. Alias names remain
private metadata and are excluded from content-free diagnostics. The signed store has no independent
rollback witness. It binds Tox transport identity, not the separately proven stable IoTox device
principal. ADR 0293 later supplies the separate signed invitation ceremony; endpoint migration
remains future and may not silently reuse alias semantics.

Two owned tests freeze selector/codec ambiguity, store signing, one-to-one collision, rename/remove,
restart, permissions, and tamper refusal. The one-binary lifecycle uses an alias for real action and
typing operations, preserves it across Agent restart and peer removal, and releases it only through
the explicit idempotent command.
