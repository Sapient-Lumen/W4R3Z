# Risk register — rev0038

Newly emphasized risks:

```text
branchlet drift: alternate service surfaces evolve into hidden protocols
catalog drift: one branch accepts a different catalog than another
scope drift: ingress/ticket/handoff refer to different scopes
request drift: one request spends another request's ticket
withdrawal blindness: stale service remains usable after local withdrawal
refusal laundering: refusal-only windows appear as healthy service
probe leakage: health probes reveal interest or raw keys
receipt leakage: contribution diagnostics become metadata/reputation surfaces
GC erasure: profile cleanup deletes hard negatives needed after restart
successor confusion: key-crisis catalog succession skips previous-link checks
```

rev0038 does not solve these globally. It makes them local executable pressure surfaces.
