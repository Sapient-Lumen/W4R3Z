# rev0019 — storeflight-leasequorum-surfaceclean

rev0019 keeps the cube in consumer-agnostic DHT design space and works the risky pieces first. The new design pressure is that storing a record is not just a `STORE` RPC, not just a valid signature, and not just a fast acknowledgement. A caller should not claim local durability until exact-digest storage receipts, family diversity, fresh entrance leases, tombstone collision checks, and later custody challenges are considered as separate typed evidence.

The revision now has a combined active surface:

- `storeflight.py` joins garden admission, eviction, control-plane reserve pressure, custody receipts, useful refusals, and tombstone collision checks.
- `leasequorum.py` asks whether fresh contact leases arrived through diverse enough entrance channels and lease families.
- `leaseroute.py` requires route-gossip repairs to be backed by fresh route-capable contact leases.
- `storemesh.py` joins sibling-store acknowledgements across mutable heads, tombstones, providers, and refusal pressure.
- `budgetreceipt.py` gives garden nodes signed service-window and sweep-audit receipts for useful refusal/throttling.
- `roundledger.py` preserves repeated-round liveness/provider/witness evidence so one green surface cannot silence another red one.
- `storecontract.py`, `custodyaudit.py`, and `storerepair.py` add the deeper custody lane: exact-digest store contracts, challenge-bound custody proofs, and bounded repair decisions.
- `surfaceclean.py` and `surfaceledger.py` keep the active cube navigable while preserving historical wake-from-amnesia context.

The strongest rev0019 rule:

```text
store acceptance is not custody proof; custody proof is not permanent truth; repair is local policy, not consensus.
```

The nonclaim remains strict: this is still no-network Python pressure work. There is no live SAM transport, no production DHT, no production STORE protocol, no production lease quorum, no global consensus, and no anonymity or Sybil guarantee.

Additional rev0019 addendum surfaces now pin the storage-life side of the STORE seam: `storagelease.py` tests live storage lease receipts and renewal/fork/tombstone pressure; `readrepair.py` tests exact/missing/stale/wrong/tombstoned replica observations before repair. These are deliberately separate from `leasequorum.py`, which remains about entrance/contact-lease source capture.

