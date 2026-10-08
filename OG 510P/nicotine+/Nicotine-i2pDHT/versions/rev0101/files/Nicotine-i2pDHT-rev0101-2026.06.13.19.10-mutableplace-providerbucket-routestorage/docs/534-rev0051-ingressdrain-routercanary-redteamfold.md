# rev0051 — ingressdrain-routercanary-redteamfold

rev0051 keeps the cube in no-network DHT design space and attacks two public-edge seams that would otherwise be treated as plumbing.

The outbound seam is `routercanary`: before a future public bridge refresh/withdraw/repair can touch a router-backed path, the local evidence must show the same profile, service, scope, request, payload, frame, SAM session, Destination, SAM endpoint, router profile digest, SAM-canary report, router-harness report, and outbox-drain report. It explicitly rejects ephemeral Destination state, accidental HTTP/SOCKS proxy exposure, quiet `notransit` regression, session/endpoint/destination drift, stale/replayed observations, same-sequence forks, previous-link mismatch, and insufficient family/path diversity.

The inbound seam is `ingressdrain`: before public bridge handler work can be considered complete, it must bind ingress-gate, service-ticket, load-sheath, continuity, caller, handler, exact request, metadata budget, refusal state, and receipt sequence. It rejects metadata-budget overrun, replay/fork/rollback, completion after useful refusal, and refusal-only laundering.


A folded branchlet also adds `sendseal` and `effectledger`: `sendseal` joins commit-barrier, outbox-drain, SAM-canary, and compact-join reports before any future public send; `effectledger` preserves prepare/send-shadow/commit/abort memory so restart or idempotent replay cannot silently rewrite public-edge state.

The audit/refactor lane is `redteamfold`, which pins the new rev0051 surfaces through source, tests, docs, public pointers, head registry, fold map, fold registry, surface ledger, and the rev0050 drainfold predecessor.

Strong sentence:

```text
A future public bridge side effect has two dangerous mouths: outbound router publication and inbound handler work; both must stay exact-scope, budgeted, and replay-resistant before live I2P noise exists.
```

Nonclaims remain: no live I2P/SAM transport, no production DHT, no production public bridge protocol, no production router manager, no production ingress/handler protocol, no private retrieval guarantee, no global reputation, no mutable-head consensus, no Sybil/anonymity guarantee, and no Nicotine+ patch.
