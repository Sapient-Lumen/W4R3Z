# Store contracts and custody leases — rev0019

A signed `STORE` acknowledgement is not storage truth. `storecontract.py` makes this explicit with bounded exact-digest store contracts.

A store contract receipt says:

```text
this storage key / node accepted custody of this exact digest
for this target and purpose
inside this time window
with this family label and replica rank
```

Useful refusals are first-class. They do not count as replicas, but they do count as capacity evidence and backoff pressure.

Risk tested here:

```text
signed wrong-digest pressure
expired/stale receipt pressure
invalid receipt floods
same request with weak family diversity
useful refusals without treating refusal as storage success
```

The receipt is deliberately only the first half of the story. Ongoing custody is tested separately by `custodyaudit.py`.
