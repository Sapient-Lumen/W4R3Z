# Netgraph + netmap/VALE as derived network fabrics (underused FreeBSD superpowers)

**Tier:** C (Optional lane)  
**Profiles:** A, C, D  
**Pillars:** isolation, operability
**Patterns:** Plan→Apply→Receipt, Observation→Suggestion→Review→Enforce  

FreeBSD has two unusually composable networking substrates that are *powerful*, *introspectable*, and relatively underused in “normal” OS designs:

- **netgraph(4)**: a kernel graph framework where networking functions are **nodes** connected by **hooks**.
- **netmap(4)** (optional): a framework for very fast packet I/O; its **VALE** feature provides an in-kernel virtual switch.

DeriveBSD does **not** need either by default.
But as a greenfield, microVM-heavy OS, it’s worth baking in a clean place for them early, because they map extremely well onto DeriveBSD’s model:

- *graphs as contracts*
- *plans compile to concrete mutations*
- *mutations are receipted*
- *runtime wiring is explainable and diffable*


## 1) The netgraph shape (why it fits DeriveBSD)

netgraph is fundamentally a **wiring language** for packet paths.
It lets you build a topology out of small blocks (bridge, nat, tee, one2many, ether, sockets, etc.) and then inspect the graph.

That is exactly what DeriveBSD wants for host networking:

- a **typed intent** (`net.topology.plan`)
- an **apply receipt** (`net.topology.receipt`)
- a stable **observed-state digest** (graph snapshot → hash)
- drift detection and commit-confirm semantics

Key operational upside: a netgraph topology is naturally representable as a *graph snapshot* (e.g. `ngctl dot`), which is a great “human explainability” artifact to attach to receipts.

References:
- netgraph(4): https://man.freebsd.org/cgi/man.cgi?query=netgraph&sektion=4
- FreeBSD Handbook note (netgraph for traffic between host/jails): https://docs.freebsd.org/en/books/handbook/book/
- FreeBSD Foundation (accessible overview + examples): https://freebsdfoundation.org/our-work/journal/browser-based-edition/networking-3/netgraph-for-the-rest-of-us


## 2) Practical node sets to standardize (v0)

To keep the surface small, DeriveBSD should treat netgraph as an **optional backend** with a **curated node allowlist**.
Start with the boring, high-leverage pieces:

- **ng_bridge(4)** for L2 switching
- **ng_nat(4)** for NAT (libalias-backed)
- **ng_ether(4)** for attaching to real interfaces
- **ng_eiface(4)** for virtual Ethernet interfaces (jails/workloads)
- **ng_socket(4)** only for brokered, policy-scoped tooling (no ambient debug sockets)

References:
- ng_bridge(4): https://man.freebsd.org/cgi/man.cgi?query=ng_bridge&sektion=4
- ng_nat(4): https://man.freebsd.org/cgi/man.cgi?query=ng_nat&sektion=4


## 3) How it plugs into `net.topology.plan`

DeriveBSD already treats the host substrate as a derived operation (`docs/322-network-topology-and-firewall-as-derived-operations.md`).
Add a *backend selector* and a *fabric stanza*:

- default backend: **if_bridge + pf** (stable and familiar)
- optional backend: **netgraph fabric**

A netgraph fabric stanza should be expressed as:

- `nodes[]` (type + name + parameters)
- `links[]` (node:hook ↔ node:hook)
- `exports[]` (which edges become named interfaces exposed to jails/microVMs)

The compiler produces:

- module loads (explicit, policy-gated)
- `ngctl` actions (create, name, connect)
- interface attachment actions (e.g. expose `ng_eiface` endpoints)

**Receipt requirements:**

- a digest of the **graph snapshot** (dot output)
- a list of node types used
- a list of exported interface names
- a link to pf anchor digests (pf remains the policy boundary)


## 4) netmap/VALE as an optional fast path

netmap(4) is primarily a performance tool: it’s used for high-rate packet capture/forwarding and can reduce per-packet overhead.
Its VALE feature implements a fast in-kernel virtual switch.

DeriveBSD should treat netmap/VALE as:

- **default off**
- an **explicit topology backend** (or an acceleration mode for specific links)
- a **reviewable drift surface** (enabling it changes the networking attack surface)

References:
- netmap(4): https://man.freebsd.org/cgi/man.cgi?query=netmap&sektion=4
- VALE man page (FreeBSD flavor): https://manpages.ubuntu.com/manpages/jammy/man4/vale.4freebsd.html

This is also where the packet-authority boundary must stay crisp:
netmap/VALE is **not** a casual compatibility convenience or packet-capture loophole.
It belongs to the stronger explicit lane fixed in `docs/506-packet-capture-raw-sockets-and-fast-packet-io-boundary.md`, where fast packet I/O stays default-off and reviewable as a deliberate dataplane/acceleration choice.

## 5) Safety posture (don’t turn “cool graphs” into ambient authority)

netgraph and netmap are kernel extensions.
In DeriveBSD terms:

- enabling additional node types expands **UAPI/attack surface**
- it must be visible in **closure diffs** and **drift bundles**
- it should require a policy decision record when expanding the allowlist

Rule of thumb:

- **pf** remains the access-control enforcement plane
- netgraph/netmap are treated as *implementation backends* for the datapath, and remain **policy-governed + receipted**


## 6) Why bake this in early

Even if most users stick to if_bridge/pf, a netgraph/netmap lane gives DeriveBSD:

- an explicit place to put “high-performance/complex networking” without ad-hoc scripts
- a graph-shaped explainability artifact that pairs well with the evidence spine
- an adoption story for advanced deployments (routers, multi-tenant labs, microVM clusters)

Last updated: 2026-03-08r235
