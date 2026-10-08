# Python surface — rev0019

New surfaces added in this pass:

```text
leaseroute.py       lease-backed route-gossip acceptance
storemesh.py        store-round composition across mutable/tombstone/provider records
budgetreceipt.py    signed garden budget receipts for sweep throttling/refusal
roundledger.py      repeated-round liveness/proof/witness coupling
storecontract.py    exact-digest bounded store contracts
custodyaudit.py     challenge-bound custody proof audits
storerepair.py      local repair planning after lease/audit disagreement
surfaceledger.py    active module/test/doc ledger
```

Parallel rev0019 branchlet retained and audited:

```text
storeflight.py      garden STORE admission and custody receipts
leasequorum.py      source/path/node family diversity over contact leases
storagelease.py     storage lease receipts and lease quorum
readrepair.py     replica observation and repair planning
surfaceclean.py     active pointer/surface cleanup helpers
```

The new active-surface ledger is `surfaceledger.rev0019_entries()`.
