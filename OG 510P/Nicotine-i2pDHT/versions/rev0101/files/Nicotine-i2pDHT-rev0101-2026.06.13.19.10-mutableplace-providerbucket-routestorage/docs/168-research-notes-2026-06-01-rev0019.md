# Research notes — 2026-06-01 — rev0019

rev0019 continues the risk-first strategy without live transport. The design keeps treating provider records, mutable heads, tombstones, witnesses, contact leases, and STORE acknowledgements as typed evidence surfaces that a local policy joins deliberately.

The new emphasis is the first dangerous STORE seam. Earlier revisions tested lookup pressure, provider proof pressure, garden refusal, tombstone cache, contact leases, sibling-cast planning, and keyspace cartography. This revision asks how those pieces behave when local code wants to say “stored enough.”

The strongest guesses retained:

```text
exact digest beats vague availability
useful refusal is capacity evidence, not success
fresh leases beat immortal cached contacts
same-sequence forks are quarantine evidence
tombstones block resurrection pressure locally
channel diversity matters before entrance trust
active metadata should be audited, not trusted by habit
```

No new external dependency was added. The live SAM/I2P boundary remains intentionally shadowed.

The late rev0019 addendum splits the storage seam further. Garden admission/custody, storage lease freshness, and read-repair are different judgments. This follows the old Kademlia STORE/republish instinct but refuses to treat a signed ack as enough evidence on an anonymous/high-latency substrate. Tahoe-style lease thinking also remains useful: storage persistence needs renewal/accounting rather than immortal assumptions.

