# Ingress drain for public bridge work

`ingressdrain.py` handles the opposite public-edge direction from `routercanary`: inbound work accepted by a public bridge must not silently become unbounded handler work.

The drain receipts bind:

```text
profile / service / scope / request
caller / handler / ingress request
ingress gate / service ticket / load sheath / continuity report
phase / metadata units / refusal reason / sequence / previous digest
family / path family
```

The first tests focus on refusal laundering and metadata pressure. Useful refusal is healthy when bounded and honest, but a refusal-only loop should not score as completed contribution. Completion after refusal is a joined-boundary error, not a harmless double record.

This surface stays no-network and no-handler. It exists so public bridge ingress cannot later be dismissed as ordinary queue plumbing.
