
# rev0008 — open questions around mutability

This revision answers the user's question by refusing to close the questions too early.  The DHT should be born with mutable heads, but the hard part is not the `put` RPC.  The hard part is deciding what mutable truth means when the substrate is anonymous, slow, adversarial, and filled with generous but non-authoritative garden nodes.

## The questions that remain live

1. **Identity binding.** Node routing identity wants to be bound to an I2P Destination and DHT key so arbitrary node-id selection is expensive. Mutable application identity wants portability, delegation, and key rotation. The current guess is: route with Destination-bound node identity; write application heads with delegated writer keys.

2. **Canonical format.** BEP44-style bencode is useful for small mutable heads and mutable torrent compatibility. Richer systems may want CBOR-like codecs, typed manifests, or application-specific encodings. The invariant is deterministic signature bytes.

3. **Rollback memory.** A valid older signature can still be an attack. Clients need local highest-seen sequence memory, but the DHT should not pretend to have global consensus. Garden witness receipts should be evidence, not authority.

4. **Same-sequence forks.** If a publisher signs two different values with the same sequence, stores can reject locally but the network can still split. Preserve fork evidence; do not silently pick a side.

5. **Seed authority shape.** One official mutable seed head recreates central entrance dependence. The preferred shape is a portfolio: maintainer defaults, community gardens, user-imported friends, cached last-good, and direct invites.

6. **Metadata mode ladder.** Some power users will choose connectivity over privacy. That can be honorable only when the role is explicit: garden, bridge, search helper, sync mirror, block cache, wake courier.

7. **Provider sweep budget.** Mutable heads and provider records need refresh discipline. Region sweep beats naive per-key reproviding, especially over I2P latency.

8. **Capability revocation.** Future sync and garden delegation need capabilities, but revocation is inherently stale in offline networks. Short-lived grants plus mutable revocation/tombstone heads are the current guess.

9. **Garden non-authority.** Gardens should serve more than leaves, but should not become truth. Outputs are receipts, hints, caches, witness reports, and service offers.

## One sentence

Mutability is where sovereignty and abuse meet; the DHT should give users stable changing names without quietly creating a new center.
