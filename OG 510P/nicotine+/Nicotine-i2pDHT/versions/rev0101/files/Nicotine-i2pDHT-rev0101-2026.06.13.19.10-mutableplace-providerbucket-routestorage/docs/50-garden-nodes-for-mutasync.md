# Garden nodes for mutable sync

Garden nodes become even more important once mutable records become a sync control plane.

A sleeping laptop should not have to keep every head alive.  A tiny phone should not have to serve every block.  A power user with bandwidth, disk, RAM, and uptime should be able to help — without becoming owner, tracker, authority, or cloud provider.

## Useful garden services

| Service | Helps leaves | Helps the garden |
|---|---|---|
| Head watcher | Keeps mutable heads fresh and notices updates | Builds a high-quality map of active publishers |
| Roster witness | Watches writer grant epochs and rollback attempts | Learns which collections have sane governance |
| Feed relay | Serves signed feed entries | Gains excellent peer usefulness signals |
| Block cache | Caches encrypted/content-addressed blocks | Converts disk into high-impact availability |
| Snapshot mirror | Holds compact manifest roots/manifests | Makes catch-up faster and cheaper |
| Diff hinter | Answers coarse "what changed near prefix P?" questions | Amortizes expensive reconciliation work |
| Erasure-share keeper | Stores shares of encrypted content | Donates drive space without reading payloads |
| Tombstone keeper | Keeps deletion/conflict history longer | Reduces destructive resync mistakes |
| Wake rendezvous | Holds tiny envelopes for sleeping devices | Brings intermittent peers back into the graph |

## Unobvious salient benefits

### 1. Head watching creates route intelligence

A garden watching many mutable heads sees which publishers roll forward cleanly, which storage nodes keep fresh heads, and which lookup paths repeatedly return stale versions.  This is not global reputation; it is local routing wisdom.

### 2. Block caching creates demand heatmaps

Encrypted block caches leak some interest metadata, but they also give the garden a strong signal about which blocks and manifests matter.  A garden can spend disk on hot encrypted blocks and spend RAM on hot head watches.

### 3. Tombstone keeping prevents quiet corruption

Sync systems are vulnerable to old devices resurrecting deleted files or stale states.  Tombstone gardens help leaves avoid accepting very old deleted content as a fresh surprise.  The garden cannot decide truth, but it can keep signed history long enough for clients to detect weirdness.

### 4. Roster witnessing catches social mistakes

A malicious or compromised device may try to roll a writer roster backwards.  A garden cannot veto the owner key, but it can say: "I observed a newer signed roster before this older one."  That is evidence, not authority.

### 5. Diff hints reduce I2P pain

I2P latency makes naive full reconciliation expensive.  Garden diff hints can answer coarse prefix questions so peers avoid fetching entire manifests repeatedly.  These hints should be treated as accelerators, not truth.

## Garden contract shape

A garden service offer should include:

```text
service kind
capacity
TTL
metadata posture
refusal behavior
pricing/currency: none in this cube
operator note: optional
signature
```

The most important feature is graceful refusal.  A garden that says "I am full" is a better peer than one that silently drops or lies.

## Authority boundary

Garden nodes may:

- cache encrypted blocks;
- cache feed entries;
- mirror manifests;
- reannounce provider records;
- watch mutable heads;
- report stale/rollback observations;
- help new peers bootstrap.

Garden nodes may not:

- author collection changes;
- forge writer grants;
- become mandatory registrars;
- define global reputation;
- decide conflict resolution;
- silently rewrite manifests.

The garden gives.  The garden does not govern.
