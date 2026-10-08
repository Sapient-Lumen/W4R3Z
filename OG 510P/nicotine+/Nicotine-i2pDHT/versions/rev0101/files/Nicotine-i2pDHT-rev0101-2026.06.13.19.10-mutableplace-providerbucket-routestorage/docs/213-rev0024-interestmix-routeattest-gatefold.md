# rev0024 — relayticket / gossipsieve / clockguard

rev0024 deepens the current risk-first DHT lab in two complementary directions.

First, it preserves and surfaces the already-folded branchlet around `interestmix.py`, `routeattest.py`, `gateaudit.py`, and `gatefold.py`: confirmation leaks interest; route introductions can capture route repair; validated bytes still need a handler gate.

Second, it adds a new relay/gossip/time boundary: `clockguard.py`, `relayticket.py`, `gossipsieve.py`, and `branchletfold.py`. These modules treat time windows, garden relay admission, and signed gossip as local work-admission evidence, not truth.

The design sentence for this revision:

```text
The path that helps a node can also reveal, replay, bias, or capture the node.
```

New active surfaces:

- `interestmix.py` plans metadata-budgeted provider probe rounds with real and cover targets.
- `routeattest.py` adds fresh, signed, lease-bound route attestations with contact/attester/path-family pressure.
- `gateaudit.py` audits the seam after parseguard/validatorwall and before handler dispatch.
- `clockguard.py` guards time windows, clock skew, TTL, monotonic sequence, and same-sequence fork pressure.
- `relayticket.py` models short-lived, purpose-bound garden relay tickets for wake rendezvous, seed gates, provider probes, witness queries, and lookup relay.
- `gossipsieve.py` admits signed gossip hints only after signature, time, scope, replay, family, and kind checks.
- `branchletfold.py` audits under-surfaced branchlets so useful speculative code does not become orphaned code.

Nonclaims remain unchanged: no live I2P/SAM transport, no production DHT, no production provider privacy, no global route trust, no production dispatcher, no relay protocol, no Sybil/anonymity guarantee, and no application patch.
