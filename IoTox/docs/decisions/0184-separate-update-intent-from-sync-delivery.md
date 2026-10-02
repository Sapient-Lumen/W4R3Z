# ADR 0184: Separate signed update intent from sync delivery

Status: accepted construction direction, 2026-08-26.

## Context

M5B can transport, verify, retain, and explicitly activate immutable files and trees. Gate 4 can
place those immutable objects across authenticated Tox routes. Treating either sync acceptance or
ordinary sync activation as permission to install code would collapse content integrity, publisher
identity, operator authority, release policy, and target effect into one unsafe decision.

IoTox already reserves `signed-ota-v1`, message type `ota-manifest`, and the authority-ledger
`install.firmware` capability. None is advertised or dispatched. The first M7 construction slice
needs an artifact contract before it needs another remote command.

## Decision

Freeze `signed-update-bundle-v1` as specified in
`protocol-signed-update-bundle-v1.md`. One canonical, fixed-size Ed25519 manifest precedes an opaque
payload and binds its SHA-256, size, sync namespace, target, release sequence, version, kind, and
release signer. The signer must be pinned by owner-local policy; bundle claims cannot nominate their
own trust root or install path.

Keep the bundle inert throughout delivery and verification. The first slot adapter copies bytes only
to an owner-private inactive regular file. Staging, pending selection, later-incarnation health
confirmation, automatic rollback, and confirmed anti-rollback state form a separate device-signed
state machine. Ordinary sync activation remains unchanged.

Do not advertise feature bit 20 merely because local bundle verification exists. That bit remains
reserved until a remote manifest/request exchange has a complete `install.firmware` authority gate,
bounded replay semantics, and genuine-provider qualification.

## Consequences

- A compromised or merely authorized sync writer cannot install arbitrary received content unless
  it also holds a locally pinned release key and passes the update lifecycle.
- A release signer can authorize payload intent but cannot mutate device ownership or transport
  friendship.
- Multi-route scheduling can carry update bundles without becoming part of update authority.
- Failed unconfirmed candidates roll back without lowering the confirmed release high-water mark.
- Software-only signed state detects alteration and isolated rollback, but not coordinated replay of
  every complete valid local record. Hardware monotonic witnesses remain target-specific.
- M7 can be qualified first with an opaque slot and Agent restart; claiming a bootable OTA target
  still requires a named adapter, representative hardware, power cuts, and recovery evidence.
