# Conflict, capability, and threat guesses

This file keeps speculative sync dangers visible before the DHT design accidentally makes them worse.

## Conflict posture

Default guess:

> Preserve conflicts. Do not silently resolve them inside the DHT.

The DHT can store or find signed heads.  It should not decide whether Alice's edit beats Bob's edit.  Future applications can choose:

- Syncthing-like version vectors and conflict files;
- Willow-like namespace/subspace/path/timestamp semantics;
- CRDT maps/sets for app data;
- append-only event logs for audit-heavy data;
- single-writer mutable heads for torrent/update-feed data.

The substrate should allow all of these.

## Capability posture

There should be separate capabilities for:

```text
read/decrypt
write/sign
provide/cache
steward/watch
invite/bootstrap
```

Readers should be able to provide encrypted blocks without being able to write.  Garden stewards should be able to watch heads without decrypting payloads.  Providers should be able to donate storage without learning file paths when the application chooses a private metadata mode.

## Multiwriter posture

Avoid shared write keys for normal folders.  Shared write keys are simple but dangerous: every writer is indistinguishable and revocation becomes painful.

Use:

```text
owner/root key -> roster -> writer keys -> per-writer feeds
```

Then revocation means advancing the roster epoch and rejecting future entries from that writer.  Old entries still exist; the application decides how to treat them.

## Metadata posture ladder

The sync layer should support multiple modes:

| Mode | DHT metadata | Use case |
|---|---|---|
| Head-only | collection ids and head targets | low metadata fallback |
| Provider-light | provider records for encrypted blocks | availability-first private groups |
| Manifest-cache | encrypted manifests mirrored by gardens | fast catch-up |
| Public-index | readable names/categories/provider hints | public archives |
| Lab-full | rich indexes and diff hints | explicit experimental mode |

The user already said connectivity may matter more than metadata in some cases.  The cube should preserve that knob rather than pretend one privacy posture fits all.

## Threat guesses

1. **Rollback gardens:** A garden serves stale but valid heads.  Defense: sequence monotonicity, quorum reads, local witness memory.
2. **False providers:** A provider claims blocks it cannot serve.  Defense: semantic penalties, proof-of-possession probes, short TTLs.
3. **Roster fork:** A compromised owner key or app bug publishes divergent rosters.  Defense: explicit epochs, witness reports, conflict UX.
4. **Share enumeration:** Public provider records reveal popular collection ids.  Defense: private modes, blinded keys, opt-in public-index mode.
5. **Tombstone suppression:** Attackers hide deletions to resurrect old files.  Defense: tombstone keeper gardens, signed deletion entries, long retention knobs.
6. **I2P-latency exhaustion:** Reconciliation does too many round trips.  Defense: snapshot manifests, diff hints, region sweep, garden caching.

## Good first test surfaces

- Mutable head stale rejection.
- Per-writer feed chain verification.
- Roster signature validation.
- Snapshot root changes under file updates.
- Conflict preservation instead of overwrite.
- Garden plan from resource budgets.

rev0006 adds these as toy tests in `tests/test_mutasync.py`.
