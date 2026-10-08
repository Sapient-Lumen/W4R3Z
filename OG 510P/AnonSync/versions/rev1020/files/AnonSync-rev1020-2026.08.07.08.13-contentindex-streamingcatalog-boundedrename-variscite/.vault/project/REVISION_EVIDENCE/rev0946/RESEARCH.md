# Rev0946 external comparison research

Research checked on 2026-07-30 against primary/official documentation.

## Syncthing

The current Block Exchange Protocol retains remote index state and supports
`Index Update` deltas using monotonic per-item sequence numbers and an index ID.
Its synchronization documentation describes a persistent index/database model,
filesystem watcher plus periodic full scans, fixed-size SHA-256 block lists,
local block reuse before network transfer, temporary-file assembly, hash
verification, and explicit conflict copies. Its versioning documentation offers
trash-can, simple-count, staggered-retention, and external-command policies.

Implication for AnonSync: a durable monotonic metadata index, full-scan repair,
fixed-block reuse, conflict artifacts, and bounded version retention are proven
product shapes. AnonSync should adapt those ideas to its stronger rooted
filesystem and route-capability model rather than inventing a second abstract
history plane.

Primary sources:

- Syncthing, Block Exchange Protocol v1.
- Syncthing, Understanding Synchronization.
- Syncthing, File Versioning.
- Syncthing, FAQ and configuration documentation.

## Resilio Sync

Official Resilio material treats selective/full/disconnected modes,
placeholders, Owner/Read-Write/Read-Only permissions, linked-device identity,
encrypted folders for untrusted storage, and manual restore from an Archive as
ordinary product features. Archive defaults are documented as 30 days on
desktop and one day on mobile. The change log also shows that large trees,
archives, placeholders, platform metadata, upgrades, and shutdown behavior are
long-lived sources of real product defects.

Implication for AnonSync: replacing Resilio is not achieved by byte convergence
alone. The acceptance workflow must include recovery, permissions, storage
policy, setup/lifecycle, and the platform surface the user actually relies on.

Primary sources:

- Resilio Sync, Using Archive for file versioning and restoring deleted files.
- Resilio Sync, Synchronization Modes.
- Resilio Sync, User Management / Sync functionality in detail.
- Resilio Sync, Encrypted folders.
- Resilio Sync change log.

## rsync

The official rsync manual documents a size/mtime quick check and the project
documents its delta-transfer algorithm for sending differences rather than
whole files.

Implication for AnonSync: changed-file transfer should become block/delta based.
Fixed cryptographic blocks are the safer first fit with the existing range and
SHA-256 machinery; an rsync-style rolling checksum remains an optional later
optimization.

## Tor

Current Tor SOCKS extensions specify the `<torS0X>` magic and format `0` for an
application-provided stream-isolation parameter. Streams with different
isolation values do not share a circuit under the specified rules.

Implication for AnonSync: the connector's format-zero isolation token is aligned
with the current specification. Live privacy/fail-closed tests are more valuable
than replacing this mechanism without evidence.

Primary sources:

- Tor specifications, Tor's extensions to the SOCKS protocol.
- Tor proposal 351, SOCKS authentication extensions.
