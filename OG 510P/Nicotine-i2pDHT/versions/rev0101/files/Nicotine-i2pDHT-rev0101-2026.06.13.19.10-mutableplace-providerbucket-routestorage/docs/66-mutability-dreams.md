
# Dreams for mutable heads

Mutable records are the doorway to systems we can respect: not because the DHT stores everything, but because the DHT can publish compact, signed, changing pointers to things that are stored, mirrored, synced, witnessed, or transferred elsewhere.

## High-value mutable head families

| Dream | Mutable head points to | Why it matters | Garden help |
|---|---|---|---|
| Seed portfolios | Contact-card hashes | Entrances can survive central-server loss | Seed gates curate fresh diverse contacts |
| Policy portfolios | Policy-capsule hashes | Maintainers/gardens can update official defaults subjectively | Gardens mirror/witness policy history |
| Garden catalogs | Service offers and budgets | Leaves know what help to ask for | Gardens publish current capacity/refusal semantics |
| Mutable torrents | Current infohash | Stable name, changing release | Gardens cache heads and provider regions |
| FLOSS sync | Roster/feed/snapshot heads | Open Resilio/Syncthing-shaped control plane | Head watchers, block caches, tombstone keepers |
| Writer rosters | Delegated writer grants | Multiwriter collections need changing membership | Roster witnesses preserve epochs |
| Software updates | Release manifest hash | Auditable release channels | Mirrors and witnesses resist rollback |
| Rooms/groups | Rendezvous/invite epoch | Group discovery without central rooms | Wake couriers and invite bridges |
| Search index shards | Provider-index manifests | Search needs curation and expiration | Region gardeners and sentinel reports |
| Transparency witnesses | Signed tree/checkpoint heads | Split views and rogue keys become visible | Cross-signed receipts and monitors |
| Wake couriers | Tiny mailbox/rendezvous hints | Intermittent nodes need moving hints | Bounded storage with useful refusal |
| Capability revocation | Grant/revoke epochs | Delegation needs withdrawal | Tombstone keepers preserve revocations |

## Mutability rule of thumb

The DHT should store **small signed heads** and **provider records**. Bulk data, blocks, full indexes, and long logs should live outside the DHT and be found through it.

## Product posture

The sweetest future is not one app. It is a family:

- a mutable-torrent publisher;
- a FLOSS sync layer;
- a garden dashboard;
- a bridge/gateway for older clients;
- a friend/community seed network;
- a transparent update and policy system;
- and eventually application-specific directories that users can fork.


## Size-budget rule

If the manifest is too large for the mutable value budget, the head stores a compact manifest digest and summary instead of inlining every entry.  This keeps the DHT head small while letting gardens/providers serve the larger signed manifest elsewhere.
