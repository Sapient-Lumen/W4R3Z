# Risk register — rev0030

| Risk | rev0030 pressure test |
|---|---|
| Captured path returns fast empty answers | `negspace.py` requires responder/path diversity and rejects contradiction by positive evidence. |
| One channel becomes the new bootstrap center | `peerbook.py` checks channel-family and channel-id diversity. |
| Peerstore grows from stale contact cards | Contact leases remain short-lived and monotonic; peerbook rejects stale/forked leases. |
| Address-book repair dumps too much metadata | `peerdelta.py` uses compact range summaries and delta budgets before repair. |
| Remote sketch forks at same sequence | `peerdelta.py` quarantines same-sequence sketch forks. |
| Compromised key keeps signing convenient records | `keycrisis.py` blocks risky keyed operations under live compromise/freeze/fork notices. |
| Crisis notices become global censorship | Gate decisions are local pressure; they do not invalidate protocol truth globally. |
| Bootstrap advances from one good-looking surface | `bootstrapjoin.py` requires peerbook/live/absence/egress agreement. |
| Key recovery erases tombstones or revocations | `keycrisisjoin.py` joins crisis acceptance to checkpoint hard-negative memory. |
| Delta repair buries deletion/compromise evidence | `deltarepairjoin.py` keeps tombstone-first pressure until exact repair material arrives. |
| New surfaces become lost branchlets | `keycrisisfold.py` and `surfaceledger.py` pin navigation. |
