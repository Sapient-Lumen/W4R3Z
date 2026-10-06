# VNET jails as first‑class network compartments

FreeBSD’s **VNET jails** provide a *separate network stack* per jail (interfaces, addresses, routing table, ARP/NDP caches), which is a sharp tool for reducing ambient authority in network‑exposed subsystems.

DeriveBSD already treats networking as **policy‑composed** (`pf` anchors, FIB routing isolation, deny‑by‑default egress) and increasingly **capability‑mediated** (see `201-network-egress-as-capability.md`). VNET adds a complementary boundary: *don’t just filter traffic—give the compartment its own stack reality.*

## Why this matters for DeriveBSD

### 1) Compartment boundaries become simpler and more provable

For `fetch-domain`, `publish-domain`, `net-domain`, and other “privileged-but-networked” roles, VNET makes it possible to:

* attach only the interfaces the compartment should have (often an `epair(4)` endpoint)
* keep its routes and neighbor caches isolated from the host and other domains
* run per-domain firewalling and traffic accounting without relying solely on a shared host stack

### 2) Cleaner “network is denied” enforcement

DeriveBSD’s non‑negotiable stance is that builds should be offline by default.

With VNET:

* an offline compartment simply never receives an interface
* “restricted fetch” compartments can be given a single egress path via a dedicated bridge/gateway
* routing isolation is structural (separate stack) rather than only rule-based

### 3) A natural building block for Qubes‑y control planes

If we later move control-plane subsystems into microVMs, VNET is still valuable because it keeps *host-side* networking objects modular:

* `epair(4)` is the jail-side “virtual cable”
* `bridge(4)` (or a dedicated forwarding jail) is the host-side “virtual switch”
* `pf` anchors remain the policy layer

## DeriveBSD design hooks

### New evidence objects

Add to Plan/runtime evidence:

* `netcompartment.intent` — declared role (`fetch-domain`, `publish-domain`, `workload`, `devshell`…)
* `netcompartment.realization` — how it was instantiated (VNET jail vs shared-stack jail vs microVM)
* `netcompartment.topology` — interfaces, bridges, routes, FIB, pf anchor set

These objects make “why did this domain have network?” auditable.

### Profile templates

Provide standard profiles:

* `net.none` — no interface, no routes
* `net.fetch` — single egress interface, DNS allowed only to resolver, HTTP(S) only to fetch proxy
* `net.publish` — egress only to cache endpoints + transparency log(s), no inbound
* `net.workload` — explicit allowlists; default inbound denied

The *profile digest* must bind into the Plan identity chain.

## Implementation notes (v0‑friendly)

* Use `jail.conf` with `vnet = new`.
* Connect VNET jails to the host with `epair(4)` and a dedicated `bridge(4)`.
* Keep `pf` composition on the host (anchors) to start; optionally add per‑VNET `pf` later.

## References

* FreeBSD Handbook: VNET jails overview.
* `epair(4)` manual page.
* “Jail vnet by Examples” (FreeBSD Foundation PDF).
