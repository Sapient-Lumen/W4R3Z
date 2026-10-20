# ADR 0202: Bind workers to independent rendezvous catalogs

Status: accepted and implemented, 2026-08-27.

## Context

ADR 0201 lets one signed auxiliary identity select a different local network context from the
primary. The first actual-Tor two-peer design review found that the derived worker transport still
inherited the primary transport's bootstrap and TCP-relay records. That is sound when a local SOCKS
forwarder can reach the same fixture as native Tox, but not when a Tor exit must reach public Tox
infrastructure while the native primary remains pinned to a private Sandwurm fixture.

Changing the primary catalog for the experiment would make every route depend on public
infrastructure and would obscure whether a Tor worker bypassed its proxy. Putting rendezvous records
in the signed route set would instead turn mutable, deployment-local reachability hints into device
identity policy.

## Decision

Add repeatable exact-key Agent options:

```text
--route-worker-bootstrap KEY=HOST:PORT:TOX_PUBLIC_KEY
--route-worker-tcp-relay KEY=HOST:PORT:TOX_PUBLIC_KEY
```

Each option requires an accompanying `--route-worker-network` for the same signed auxiliary key.
A nonempty per-worker list replaces, rather than extends, the corresponding primary template list;
an omitted list keeps compatibility inheritance. Each list is bounded to 16 records, duplicate
records fail, and the complete derived transport configuration for every savedata-bound worker is
validated before any toxcore owner starts. Strict Tor therefore still requires nonempty numeric
bootstrap and relay lists, TCP membership, a numeric SOCKS endpoint, and no UDP/native fallback.

The endpoint catalogs remain unsigned local deployment policy. The stable-device-signed route set
continues to own identity, role, connection class, budgets, generation, and expiry; private
route-binding v2 continues to authenticate that artifact without disclosing local proxy or
rendezvous placement.

## Consequences

- A native primary and native worker can remain on a deterministic private fixture while one exact
  Tor worker reaches an independently supplied public Tox relay through its own proxy.
- Worker route selection is now a complete local context: route, proxy, and optional replacement
  rendezvous catalogs are joined to one authenticated auxiliary key.
- Operator-supplied public records are reachability input, never authority, and must be refreshed
  and evidenced independently.
- This closes the construction prerequisite for the two-peer actual-Tor gate. It does not itself
  prove Tor operation, public relay availability, anonymity, or cross-route failover.
